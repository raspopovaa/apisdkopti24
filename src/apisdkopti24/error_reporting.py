from __future__ import annotations

import asyncio
import logging
import math
from contextlib import suppress
from dataclasses import asdict, dataclass
from typing import Any, Protocol
from uuid import uuid4

import httpx
from pydantic import ValidationError as PydanticValidationError

from .errors import (
    AccessDeniedError,
    APIError,
    ContractSelectionError,
    DuplicateConflictError,
    FileWriteError,
    NotAuthenticatedError,
    NotFoundError,
    RateLimitError,
    RequestPreparationError,
    RequestValidationError,
    ResponseShapeError,
    ResponseTooLargeError,
    SDKConfigurationError,
    ServerError,
    ValidationError,
    api_error_message,
    normalize_error_type,
)
from .execution_budget import (
    OperationBudget,
    OperationTimeoutError,
    RetryBudgetExceededError,
)
from .operations import OperationSpec
from .policies import RetryClass


class AuditClock(Protocol):
    def monotonic(self) -> float: ...


class AuditLogger(Protocol):
    def log(
        self,
        level: int,
        msg: object,
        *args: object,
        extra: dict[str, object] | None = None,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class ErrorDescriptor:
    """Безопасная структурированная диагностика ошибки, завершившей операцию SDK."""

    sdk_error_code: str
    error_source: str
    exception_type: str
    error_message: str
    transient: bool
    retry_allowed: bool
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

_WARNING_ERROR_CODES = frozenset(
    {
        "api_validation_failed",
        "api_not_authenticated",
        "api_access_denied",
        "api_not_found",
        "api_duplicate_conflict",
        "api_rate_limited",
        "contract_selection_failed",
        "request_validation_failed",
        "request_preparation_failed",
    }
)
_MAX_AUDIT_ELAPSED_MS = 86_400_000.0


def _api_error_code(error: APIError) -> str:
    for error_type, code in _API_ERROR_CODES:
        if isinstance(error, error_type):
            return code
    return "api_error"


def _retry_allowed(
    *,
    operation: OperationSpec[object] | None,
    transient: bool,
    network_failure: bool,
) -> bool:
    if not transient or operation is None:
        return False
    retry_class = RetryClass.normalize(operation.retry_class)
    if retry_class is RetryClass.NEVER:
        return False
    if retry_class is RetryClass.NETWORK_ONLY:
        return network_failure
    return operation.idempotent


def classify_exception(
    error: BaseException,
    operation: OperationSpec[object] | None = None,
) -> ErrorDescriptor:
    """Классифицировать исключение без раскрытия запроса, ответа, URL и путей к файлам."""

    exception_type = type(error).__name__
    code: str
    source: str
    message: str
    transient = False
    network_failure = False
    http_status_code: int | None = None
    api_status_code: int | None = None
    api_error_type: str | None = None

    if isinstance(error, APIError):
        code = _api_error_code(error)
        source = "api"
        message = api_error_message(error.status_code)
        transient = error.context.transient
        http_status_code = error.context.http_status_code
        api_status_code = error.context.api_status_code
        api_error_type = normalize_error_type(error.context.error_type)
    elif isinstance(error, OperationTimeoutError):
        code = "operation_timeout"
        source = "sdk"
        message = "Превышен общий лимит времени операции"
        transient = True
        network_failure = True
    elif isinstance(error, RetryBudgetExceededError):
        code = "retry_budget_exceeded"
        source = "sdk"
        message = "Исчерпан лимит попыток операции"
        transient = True
    elif isinstance(error, asyncio.CancelledError):
        code = "operation_cancelled"
        source = "application"
        message = "Операция отменена вызывающим приложением"
    elif isinstance(error, ContractSelectionError):
        code = "contract_selection_failed"
        source = "validation"
        message = "Не удалось однозначно выбрать договор"
    elif isinstance(error, httpx.TimeoutException):
        code = "network_timeout"
        source = "network"
        message = "Истекло время ожидания сетевой операции"
        transient = True
        network_failure = True
    elif isinstance(error, httpx.RequestError):
        code = "network_error"
        source = "network"
        message = "Сетевая операция завершилась ошибкой"
        transient = True
        network_failure = True
    elif isinstance(error, ResponseTooLargeError):
        code = "response_too_large"
        source = "response"
        message = "Ответ API превышает настроенный безопасный размер"
    elif isinstance(error, ResponseShapeError):
        code = "response_shape_invalid"
        source = "response"
        message = "Ответ API имеет неожиданную структуру"
    elif isinstance(error, PydanticValidationError):
        code = "response_validation_failed"
        source = "response"
        message = "Ответ API не соответствует модели данных"
    elif isinstance(error, FileWriteError):
        code = "file_write_failed"
        source = "filesystem"
        message = "Не удалось безопасно сохранить файл"
    elif isinstance(error, OSError):
        code = "filesystem_error"
        source = "filesystem"
        message = "Операция с файлом завершилась ошибкой"
    elif isinstance(error, SDKConfigurationError):
        code = "sdk_configuration_invalid"
        source = "configuration"
        message = "Конфигурация SDK не прошла проверку"
    elif isinstance(error, RequestPreparationError):
        code = "request_preparation_failed"
        source = "validation"
        message = "Не удалось подготовить запрос по контракту операции"
    elif isinstance(error, RequestValidationError):
        code = "request_validation_failed"
        source = "validation"
        message = "Параметры запроса не прошли проверку SDK"
    elif isinstance(error, ValueError):
        code = "value_validation_failed"
        source = "validation"
        message = "Значение не прошло проверку SDK"
    else:
        code = "sdk_internal_error"
        source = "sdk"
        message = "Непредвиденная внутренняя ошибка SDK"

    retry_allowed = _retry_allowed(
        operation=operation,
        transient=transient,
        network_failure=network_failure,
    )
    return ErrorDescriptor(
        sdk_error_code=code,
        error_source=source,
        exception_type=exception_type,
        error_message=message,
        transient=transient,
        retry_allowed=retry_allowed,
        retryable=retry_allowed,
        http_status_code=http_status_code,
        api_status_code=api_status_code,
        api_error_type=api_error_type,
    )


class OperationAudit:
    """Связать события операции и сформировать ровно одно завершающее событие."""

    def __init__(
        self,
        *,
        operation: OperationSpec[object],
        logger: AuditLogger,
        clock: AuditClock,
        api_version: str | None = None,
        route_name: str = "default",
    ) -> None:
        self._operation = operation
        self._logger = logger
        self._clock = clock
        self._started_at = clock.monotonic()
        self._terminal = False
        self.logging_failed = False
        requested_version = api_version or operation.default_version
        try:
            route = operation.resolve_route(
                api_version=requested_version,
                route_name=route_name,
            )
            audit_version = route.api_version
            audit_route_name = route.name
            http_method = route.http_method
        except ValueError:
            audit_version = "invalid"
            audit_route_name = "invalid"
            http_method = operation.http_method
        self._fields: dict[str, object] = {
            "request_audit": True,
            "operation_id": uuid4().hex,
            "operation": operation.name,
            "api_version": audit_version,
            "route_name": audit_route_name,
            "http_method": http_method,
            "recovered": False,
        }

    def start(self) -> None:
        self._emit(logging.INFO, "started")

    def event(self, event: str, *, recovered: bool = False) -> None:
        self._emit(logging.INFO, event, recovered=recovered)

    def completed(self, budget: OperationBudget, *, recovered: bool = False) -> None:
        self._terminal_event("completed", budget, recovered=recovered)

    def cancelled(
        self,
        error: asyncio.CancelledError,
        budget: OperationBudget,
        *,
        recovered: bool = False,
    ) -> None:
        self._terminal_event("cancelled", budget, recovered=recovered, error=error)

    def failed(
        self,
        error: Exception,
        budget: OperationBudget,
        *,
        recovered: bool = False,
    ) -> None:
        self._terminal_event("failed", budget, recovered=recovered, error=error)

    def _terminal_event(
        self,
        event: str,
        budget: OperationBudget,
        *,
        recovered: bool,
        error: BaseException | None = None,
    ) -> None:
        if self._terminal:
            return
        self._terminal = True
        elapsed_ms = (self._clock.monotonic() - self._started_at) * 1000
        if not math.isfinite(elapsed_ms):
            elapsed_ms = 0.0
        fields: dict[str, object] = {
            "elapsed_ms": min(_MAX_AUDIT_ELAPSED_MS, max(0.0, elapsed_ms)),
            "attempts_used": budget.attempts_used,
        }
        level = logging.INFO
        if error is not None:
            try:
                descriptor = classify_exception(error, self._operation)
            except Exception:
                descriptor = ErrorDescriptor(
                    sdk_error_code="sdk_internal_error",
                    error_source="sdk",
                    exception_type="Exception",
                    error_message="Не удалось классифицировать ошибку SDK",
                    transient=False,
                    retry_allowed=False,
                    retryable=False,
                )
            fields.update(descriptor.as_log_fields())
            if event == "failed":
                level = (
                    logging.WARNING
                    if descriptor.sdk_error_code in _WARNING_ERROR_CODES
                    else logging.ERROR
                )
        self._emit(level, event, recovered=recovered, fields=fields)

    def _emit(
        self,
        level: int,
        event: str,
        *,
        recovered: bool = False,
        fields: dict[str, object] | None = None,
    ) -> None:
        event_fields = dict(self._fields)
        event_fields.update({"event": event, "recovered": recovered})
        if fields:
            event_fields.update(fields)
        try:
            self._logger.log(
                level,
                "Аудит запроса API: событие=%s операция=%s operation_id=%s sdk_error_code=%s причина=%s",
                event,
                self._operation.name,
                self._fields["operation_id"],
                event_fields.get("sdk_error_code", "none"),
                event_fields.get("error_message", "нет"),
                extra=event_fields,
            )
        except Exception:
            # Сбой журналирования не должен менять результат операции API.
            self.logging_failed = True
            with suppress(Exception):
                logging.getLogger("apisdkopti24.audit").error(
                    "Не удалось записать аудит SDK; событие операции может отсутствовать"
                )


__all__ = ["ErrorDescriptor", "OperationAudit", "classify_exception"]
