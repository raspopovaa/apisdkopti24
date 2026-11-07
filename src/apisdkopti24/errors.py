from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .sanitization import message_mentions_sensitive_key, scrub


class Opti24Error(Exception):
    """Общий базовый класс всех исключений SDK.

    Позволяет поймать любую ошибку SDK одним ``except Opti24Error``. Встроенные
    родители (``ValueError``, ``TimeoutError`` и другие) у классов сохраняются.
    """


class SDKConfigurationError(Opti24Error, ValueError):
    """Конфигурация SDK не позволяет начать операцию API."""


class RequestValidationError(Opti24Error, ValueError):
    """Параметры публичного запроса нарушают правила проверки SDK."""


class RequestPreparationError(Opti24Error, ValueError):
    """Проверенные значения нельзя разместить в запросе выбранной операции."""


class ResponseTooLargeError(Opti24Error, ValueError):
    """Ответ превышает настроенный предел загрузки в память."""

    def __init__(self, *, maximum_bytes: int) -> None:
        super().__init__("Ответ превышает настроенный предел размера")
        self.maximum_bytes = maximum_bytes


class ResponseShapeError(Opti24Error, TypeError):
    """Разобранный ответ API имеет неожиданную структуру верхнего уровня."""


# Текст исключения должен оставаться однострочным и коротким, даже если сервер
# вернул объект с тысячами неподходящих записей.
_MAX_LISTED_RESPONSE_PROBLEMS = 3
_MAX_RESPONSE_PROBLEMS = 50
_MAX_LOCATION_LENGTH = 120

ResponseProblem = tuple[str, str]
"""Путь поля и тип ошибки Pydantic: без значения из ответа."""


class ResponseValidationError(Opti24Error, ValueError):
    """Ответ API не соответствует модели данных SDK.

    ``problems`` содержит пары «путь поля, тип ошибки» без значений из ответа;
    исходная ошибка Pydantic доступна в ``__cause__``.
    """

    def __init__(
        self,
        *,
        operation: str,
        model_name: str,
        problems: tuple[ResponseProblem, ...],
        problem_count: int,
    ) -> None:
        self.operation = operation
        self.model_name = model_name
        self.problems = problems
        self.problem_count = problem_count
        listed = "; ".join(
            f"{location}: {kind}" for location, kind in problems[:_MAX_LISTED_RESPONSE_PROBLEMS]
        )
        hidden = problem_count - min(len(problems), _MAX_LISTED_RESPONSE_PROBLEMS)
        suffix = f"; и ещё {hidden}" if hidden > 0 else ""
        super().__init__(
            f"Ответ API операции {operation} не соответствует модели {model_name}: "
            f"{listed}{suffix}"
        )

    @classmethod
    def from_pydantic(
        cls, error: Any, *, operation: str, model_name: str
    ) -> ResponseValidationError:
        details = error.errors(include_url=False, include_input=False, include_context=False)
        problems = tuple(
            (
                _bounded_single_line(".".join(str(part) for part in item["loc"]) or "<корень>"),
                _bounded_single_line(str(item.get("type", "unknown"))),
            )
            for item in details[:_MAX_RESPONSE_PROBLEMS]
        )
        return cls(
            operation=operation,
            model_name=model_name,
            problems=problems,
            problem_count=len(details),
        )


def _bounded_single_line(value: str) -> str:
    return " ".join(scrub(value).split())[:_MAX_LOCATION_LENGTH]


class PaginationLimitError(Opti24Error, RuntimeError):
    """Итератор дошёл до ``max_pages`` раньше, чем выдал ``total_count`` записей.

    Выдаётся только при ``strict=True``: без него итератор пишет предупреждение в
    журнал и останавливается. Уже выданные записи остаются у приложения.
    """

    def __init__(self, *, operation: str, max_pages: int, received: int, total_count: int) -> None:
        super().__init__(
            f"{operation}: перебор остановлен на max_pages={max_pages}, получено "
            f"{received} из {total_count} записей; увеличьте max_pages"
        )
        self.operation = operation
        self.max_pages = max_pages
        self.received = received
        self.total_count = total_count


class ReportWaitTimeoutError(Opti24Error, TimeoutError):
    """Отчёт не стал готов к скачиванию за отведённое время ожидания.

    ``available_after`` — последнее значение из списка задач; ``None``, если задача
    так и не появилась в списке. Идентификатор задачи есть в ``job_id``, но не в
    тексте исключения.
    """

    def __init__(self, *, job_id: str, timeout: float, available_after: int | None) -> None:
        if available_after is None:
            reason = "задача не появилась в списке заказанных отчётов"
        else:
            reason = f"последнее available_after={available_after} с"
        super().__init__(
            f"Отчёт не готов за {timeout:g} с: {reason}; не заказывайте отчёт заново, "
            "продолжите ожидание"
        )
        self.job_id = job_id
        self.timeout = timeout
        self.available_after = available_after


