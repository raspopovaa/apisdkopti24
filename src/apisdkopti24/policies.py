"""Политики повторов, частоты и одновременности запросов клиента."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .errors import SDKConfigurationError

SAFE_HTTP_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
IDEMPOTENT_HTTP_METHODS = SAFE_HTTP_METHODS | {"PUT", "DELETE"}


class RetryClass(StrEnum):
    """Класс повтора операции из каталога операций.

    * ``NEVER`` — не повторять никогда (изменения без идемпотентности).
    * ``SAFE`` — повторять, если операция идемпотентна.
    * ``NETWORK_ONLY`` — повторять только при сбое сети, когда запрос не дошёл до
      сервера (вход ``authUser``).
    """

    NEVER = "never"
    SAFE = "safe"
    NETWORK_ONLY = "network_only"

    @classmethod
    def normalize(cls, value: str | RetryClass) -> RetryClass:
        """Привести строку из каталога к ``RetryClass``.

        :param value: ``RetryClass`` или его строковое значение.
        :return: Значение перечисления.
        :raises ValueError: Неизвестный класс повтора.
        """
        if isinstance(value, cls):
            return value
        return cls(value)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Число попыток и паузы автоматических повторов.

    :ivar network_attempts: Попыток при сетевых ошибках.
    :ivar rate_limit_attempts: Попыток после ответа 429/509.
    :ivar max_total_attempts: Предел HTTP-попыток одной операции.
    :ivar network_backoff_min_seconds: Первая пауза после сетевой ошибки.
    :ivar network_backoff_max_seconds: Предел удваивающейся паузы.
    :ivar rate_limit_backoff_seconds: Шаг паузы после 429/509.
    :ivar auth_retry_min_interval_seconds: Минимальная пауза между входами (защита от бана WAF).
    :raises SDKConfigurationError: Попыток меньше 1 или пауза отрицательная или не число.
    """

    network_attempts: int = 5
    rate_limit_attempts: int = 3
    max_total_attempts: int = 5
    network_backoff_min_seconds: float = 2.0
    network_backoff_max_seconds: float = 60.0
    rate_limit_backoff_seconds: float = 0.5
    auth_retry_min_interval_seconds: float = 5.0

    def __post_init__(self) -> None:
        if (
            min(
                self.network_attempts,
                self.rate_limit_attempts,
                self.max_total_attempts,
            )
            < 1
        ):
            raise SDKConfigurationError("Число попыток должно быть не меньше 1")
        delays = (
            self.network_backoff_min_seconds,
            self.network_backoff_max_seconds,
            self.rate_limit_backoff_seconds,
            self.auth_retry_min_interval_seconds,
        )
        # NaN проходит любые сравнения, а бесконечная задержка не умещается в срок операции.
        if not all(math.isfinite(delay) and delay >= 0 for delay in delays):
            raise SDKConfigurationError(
                "Задержки перед повторами должны быть конечными неотрицательными числами"
            )

    def network_attempt_count(
        self,
        retry_class: str | RetryClass,
        http_method: str,
        *,
        idempotent: bool | None = None,
    ) -> int:
        """Сколько попыток дать операции при сетевых ошибках.

        Вход (``NETWORK_ONLY``) и идемпотентная ``SAFE``-операция получают
        ``min(network_attempts, max_total_attempts)``, остальные — одну попытку.

        :param retry_class: Класс повтора операции.
        :param http_method: HTTP-метод; определяет идемпотентность, если она не задана.
        :param idempotent: Явная идемпотентность из каталога.
        :return: Число попыток, не меньше 1.
        """
        normalized = RetryClass.normalize(retry_class)
        resolved_idempotent = (
            http_method.upper() in IDEMPOTENT_HTTP_METHODS if idempotent is None else idempotent
        )
        if normalized is RetryClass.NETWORK_ONLY:
            return min(self.network_attempts, self.max_total_attempts)
        if normalized is RetryClass.SAFE and resolved_idempotent:
            return min(self.network_attempts, self.max_total_attempts)
        return 1

    def rate_limit_attempt_count(
        self,
        retry_class: str | RetryClass,
        http_method: str,
        *,
        idempotent: bool | None = None,
        billable: bool = False,
    ) -> int:
        """Сколько попыток дать операции после ответа 429/509.

        Повторяются только идемпотентные ``SAFE``-операции без тарификации: тарифицируется
        ли ответ 429/509, не описано, а повтор платного чтения мог бы стоить ещё одного
        запроса из пакета.

        :param retry_class: Класс повтора операции.
        :param http_method: HTTP-метод; определяет идемпотентность, если она не задана.
        :param idempotent: Явная идемпотентность из каталога.
        :param billable: Запрос тарифицируется.
        :return: Число попыток, не меньше 1.
        """
        normalized = RetryClass.normalize(retry_class)
        resolved_idempotent = (
            http_method.upper() in IDEMPOTENT_HTTP_METHODS if idempotent is None else idempotent
        )
        # Тарифицируется ли ответ 429/509, не описано: платное чтение после него не
        # повторяется, чтобы повтор не стоил ещё одного запроса.
        if normalized is RetryClass.SAFE and resolved_idempotent and not billable:
            return min(self.rate_limit_attempts, self.max_total_attempts)
        return 1

    def initial_network_backoff(self, retry_class: str | RetryClass) -> float:
        """Первая пауза перед сетевым повтором.

        Для входа — не меньше ``auth_retry_min_interval_seconds``, чтобы серия
        ``authUser`` не привела к блокировке WAF.

        :param retry_class: Класс повтора операции.
        :return: Пауза в секундах.
        """
        if RetryClass.normalize(retry_class) is RetryClass.NETWORK_ONLY:
            return max(
                self.network_backoff_min_seconds,
                self.auth_retry_min_interval_seconds,
            )
        return self.network_backoff_min_seconds


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    """Ограничение частоты запросов клиента.

    :ivar requests_per_second: Не больше стольких запросов в секунду; ``None`` — без ограничения.
    :raises SDKConfigurationError: Значение не конечное или не больше нуля.
    """

    requests_per_second: float | None = None

    def __post_init__(self) -> None:
        # NaN и бесконечность дали бы интервал, при котором ограничитель молча не ждёт.
        if self.requests_per_second is not None and not (
            math.isfinite(self.requests_per_second) and self.requests_per_second > 0
        ):
            raise SDKConfigurationError(
                "requests_per_second должен быть конечным числом больше нуля"
            )

    @property
    def minimum_interval_seconds(self) -> float:
        """Минимальная пауза между запросами: ``1 / requests_per_second`` или 0 без ограничения."""
        if self.requests_per_second is None:
            return 0.0
        return 1.0 / self.requests_per_second


@dataclass(frozen=True, slots=True)
class ConcurrencyPolicy:
    """Сколько запросов клиента может выполняться одновременно.

    :ivar max_in_flight: Предел одновременных запросов, не меньше 1.
    :raises SDKConfigurationError: Значение меньше 1.
    """

    max_in_flight: int = 20

    def __post_init__(self) -> None:
        if self.max_in_flight < 1:
            raise SDKConfigurationError("max_in_flight должен быть не меньше 1")
