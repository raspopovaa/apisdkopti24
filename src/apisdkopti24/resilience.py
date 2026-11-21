"""Автоматические повторы, ограничение частоты и одновременности запросов.

:class:`RetryController` повторяет попытку после сетевой ошибки (с растущей
паузой) и после ответа 429/509 (ограничение частоты); все паузы и попытки
укладываются в один бюджет операции. :class:`RateLimiter` держит минимальный
интервал между запросами и отдельный — между входами.
"""

from __future__ import annotations

import asyncio
import math
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass
from typing import TypeVar

import httpx

from .execution_budget import OperationBudget, OperationTimeoutError, acquired_within
from .logger import LoggerLike
from .policies import RetryClass, RetryPolicy
from .runtime import Clock

ResultT = TypeVar("ResultT")
Jitter = Callable[[float], float]


class RateLimited:
    """Внутренний результат: сервер ограничил частоту запросов; требуется ожидание."""


RATE_LIMITED = RateLimited()


class RateLimiter:
    """Согласовать интервалы запросов общего потока и авторизации.

    :param request_interval: Минимальная пауза между любыми запросами, секунд (0 — без паузы).
    :param auth_interval: Минимальная пауза между входами ``authUser``, секунд.
    :param clock: Часы для ожидания.
    """

    def __init__(
        self,
        *,
        request_interval: float,
        auth_interval: float,
        clock: Clock,
    ) -> None:
        self._request_interval = request_interval
        self._auth_interval = auth_interval
        self._clock = clock
        self._request_lock = asyncio.Lock()
        self._auth_lock = asyncio.Lock()
        self._last_request: float | None = None
        self._last_auth_request: float | None = None

    async def acquire(
        self,
        retry_class: str | RetryClass,
        budget: OperationBudget | None,
    ) -> None:
        """Дождаться своей очереди перед отправкой попытки.

        Для входа (класс ``NETWORK_ONLY``) сначала выдерживается интервал входов, затем
        общий интервал: иначе ``authUser`` ушёл бы в обход общего интервала. Ожидание в
        очереди и сама пауза не выходят за срок операции.

        :param retry_class: Класс повтора операции.
        :param budget: Бюджет операции или ``None``.
        :raises OperationTimeoutError: Очередь или пауза не укладываются в срок операции.
        """
        # Интервал входа ждётся первым: иначе authUser ушёл бы вне общего интервала.
        if RetryClass.normalize(retry_class) is RetryClass.NETWORK_ONLY:
            async with self._queued(self._auth_lock, budget):
                self._last_auth_request = await self._wait(
                    previous=self._last_auth_request,
                    interval=self._auth_interval,
                    budget=budget,
                )
        async with self._queued(self._request_lock, budget):
            self._last_request = await self._wait(
                previous=self._last_request,
                interval=self._request_interval,
                budget=budget,
            )

    def _queued(
        self,
        lock: asyncio.Lock,
        budget: OperationBudget | None,
    ) -> AbstractAsyncContextManager[None]:
        """Встать в очередь ограничителя, ожидая не дольше срока операции."""
        remaining = budget.remaining(self._clock.monotonic()) if budget is not None else None
        return acquired_within(
            lock, remaining, "Общий лимит времени операции истёк в очереди ограничителя частоты"
        )

    async def _wait(
        self,
        *,
        previous: float | None,
        interval: float,
        budget: OperationBudget | None,
    ) -> float:
        """Подождать, пока с прошлого запроса пройдёт ``interval``, и вернуть время отправки.

        :param previous: Время прошлого запроса по монотонным часам или ``None``.
        :param interval: Минимальный интервал, секунд.
        :param budget: Бюджет операции или ``None``.
        :return: Момент, который станет новым «прошлым запросом».
        :raises OperationTimeoutError: Пауза не укладывается в срок операции.
        """
        if interval <= 0:
            return self._clock.monotonic()
        now = self._clock.monotonic()
        if previous is not None:
            delay = previous + interval - now
            if delay > 0:
                if budget is not None:
                    budget.ensure_delay_fits(now, delay)
                await self._clock.sleep(delay)
                now = self._clock.monotonic()
        return now


@dataclass(frozen=True, slots=True)
class _AttemptPlan:
    """Сколько попыток положено операции и с какой паузы начинаются сетевые повторы."""

    method: str
    operation_name: str
    retry_class: str | RetryClass
    network_attempts: int
    rate_attempts: int
    initial_network_backoff: float


class _NetworkCause:
    """Последняя сетевая ошибка операции: причина возможного истечения её срока."""

    __slots__ = ("error",)

    def __init__(self) -> None:
        """Начать без сетевой ошибки."""
        self.error: httpx.RequestError | None = None