class FileWriteError(Opti24Error, OSError):
    """Загружаемый файл не удалось безопасно сохранить."""


# Приложение №1 спецификации 1.1.60: страны, с IP-адресов которых API принимает запросы.
API_ALLOWED_COUNTRIES = ("RU", "BY", "KZ", "TJ", "KG", "IQ", "AE", "RS")


class APINetworkError(Opti24Error):
    """Обмен с сервером API прерван сетевой ошибкой: ответ сервера не получен.

    Если соединение было установлено, сервер мог получить и выполнить запрос.
    Исходная ошибка httpx сохраняется в ``__cause__``.
    """

    def __init__(self, host: str, message: str | None = None) -> None:
        super().__init__(
            message
            or (
                f"Обмен с сервером API {host} прерван сетевой ошибкой, ответ не получен. "
                "Сервер мог выполнить запрос: проверьте результат чтением, прежде чем "
                "повторять изменяющую операцию"
            )
        )
        self.host = host


class APIConnectionError(APINetworkError):
    """Соединение с сервером API не установлено: ответ сервера не получен.

    Сервер API не отвечает на подключения с IP-адресов вне разрешённых стран,
    поэтому такой отказ выглядит как timeout подключения, а не как HTTP-ошибка.
    Запрос до сервера не дошёл.
    """

    def __init__(self, host: str) -> None:
        super().__init__(
            host,
            f"Не удалось установить соединение с сервером API {host}. "
            "API принимает запросы только с IP-адресов стран "
            f"{', '.join(API_ALLOWED_COUNTRIES)}; проверьте сеть, VPN или прокси",
        )


class APIResponseTimeoutError(APINetworkError):
    """Сервер API не ответил за timeout попытки после установки соединения.

    Запрос мог быть получен и выполнен: долгие операции сервер иногда завершает
    уже после того, как клиент перестал ждать ответ.
    """

    def __init__(self, host: str) -> None:
        super().__init__(
            host,
            f"Сервер API {host} не ответил за отведённое время. Запрос мог быть получен "
            "и выполнен: проверьте результат чтением, прежде чем повторять изменяющую "
            "операцию; для долгих операций увеличьте TimeoutPolicy",
        )


@dataclass(frozen=True, slots=True)
class ErrorContext:
    http_status_code: int
    api_status_code: int | None
    error_type: str | None
    messages: tuple[str, ...]
    method_name: str | None
    hint: str | None
    transient: bool
    """Ошибка может быть временной; это не разрешает повтор операции."""
    reason: str | None = None
    """Стабильный код распознанного ответа API (например, ``processing_refused``).

    ``None``, если SDK не узнал ответ по таблице известных ответов.
    """


class ContractSelectionError(Opti24Error, ValueError):
    """Не удалось однозначно выбрать договор для серверной сессии."""

    def __init__(
        self,
        message: str,
        *,
        available_contracts: tuple[tuple[str, str], ...] = (),
    ) -> None:
        super().__init__(message)
        self.available_contracts = available_contracts


class APIError(Opti24Error):
    def __init__(
        self,
        status_code: int,
        message: str = "",
        body: Any = None,
        endpoint: str | None = None,
        *,
        http_status_code: int | None = None,
        api_status_code: int | None = None,
        error_type: str | None = None,
        messages: tuple[str, ...] | None = None,
        method_name: str | None = None,
        hint: str | None = None,
        transient: bool = False,
        server_messages: tuple[str, ...] = (),
        reason: str | None = None,
    ) -> None:
        public_message = _public_error_message(message)
        super().__init__(f"{status_code}: {public_message}")
        self.status_code = status_code
        self.http_status_code: int = (
            http_status_code if http_status_code is not None else status_code
        )
        self.api_status_code = api_status_code
        self.message = public_message
        self.endpoint = endpoint
        self.__raw_payload = body
        # Сообщения сервера после очистки: только для текста исключения, не для audit.
        self.server_messages: tuple[str, ...] = tuple(
            cleaned for item in server_messages if (cleaned := _public_error_message(item))
        )
        self.context: ErrorContext = ErrorContext(
            http_status_code=self.http_status_code,
            api_status_code=api_status_code,
            error_type=normalize_error_type(error_type),
            messages=(
                tuple(_public_error_message(item) for item in messages)
                if messages
                else (() if not public_message else (public_message,))
            ),
            method_name=method_name,
            hint=hint,
            transient=transient,
            reason=reason,
        )

    def get_raw_payload(self) -> Any:
        """Вернуть исходный ответ сервера без очистки для явной локальной диагностики."""
        return self.__raw_payload

    def __str__(self) -> str:
        location = f" при выполнении {self.context.method_name}" if self.context.method_name else ""
        server = (
            f" Сообщение сервера: {'; '.join(self.server_messages)}."
            if self.server_messages
            else ""
        )
        suffix = f" Подсказка: {self.context.hint}" if self.context.hint else ""
        return (
            f"{self.__class__.__name__}: [{self.status_code}] {self.message}"
            f"{location}{server}{suffix}"
        )


