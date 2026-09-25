from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .http_status import RATE_LIMIT_STATUS_CODES, RETRYABLE_STATUS_CODES
from .sanitization import message_mentions_sensitive_key, scrub


class SDKConfigurationError(ValueError):
    """SDK configuration is invalid before an API operation can start."""


class RequestValidationError(ValueError):
    """Public request values violate an SDK-side contract."""


class RequestPreparationError(ValueError):
    """Validated values cannot be placed into the requested wire operation."""


class ResponseTooLargeError(ValueError):
    """A response exceeded its configured in-memory safety limit."""

    def __init__(self, *, maximum_bytes: int) -> None:
        super().__init__("response exceeds configured size limit")
        self.maximum_bytes = maximum_bytes


class ResponseShapeError(TypeError):
    """A decoded API response has an unexpected top-level shape."""


class FileWriteError(OSError):
    """A download could not be safely persisted to its destination."""


@dataclass(frozen=True, slots=True)
class ErrorContext:
    http_status_code: int
    api_status_code: int | None
    error_type: str | None
    messages: tuple[str, ...]
    method_name: str | None
    hint: str | None
    retryable: bool

    @property
    def transient(self) -> bool:
        """Failure may be temporary; this does not authorize retrying an operation."""
        return self.retryable


class ContractSelectionError(ValueError):
    """Не удалось однозначно выбрать договор для серверной сессии."""

    def __init__(
        self,
        message: str,
        *,
        available_contracts: tuple[tuple[str, str], ...] = (),
    ) -> None:
        super().__init__(message)
        self.available_contracts = available_contracts


class APIError(Exception):
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
        retryable: bool = False,
    ) -> None:
        public_message = _public_error_message(message)
        super().__init__(f"{status_code}: {public_message}")
        self.status_code = status_code
        self.http_status_code = http_status_code if http_status_code is not None else status_code
        self.api_status_code = api_status_code
        self.message = public_message
        self.endpoint = endpoint
        self.__raw_payload = body
        self.context = ErrorContext(
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
            retryable=retryable,
        )

    def get_raw_payload(self) -> Any:
        """Return the unredacted server payload for explicit local diagnostics."""
        return self.__raw_payload

    def __str__(self) -> str:
        location = f" during {self.context.method_name}" if self.context.method_name else ""
        suffix = f" Hint: {self.context.hint}" if self.context.hint else ""
        return f"{self.__class__.__name__}: [{self.status_code}] {self.message}{location}{suffix}"


def _public_error_message(message: str, *, maximum_length: int = 500) -> str:
    if message_mentions_sensitive_key(message):
        normalized = "API error response contained sensitive data"
    else:
        normalized = " ".join(scrub(message).split())
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


ERROR_HINTS: dict[int, str] = {
    400: "Проверьте структуру запроса и корректность передаваемых параметров.",
    401: "Проверьте, что пользователь авторизован и передан корректный session_id.",
    403: "Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.",
    404: "Проверьте идентификаторы и endpoint: запрашиваемый ресурс не найден.",
    409: "Проверьте интеграцию на повторную отправку однотипных запросов.",
    429: "Превышен лимит запросов — повторите запрос позже с backoff.",
    500: "Серверная ошибка — повторите запрос позже или обратитесь в поддержку.",
    509: "Превышено ограничение по запросам/каналу — повторите запрос позже.",
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
KNOWN_ERROR_TYPES = frozenset(
    {
        "validationFailed",
        "notAuthenticated",
        "accessDenied",
        "notFound",
        "duplicateConflict",
        "tooManyRequests",
        "rateLimitExceeded",
        "internalError",
    }
)


def normalize_error_type(value: object) -> str | None:
    """Only contract symbols may enter ordinary diagnostics."""
    return value if isinstance(value, str) and value in KNOWN_ERROR_TYPES else None


def api_error_message(status_code: int) -> str:
    """Return a local message without interpolating server-controlled values."""
    return API_ERROR_MESSAGES.get(
        status_code, "Ошибка сервера API" if status_code >= 500 else "Ошибка API"
    )


def build_api_error(
    *,
    status_code: int,
    body: Any,
    endpoint: str | None,
    method_name: str | None = None,
    http_status_code: int | None = None,
) -> APIError:
    error_map: dict[str, type[APIError]] = {
        "validationFailed": ValidationError,
        "notAuthenticated": NotAuthenticatedError,
        "accessDenied": AccessDeniedError,
        "notFound": NotFoundError,
        "duplicateConflict": DuplicateConflictError,
        "tooManyRequests": RateLimitError,
        "rateLimitExceeded": RateLimitError,
        "internalError": ServerError,
    }

    error_type: str | None = None
    api_status_code: int | None = None
    if isinstance(body, dict):
        status = body.get("status")
        if isinstance(status, dict):
            raw_code = status.get("code")
            if type(raw_code) is int:
                api_status_code = raw_code
            errors = status.get("errors")
            if isinstance(errors, list) and errors and isinstance(errors[0], dict):
                error_type = normalize_error_type(errors[0].get("type"))

    resolved_http_status_code = http_status_code if http_status_code is not None else status_code
    http_failed = not 200 <= resolved_http_status_code < 300
    effective_status_code = (
        resolved_http_status_code
        if http_failed
        else (
            api_status_code
            if api_status_code is not None and not 200 <= api_status_code < 300
            else status_code
        )
    )
    hint = ERROR_HINTS.get(
        effective_status_code,
        ERROR_HINTS.get(500) if effective_status_code >= 500 else None,
    )
    retryable = effective_status_code in RETRYABLE_STATUS_CODES

    exc_type: type[APIError]
    if http_failed or error_type is None:
        if effective_status_code == 400:
            exc_type = ValidationError
        elif effective_status_code == 401:
            exc_type = NotAuthenticatedError
        elif effective_status_code == 403:
            exc_type = AccessDeniedError
        elif effective_status_code == 404:
            exc_type = NotFoundError
        elif effective_status_code == 409:
            exc_type = DuplicateConflictError
        elif effective_status_code in RATE_LIMIT_STATUS_CODES:
            exc_type = RateLimitError
        elif effective_status_code >= 500:
            exc_type = ServerError
        else:
            exc_type = APIError
    else:
        exc_type = error_map.get(
            error_type,
            (
                RateLimitError
                if effective_status_code in RATE_LIMIT_STATUS_CODES
                else (ServerError if effective_status_code >= 500 else APIError)
            ),
        )

    return exc_type(
        status_code=effective_status_code,
        message=api_error_message(effective_status_code),
        body=body,
        endpoint=endpoint,
        http_status_code=resolved_http_status_code,
        api_status_code=api_status_code,
        error_type=error_type,
        messages=(api_error_message(effective_status_code),),
        method_name=method_name,
        hint=hint,
        retryable=retryable,
    )
