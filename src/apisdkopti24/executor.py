from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Protocol, TypeVar

from .config import TimeoutPolicy
from .error_reporting import OperationAudit
from .errors import (
    NotAuthenticatedError,
    RequestPreparationError,
    ResponseShapeError,
    SDKConfigurationError,
)
from .execution_budget import OperationBudget
from .logger import LoggerLike
from .modeling import ResponseModel, decode_model
from .operations import OperationSpec
from .requests import FileTarget, PreparedRequest, RequestOptions
from .runtime import Clock
from .service_base import APIKeyProvider, SessionContext, SessionGate, SessionRecovery
from .utils import REDACTED, is_sensitive_log_key, sanitize_for_logging

ResponseT = TypeVar("ResponseT", bound=ResponseModel)
ResultT = TypeVar("ResultT")


class JsonTransport(Protocol):
    async def request(self, request: PreparedRequest) -> dict[str, object]: ...


class BytesTransport(Protocol):
    async def request_stream(self, request: PreparedRequest) -> bytes: ...


class FileTransport(Protocol):
    async def request_stream_to_file(
        self,
        request: PreparedRequest,
        target: FileTarget,
    ) -> Path: ...


class Transport(JsonTransport, BytesTransport, FileTransport, Protocol):
    async def aclose(self) -> None: ...


class OperationExecutor:
    """Подготовить запросы по OperationSpec независимо от реализации транспорта."""

    def __init__(
        self,
        *,
        api_key_provider: APIKeyProvider,
        transport: Transport,
        session_context: SessionContext,
        timeouts: TimeoutPolicy,
        logger: LoggerLike,
        clock: Clock,
        max_attempts: int = 5,
    ) -> None:
        if max_attempts < 1:
            raise SDKConfigurationError("max_attempts должен быть не меньше 1")
        self._api_key_provider = api_key_provider
        self._transport = transport
        self._session_context = session_context
        self._timeouts = timeouts
        self._logger = logger
        self._clock = clock
        self._max_attempts = max_attempts

    def _headers(
        self,
        operation: OperationSpec[object],
        options: RequestOptions,
    ) -> dict[str, str]:
        api_key = self._api_key_provider.get_api_key()
        if not api_key:
            raise RequestPreparationError("Поставщик ключа API вернул пустое значение")
        context = self._session_context.request_context(contract_id=options.contract_id)
        headers: dict[str, str] = {
            "api_key": api_key,
            "date_time": self._clock.now().strftime("%Y-%m-%d %H:%M:%S"),
            "User-Agent": "apisdkopti24",
        }
        if options.json_body is not None:
            headers["Content-Type"] = "application/json"
        elif options.form is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if operation.requires_session and context.session_id:
            headers["session_id"] = context.session_id
            if context.contract_id and "header" in operation.request.contract_locations:
                headers["contract_id"] = context.contract_id
        protected = {"api_key", "session_id", "contract_id", "date_time", "content_type"}
        for name, value in options.headers.items():
            if name.lower().replace("-", "_") in protected:
                raise RequestPreparationError(f"Переопределение заголовка запрещено: {name}")
            headers[name] = value
        self._logger.debug("Подготовленные заголовки: %s", sanitize_for_logging(headers))
        return headers

    def prepare(
        self,
        operation: OperationSpec[object],
        options: RequestOptions,
        budget: OperationBudget,
    ) -> PreparedRequest:
        request_spec = operation.request
        if options.query and not request_spec.has_query:
            raise RequestPreparationError(
                f"Операция {operation.name!r} не принимает параметры строки запроса"
            )
        if options.form is not None and request_spec.body_kind != "form":
            raise RequestPreparationError(f"Операция {operation.name!r} не принимает данные формы")
        if options.json_body is not None and request_spec.body_kind != "json":
            raise RequestPreparationError(f"Операция {operation.name!r} не принимает тело JSON")
        if options.contract_id is not None and "header" not in request_spec.contract_locations:
            raise RequestPreparationError(
                f"Операция {operation.name!r} не принимает заголовок contract_id"
            )
        route = operation.resolve_route(
            api_version=options.api_version,
            route_name=options.route_name,
        )
        context = self._session_context.request_context(contract_id=options.contract_id)
        return PreparedRequest(
            method=route.http_method,
            endpoint=route.render(options.path_params),
            api_version=route.api_version,
            headers=self._headers(operation, options),
            query=options.query,
            form=options.form,
            json_body=options.json_body,
            timeout=self._timeouts.resolve(operation.timeout_class),
            method_name=operation.name,
            retry_class=operation.retry_class,
            idempotent=operation.idempotent,
            request_context=context,
            operation_budget=budget,
        )

    def create_budget(self, operation: OperationSpec[object]) -> OperationBudget:
        return OperationBudget(
            deadline_at=self._clock.monotonic()
            + self._timeouts.resolve_total(operation.timeout_class),
            max_attempts=self._max_attempts,
        )

    @property
    def clock(self) -> Clock:
        return self._clock

    @staticmethod
    def decode_response(
        operation: OperationSpec[ResponseT],
        payload: dict[str, object],
    ) -> ResponseT:
        if operation.response_type is None:
            raise ResponseShapeError(f"Операция JSON {operation.name!r} не содержит типа ответа")
        return decode_model(operation.response_type, payload)

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
        *,
        budget: OperationBudget | None = None,
    ) -> ResponseT:
        request_options = options or RequestOptions()
        prepared = self.prepare(
            operation,
            request_options,
            budget or self.create_budget(operation),
        )
        payload = await self._transport.request(prepared)
        return self.decode_response(operation, payload)

    async def send_json(self, request: PreparedRequest) -> dict[str, object]:
        return await self._transport.request(request)

    async def send_bytes(self, request: PreparedRequest) -> bytes:
        return await self._transport.request_stream(request)

    async def send_file(self, request: PreparedRequest, target: FileTarget) -> Path:
        return await self._transport.request_stream_to_file(request, target)