class RetryController:
    """Применить политику повторов с единым лимитом времени и попыток операции.

    Внешний цикл — сетевые повторы (``httpx.RequestError``), пауза удваивается до
    ``network_backoff_max_seconds``. Внутренний — повторы после 429/509 с паузой
    ``rate_limit_backoff_seconds × номер попытки``. Каждая пауза случайно
    уменьшается (джиттер), чтобы параллельные клиенты не повторяли запросы
    одновременно.

    :param policy: Число попыток и паузы.
    :param limiter: Ограничитель частоты.
    :param clock: Часы для пауз и срока операции.
    :param logger: Журнал предупреждений о повторах.
    :param jitter: Функция «верхняя граница паузы → пауза»; по умолчанию равномерно от 0.
    """

    def __init__(
        self,
        *,
        policy: RetryPolicy,
        limiter: RateLimiter,
        clock: Clock,
        logger: LoggerLike,
        jitter: Jitter | None = None,
    ) -> None:
        self._policy = policy
        self._limiter = limiter
        self._clock = clock
        self._logger = logger
        self._jitter = jitter or (lambda cap: random.uniform(0.0, cap))

    async def execute(
        self,
        *,
        method: str,
        operation_name: str,
        retry_class: str | RetryClass,
        idempotent: bool,
        budget: OperationBudget | None,
        billable: bool = False,
        attempt: Callable[[int, int, float | None], Awaitable[ResultT | RateLimited]],
        concurrency_gate: asyncio.Semaphore | None = None,
    ) -> ResultT:
        """Выполнить попытку с повторами по политике операции.

        Число попыток зависит от класса повтора, HTTP-метода, идемпотентности и
        тарификации (см. :class:`~apisdkopti24.policies.RetryPolicy`). Если срок
        операции истёк после сетевой ошибки, в ``__cause__`` ``OperationTimeoutError``
        остаётся эта ошибка: видно, что сервер так и не ответил.

        :param method: HTTP-метод.
        :param operation_name: Имя операции для журнала.
        :param retry_class: Класс повтора операции.
        :param idempotent: Повтор не создаст запись дважды.
        :param budget: Бюджет операции или ``None``.
        :param billable: Запрос тарифицируется; платное чтение после 429/509 не повторяется.
        :param attempt: Одна попытка: ``(номер, всего, остаток срока) → результат`` или
            ``RATE_LIMITED``.
        :param concurrency_gate: Семафор одновременных запросов клиента или ``None``.
        :return: Результат удачной попытки.
        :raises httpx.RequestError: Сетевая ошибка на последней попытке.
        :raises OperationTimeoutError: Истёк срок операции.
        :raises RetryBudgetExceededError: Исчерпаны попытки операции.
        """
        plan = self._plan(method, operation_name, retry_class, idempotent, billable)
        network_cause = _NetworkCause()
        network_backoff = plan.initial_network_backoff
        try:
            for network_attempt in range(1, plan.network_attempts + 1):
                try:
                    return await self._rate_limited_round(
                        plan, attempt, budget, concurrency_gate, network_cause
                    )
                except httpx.RequestError as error:
                    network_cause.error = error
                    if network_attempt >= plan.network_attempts:
                        raise
                    await self._wait(
                        budget,
                        self._jitter(network_backoff),
                        "Сетевая ошибка: метод=%s операция=%s попытка=%s/%s ожидание=%.2f с",
                        plan,
                        network_attempt,
                        plan.network_attempts,
                    )
                    network_backoff = min(
                        network_backoff * 2,
                        self._policy.network_backoff_max_seconds,
                    )
        except OperationTimeoutError as error:
            # Сохраняем сетевую причину, иначе истечение общего лимита скрывает,
            # что сервер так и не ответил (например, соединение не установилось).
            if network_cause.error is not None and error.__cause__ is None:
                raise error from network_cause.error
            raise
        raise RuntimeError("Цикл повторов после сетевых ошибок завершился без результата")

    def _plan(
        self,
        method: str,
        operation_name: str,
        retry_class: str | RetryClass,
        idempotent: bool,
        billable: bool,
    ) -> _AttemptPlan:
        """Число попыток и начальная пауза по классу повтора, методу и тарификации."""
        normalized_method = method.upper()
        return _AttemptPlan(
            method=normalized_method,
            operation_name=operation_name,
            retry_class=retry_class,
            network_attempts=self._policy.network_attempt_count(
                retry_class, normalized_method, idempotent=idempotent
            ),
            rate_attempts=self._policy.rate_limit_attempt_count(
                retry_class,
                normalized_method,
                idempotent=idempotent,
                billable=billable,
            ),
            initial_network_backoff=self._policy.initial_network_backoff(retry_class),
        )

    async def _rate_limited_round(
        self,
        plan: _AttemptPlan,
        attempt: Callable[[int, int, float | None], Awaitable[ResultT | RateLimited]],
        budget: OperationBudget | None,
        concurrency_gate: asyncio.Semaphore | None,
        network_cause: _NetworkCause,
    ) -> ResultT:
        """Попытки одной сетевой серии: повтор после 429/509 с растущей паузой."""
        for rate_attempt in range(1, plan.rate_attempts + 1):
            result = await self._send_once(plan, attempt, rate_attempt, budget, concurrency_gate)
            if not isinstance(result, RateLimited):
                return result
            # Сервер ответил: прежняя сетевая ошибка больше не причина возможного
            # истечения срока, иначе 509 выглядел бы как отказ соединения.
            network_cause.error = None
            await self._wait(
                budget,
                self._jitter(self._policy.rate_limit_backoff_seconds * rate_attempt),
                "Ограничение частоты запросов: метод=%s операция=%s попытка=%s/%s ожидание=%.2f с",
                plan,
                rate_attempt,
                plan.rate_attempts,
            )
        raise RuntimeError(
            "Цикл повторов после ограничения частоты запросов завершился без результата"
        )

    async def _send_once(
        self,
        plan: _AttemptPlan,
        attempt: Callable[[int, int, float | None], Awaitable[ResultT | RateLimited]],
        rate_attempt: int,
        budget: OperationBudget | None,
        concurrency_gate: asyncio.Semaphore | None,
    ) -> ResultT | RateLimited:
        """Отправить одну попытку: слот одновременности, очередь частоты, списание попытки.

        Слот занимается до ограничителя и списания попытки: иначе ожидание слота не
        входило бы в срок операции, а очередь уходила бы пачкой.

        :return: Результат попытки или ``RATE_LIMITED``.
        """
        # Слот берётся до лимитера и списания попытки: иначе ожидание
        # слота не входит в срок операции, а очередь уходит пачкой.
        async with self._attempt_slot(concurrency_gate, budget):
            await self._limiter.acquire(plan.retry_class, budget)
            remaining = (
                budget.claim_attempt(self._clock.monotonic()) if budget is not None else None
            )
            return await self._attempt_within_deadline(
                attempt, rate_attempt, plan.rate_attempts, remaining
            )

    @staticmethod
    async def _attempt_within_deadline(
        attempt: Callable[[int, int, float | None], Awaitable[ResultT | RateLimited]],
        rate_attempt: int,
        rate_attempts: int,
        remaining: float | None,
    ) -> ResultT | RateLimited:
        """Ограничить попытку целиком: таймаут httpx считается на каждое чтение отдельно."""
        if remaining is None or not math.isfinite(remaining):
            return await attempt(rate_attempt, rate_attempts, remaining)
        deadline = asyncio.timeout(remaining)
        try:
            async with deadline:
                return await attempt(rate_attempt, rate_attempts, remaining)
        except TimeoutError as error:
            if deadline.expired():
                # Как обычный таймаут чтения: сервер мог выполнить запрос, повтор решает политика.
                raise httpx.ReadTimeout("Общий лимит времени операции истёк при чтении") from error
            raise

    async def _wait(
        self,
        budget: OperationBudget | None,
        delay: float,
        message: str,
        plan: _AttemptPlan,
        attempt_number: int,
        attempts_total: int,
    ) -> None:
        """Выдержать паузу перед повтором, если она укладывается в срок операции."""
        if budget is not None:
            budget.ensure_delay_fits(self._clock.monotonic(), delay)
        self._logger.warning(
            message, plan.method, plan.operation_name, attempt_number, attempts_total, delay
        )
        await self._clock.sleep(delay)

    @asynccontextmanager
    async def _attempt_slot(
        self,
        gate: asyncio.Semaphore | None,
        budget: OperationBudget | None,
    ) -> AsyncIterator[None]:
        """Занять слот одновременных запросов, ожидая не дольше срока операции."""
        if gate is None:
            yield
            return
        remaining = budget.remaining(self._clock.monotonic()) if budget is not None else None
        async with acquired_within(
            gate, remaining, "Общий лимит времени операции истёк в ожидании свободного слота"
        ):
            yield


__all__ = ["RATE_LIMITED", "RateLimited", "RateLimiter", "RetryController"]
