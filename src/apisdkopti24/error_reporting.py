from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from typing import Any

import httpx
from pydantic import ValidationError as PydanticValidationError

from .errors import (
    AccessDeniedError,
    APIError,
    ContractSelectionError,
    DuplicateConflictError,
    NotAuthenticatedError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .execution_budget import OperationTimeoutError, RetryBudgetExceededError


@dataclass(frozen=True, slots=True)
class ErrorDescriptor:
    """Safe, structured diagnostics for one terminal SDK failure."""

    sdk_error_code: str
    error_source: str
    exception_type: str
    error_message: str
    retryable: bool
    http_status_code: int | None = None
    api_status_code: int | None = None
    api_error_type: str | None = None

    def as_log_fields(self) -> dict[str, Any]:
        return asdict(self)


_API_ERROR_CODES: tuple[tuple[type[APIError], str], ...] = (
    (ValidationError, "api_validation_failed"),
    (NotAuthenticatedError, "api_not_authenticated"),
    (AccessDeniedError, "api_access_denied"),
    (NotFoundError, "api_not_found"),
    (DuplicateConflictError, "api_duplicate_conflict"),
    (RateLimitError, "api_rate_limited"),
    (ServerError, "api_server_error"),
)


def _api_error_code(error: APIError) -> str:
    for error_type, code in _API_ERROR_CODES:
        if isinstance(error, error_type):
            return code
    return "api_error"


def classify_exception(error: BaseException) -> ErrorDescriptor:
    """Classify an exception without exposing request, response, URL or file values."""

    exception_type = type(error).__name__

    if isinstance(error, APIError):
        return ErrorDescriptor(
            sdk_error_code=_api_error_code(error),
            error_source="api",
            exception_type=exception_type,
            error_message=error.message or "API вернул ошибку",
            retryable=error.context.retryable,
            http_status_code=error.context.http_status_code,
            api_status_code=error.context.api_status_code,
            api_error_type=error.context.error_type,
        )
    if isinstance(error, OperationTimeoutError):
        return ErrorDescriptor(
            sdk_error_code="operation_timeout",
            error_source="sdk",
            exception_type=exception_type,
            error_message="Превышен общий лимит времени операции",
            retryable=True,
        )
    if isinstance(error, RetryBudgetExceededError):
        return ErrorDescriptor(
            sdk_error_code="retry_budget_exceeded",
            error_source="sdk",
            exception_type=exception_type,
            error_message="Исчерпан лимит попыток операции",
            retryable=False,
        )
    if isinstance(error, asyncio.CancelledError):
        return ErrorDescriptor(
            sdk_error_code="operation_cancelled",
            error_source="application",
            exception_type=exception_type,
            error_message="Операция отменена вызывающим приложением",
            retryable=False,
        )
    if isinstance(error, ContractSelectionError):
        return ErrorDescriptor(
            sdk_error_code="contract_selection_failed",
            error_source="validation",
            exception_type=exception_type,
            error_message="Не удалось однозначно выбрать договор",
            retryable=False,
        )
    if isinstance(error, httpx.TimeoutException):
        return ErrorDescriptor(
            sdk_error_code="network_timeout",
            error_source="network",
            exception_type=exception_type,
            error_message="Истекло время ожидания сетевой операции",
            retryable=True,
        )
    if isinstance(error, httpx.RequestError):
        return ErrorDescriptor(
            sdk_error_code="network_error",
            error_source="network",
            exception_type=exception_type,
            error_message="Сетевая операция завершилась ошибкой",
            retryable=True,
        )
    if isinstance(error, PydanticValidationError):
        return ErrorDescriptor(
            sdk_error_code="response_validation_failed",
            error_source="validation",
            exception_type=exception_type,
            error_message="Ответ API не соответствует модели данных",
            retryable=False,
        )
    if isinstance(error, OSError):
        return ErrorDescriptor(
            sdk_error_code="filesystem_error",
            error_source="filesystem",
            exception_type=exception_type,
            error_message="Операция с файлом завершилась ошибкой",
            retryable=False,
        )
    if isinstance(error, ValueError):
        return ErrorDescriptor(
            sdk_error_code="value_validation_failed",
            error_source="validation",
            exception_type=exception_type,
            error_message="Значение не прошло проверку SDK",
            retryable=False,
        )
    if isinstance(error, TypeError):
        return ErrorDescriptor(
            sdk_error_code="response_shape_invalid",
            error_source="sdk",
            exception_type=exception_type,
            error_message="SDK получил данные неожиданного типа",
            retryable=False,
        )
    return ErrorDescriptor(
        sdk_error_code="sdk_internal_error",
        error_source="sdk",
        exception_type=exception_type,
        error_message="Непредвиденная внутренняя ошибка SDK",
        retryable=False,
    )


__all__ = ["ErrorDescriptor", "classify_exception"]