_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _public_error_message(message: str, *, maximum_length: int = 500) -> str:
    if message_mentions_sensitive_key(message):
        normalized = "Ответ API с ошибкой содержал конфиденциальные данные"
    else:
        without_ansi = _ANSI_ESCAPE_RE.sub(" ", message)
        printable = "".join(char if char.isprintable() else " " for char in without_ansi)
        normalized = " ".join(scrub(printable).split())
    if len(normalized) <= maximum_length:
        return normalized
    return normalized[: maximum_length - 1].rstrip() + "…"


class ValidationError(APIError):
    pass


class NotAuthenticatedError(APIError):
    pass


class AccessDeniedError(APIError):
    pass


class NotFoundError(APIError):
    pass


class DuplicateConflictError(APIError):
    pass


class RateLimitError(APIError):
    pass


class ServerError(APIError):
    pass


# Классы ниже уточняют ответы API, у которых HTTP-код не указывает причину. SDK
# узнаёт их по тексту сообщения сервера; если оператор изменит формулировку,
# придёт исходный класс по коду (AccessDeniedError или ServerError).


class ProcessingRefusalError(AccessDeniedError):
    """Процессинг отказал в операции по карте: ``403`` с «[Код ошибки: NN]» в тексте.

    ``processing_code`` содержит код отказа процессинга из текста сообщения.
    """

    processing_code: int | None = None


class PlanNotPaidError(AccessDeniedError):
    """Метод закрыт тарифом: ``403`` «требуется оплатить API VIP»."""


class ObjectNotAccessibleError(AccessDeniedError):
    """Объект не найден или чужой: ``403`` «Не найден контракт, карта или группа».

    API отвечает так и на несуществующий ID, и на объект другого договора, поэтому
    по ответу эти случаи не различить.
    """


class DuplicateLoginError(AccessDeniedError, DuplicateConflictError):
    """Пользователь с таким логином уже есть: сервер отвечает ``403``, а не ``409``.

    Ловится и как ``AccessDeniedError``, и как ``DuplicateConflictError``.
    """


class InviteNotReadyError(ServerError):
    """Приглашение без карт и шаблона: сервер отвечает ``500``, хотя это ошибка данных.

    ``context.transient`` равен ``False``: повтор того же запроса не поможет.
    """


class WafBlockedError(AccessDeniedError):
    """Запрос остановил WAF оператора: ``403`` с HTML-страницей вместо JSON.

    Так WAF отвечает на неизвестный путь, на заблокированный User-Agent и временным
    баном после серии входов. HTML-страница в текст исключения не попадает.
    """


class ReportFailedError(ServerError):
    """Отчёт не будет сформирован: сервер отвечает ``500`` на скачивание неудачной задачи.

    ``context.transient`` равен ``False``: повтор скачивания не поможет, закажите отчёт заново.
    """


ERROR_HINTS: dict[int, str] = {
    400: "Проверьте структуру запроса и корректность передаваемых параметров.",
    401: "Проверьте, что пользователь авторизован и передан корректный session_id.",
    403: "Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.",
    404: "Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.",
    409: "Проверьте интеграцию на повторную отправку однотипных запросов.",
    429: "Превышен лимит запросов. Повтор после задержки допустим только для безопасной операции.",
    500: "Ошибка сервера. Перед повтором убедитесь в безопасности операции; при неопределённом результате проверьте её состояние.",
    509: "Превышено ограничение по запросам или каналу. Повтор после задержки допустим только для безопасной операции.",
}


API_ERROR_MESSAGES: dict[int, str] = {
    400: "Некорректные параметры запроса",
    401: "Необходима авторизация",
    403: "Доступ запрещён",
    404: "Объект или маршрут не найден",
    409: "Конфликт повторного запроса",
    429: "Превышен лимит запросов",
    509: "Превышен лимит запросов",
}
_ERROR_TYPE_CLASSES: dict[str, type[APIError]] = {
    "validationFailed": ValidationError,
    "notAuthenticated": NotAuthenticatedError,
    "accessDenied": AccessDeniedError,
    "notFound": NotFoundError,
    "duplicateConflict": DuplicateConflictError,
    "tooManyRequests": RateLimitError,
    "rateLimitExceeded": RateLimitError,
    "internalError": ServerError,
}
KNOWN_ERROR_TYPES = frozenset(_ERROR_TYPE_CLASSES)


MAX_SERVER_MESSAGES = 5


def normalize_error_type(value: object) -> str | None:
    """Допустить в обычную диагностику только известные типы ошибок API."""
    return value if isinstance(value, str) and value in KNOWN_ERROR_TYPES else None


def api_error_message(status_code: int) -> str:
    """Вернуть локальное сообщение без подстановки значений, полученных от сервера."""
    return API_ERROR_MESSAGES.get(
        status_code, "Ошибка сервера API" if status_code >= 500 else "Ошибка API"
    )