class DefaultRequestExecutor:
    """Проверить и восстановить сессию, записать аудит и разобрать типизированный ответ."""

    def __init__(
        self,
        *,
        operation_executor: OperationExecutor,
        session_gate: SessionGate,
        session_recovery: SessionRecovery,
        logger: LoggerLike,
        clock: Clock | None = None,
    ) -> None:
        self._operations = operation_executor
        self._session_gate = session_gate
        self._session_recovery = session_recovery
        self._logger = logger
        self._clock = clock or operation_executor.clock

    def preview_headers(
        self,
        operation: OperationSpec[object],
        options: RequestOptions | None = None,
    ) -> dict[str, str]:
        """Подготовить очищенные заголовки для диагностики без раскрытия секретов."""
        headers = self._operations._headers(operation, options or RequestOptions())
        return {
            name: REDACTED if is_sensitive_log_key(name) else value
            for name, value in headers.items()
        }

    async def _run_with_recovery(
        self,
        operation: OperationSpec[object],
        request: Callable[[], Awaitable[ResultT]],
        budget: OperationBudget,
        audit: OperationAudit,
    ) -> ResultT:
        audit.start()
        try:
            result = await request()
        except NotAuthenticatedError as error:
            if not operation.requires_session:
                audit.failed(error, budget)
                raise
            audit.event("session_recovery")
            try:
                await self._session_recovery.recover(budget)
                result = await request()
            except asyncio.CancelledError as error:
                audit.cancelled(error, budget, recovered=True)
                raise
            except Exception as error:
                audit.failed(error, budget, recovered=True)
                raise
            audit.completed(budget, recovered=True)
            return result
        except asyncio.CancelledError as error:
            audit.cancelled(error, budget)
            raise
        except Exception as error:
            audit.failed(error, budget)
            raise
        audit.completed(budget)
        return result

    async def _prepared(
        self,
        operation: OperationSpec[object],
        options: RequestOptions,
        budget: OperationBudget,
    ) -> PreparedRequest:
        if operation.requires_session:
            await self._session_gate.ensure_authenticated()
        return self._operations.prepare(operation, options, budget)

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
    ) -> ResponseT:
        request_options = options or RequestOptions()
        budget = self._operations.create_budget(operation)
        audit = OperationAudit(
            operation=operation,
            logger=self._logger,
            clock=self._clock,
            api_version=request_options.api_version,
            route_name=request_options.route_name,
        )

        async def send() -> ResponseT:
            prepared = await self._prepared(operation, request_options, budget)
            payload = await self._operations.send_json(prepared)
            return self._operations.decode_response(operation, payload)

        return await self._run_with_recovery(operation, send, budget, audit)

    async def execute_stream(
        self,
        operation: OperationSpec[bytes],
        options: RequestOptions | None = None,
    ) -> bytes:
        request_options = options or RequestOptions()
        budget = self._operations.create_budget(operation)
        audit = OperationAudit(
            operation=operation,
            logger=self._logger,
            clock=self._clock,
            api_version=request_options.api_version,
            route_name=request_options.route_name,
        )

        async def send() -> bytes:
            prepared = await self._prepared(operation, request_options, budget)
            return await self._operations.send_bytes(prepared)

        return await self._run_with_recovery(operation, send, budget, audit)

    async def execute_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path:
        request_options = options or RequestOptions()
        budget = self._operations.create_budget(operation)
        audit = OperationAudit(
            operation=operation,
            logger=self._logger,
            clock=self._clock,
            api_version=request_options.api_version,
            route_name=request_options.route_name,
        )
        target = FileTarget(Path(destination))

        async def send() -> Path:
            prepared = await self._prepared(operation, request_options, budget)
            return await self._operations.send_file(prepared, target)

        return await self._run_with_recovery(operation, send, budget, audit)


__all__ = [
    "BytesTransport",
    "DefaultRequestExecutor",
    "FileTransport",
    "JsonTransport",
    "OperationExecutor",
    "Transport",
]
