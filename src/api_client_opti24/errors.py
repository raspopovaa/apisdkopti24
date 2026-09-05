from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ErrorContext:
    http_status_code: int
    api_status_code: int | None
    error_type: str | None
    messages: tuple[str, ...]
    raw_payload: Any
    endpoint: str | None
    method_name: str | None
    hint: str | None
    retryable: bool


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
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.http_status_code = http_status_code if http_status_code is not None else status_code
        self.api_status_code = api_status_code
        self.message = message
        self.body = body
        self.endpoint = endpoint
        self.context = ErrorContext(
            http_status_code=self.http_status_code,
            api_status_code=api_status_code,
            error_type=error_type,
            messages=messages or (() if not message else (message,)),
            raw_payload=body,
            endpoint=endpoint,
            method_name=method_name,
            hint=hint,
            retryable=retryable,
        )

    def __str__(self) -> str:
        location = f" during {self.endpoint}" if self.endpoint else ""
        suffix = f" Hint: {self.context.hint}" if self.context.hint else ""
        return f"{self.__class__.__name__}: [{self.status_code}] {self.message}{location}{suffix}"


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


def _extract_messages_from_error(error: Any) -> tuple[str, ...]:
    if isinstance(error, dict):
        raw_message = error.get("message")
        if isinstance(raw_message, list):
            return tuple(str(item) for item in raw_message if item is not None)
        if raw_message is not None:
            return (str(raw_message),)
    elif error is not None:
        return (str(error),)
    return ()


def _dedupe_messages(messages: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for message in messages:
        if message not in seen:
            seen.add(message)
            ordered.append(message)
    return tuple(ordered)


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
    messages: tuple[str, ...] = ()
    message = "Unknown API error"

    if isinstance(body, dict):
        status = body.get("status")
        if isinstance(status, dict):
            if isinstance(status.get("code"), int):
                api_status_code = status["code"]
            errors = status.get("errors")
            if isinstance(errors, list) and errors:
                collected_messages: list[str] = []
                for index, item in enumerate(errors):
                    if index == 0 and isinstance(item, dict):
                        error_type = item.get("type")
                    collected_messages.extend(_extract_messages_from_error(item))
                messages = _dedupe_messages(tuple(collected_messages))
            if not messages:
                status_message = status.get("message")
                messages = _extract_messages_from_error(status_message)
            if not messages:
                top_level_messages = body.get("messages")
                if isinstance(top_level_messages, list):
                    messages = tuple(str(item) for item in top_level_messages if item is not None)
                elif top_level_messages is not None:
                    messages = (str(top_level_messages),)
            if not messages:
                data = body.get("data")
                if isinstance(data, dict):
                    detail_messages: list[str] = []
                    for field_name, field_error in data.items():
                        extracted = _extract_messages_from_error(field_error)
                        if extracted:
                            detail_messages.extend(f"{field_name}: {item}" for item in extracted)
                    messages = _dedupe_messages(tuple(detail_messages))
            message = messages[0] if messages else message

    if not messages and isinstance(body, str) and body:
        messages = (body,)
        message = body

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
    retryable = effective_status_code in {429, 500, 502, 503, 504, 509}

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
        elif effective_status_code in {429, 509}:
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
                if effective_status_code in {429, 509}
                else (ServerError if effective_status_code >= 500 else APIError)
            ),
        )

    return exc_type(
        status_code=effective_status_code,
        message=message,
        body=body,
        endpoint=endpoint,
        http_status_code=resolved_http_status_code,
        api_status_code=api_status_code,
        error_type=error_type,
        messages=messages,
        method_name=method_name,
        hint=hint,
        retryable=retryable,
    )
