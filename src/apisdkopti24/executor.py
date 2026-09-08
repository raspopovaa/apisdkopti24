from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Protocol, TypeVar

from .config import TimeoutPolicy
from .errors import NotAuthenticatedError
from .execution_budget import OperationBudget
from .logger import LoggerLike
from .modeling import ResponseModel, decode_model
from .operations import OperationSpec
from .requests import FileTarget, PreparedRequest, RequestOptions
from .runtime import Clock
from .service_base import APIKeyProvider, SessionContext, SessionGate, SessionRecovery
from .utils import sanitize_for_logging

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
    """Resolve an OperationSpec and produce transport-neutral requests."""

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
            raise ValueError("max_attempts must be at least 1")
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
            raise ValueError("API key provider returned an empty value")
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
        protected = {"api_key", "session_id", "date_time"}
        for name, value in options.headers.items():
            if name.lower().replace("-", "_") in protected:
                raise ValueError(f"Header override is not allowed: {name}")
            headers[name] = value
        self._logger.debug("Prepared headers: %s", sanitize_for_logging(headers))
        return headers

    def prepare(
        self,
        operation: OperationSpec[object],
        options: RequestOptions,
        budget: OperationBudget,
    ) -> PreparedRequest:
        request_spec = operation.request
        if options.query and not request_spec.has_query:
            raise ValueError(f"Operation {operation.name!r} does not accept query parameters")
        if options.form is not None and request_spec.body_kind != "form":
            raise ValueError(f"Operation {operation.name!r} does not accept form data")
        if options.json_body is not None and request_spec.body_kind != "json":
            raise ValueError(f"Operation {operation.name!r} does not accept a JSON body")
        if options.contract_id is not None and "header" not in request_spec.contract_locations:
            raise ValueError(f"Operation {operation.name!r} does not accept contract_id header")
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
        if operation.response_type is None:
            raise TypeError(f"JSON operation {operation.name!r} has no response type")
        return decode_model(operation.response_type, payload)

    async def send_json(self, request: PreparedRequest) -> dict[str, object]:
        return await self._transport.request(request)

    async def send_bytes(self, request: PreparedRequest) -> bytes:
        return await self._transport.request_stream(request)

    async def send_file(self, request: PreparedRequest, target: FileTarget) -> Path:
        return await self._transport.request_stream_to_file(request, target)


class DefaultRequestExecutor:
    """Apply session gating, recovery, auditing and typed response decoding."""

    def __init__(
        self,
        *,
        operation_executor: OperationExecutor,
        session_gate: SessionGate,
        session_recovery: SessionRecovery,
        logger: LoggerLike,
    ) -> None:
        self._operations = operation_executor
        self._session_gate = session_gate
        self._session_recovery = session_recovery
        self._logger = logger

    def preview_headers(
        self,
        operation: OperationSpec[object],
        options: RequestOptions | None = None,
    ) -> dict[str, str]:
        """Build headers for diagnostics without exposing credential providers."""
        return self._operations._headers(operation, options or RequestOptions())

    def _audit(
        self, event: str, operation: OperationSpec[object], *, recovered: bool = False
    ) -> None:
        self._logger.info(
            "API request audit",
            extra={
                "request_audit": True,
                "event": event,
                "operation": operation.name,
                "api_version": operation.default_version,
                "recovered": recovered,
            },
        )

    async def _run_with_recovery(
        self,
        operation: OperationSpec[object],
        request: Callable[[], Awaitable[ResultT]],
        budget: OperationBudget,
    ) -> ResultT:
        self._audit("started", operation)
        try:
            result = await request()
        except NotAuthenticatedError:
            if not operation.requires_session:
                self._audit("failed", operation)
                raise
            self._audit("session_recovery", operation)
            await self._session_recovery.recover(budget)
            try:
                result = await request()
            except Exception:
                self._audit("failed", operation, recovered=True)
                raise
            self._audit("completed", operation, recovered=True)
            return result
        except Exception:
            self._audit("failed", operation)
            raise
        self._audit("completed", operation)
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

        async def send() -> ResponseT:
            prepared = await self._prepared(operation, request_options, budget)
            payload = await self._operations.send_json(prepared)
            if operation.response_type is None:
                raise TypeError(f"JSON operation {operation.name!r} has no response type")
            return decode_model(operation.response_type, payload)

        return await self._run_with_recovery(operation, send, budget)

    async def execute_stream(
        self,
        operation: OperationSpec[bytes],
        options: RequestOptions | None = None,
    ) -> bytes:
        request_options = options or RequestOptions()
        budget = self._operations.create_budget(operation)

        async def send() -> bytes:
            prepared = await self._prepared(operation, request_options, budget)
            return await self._operations.send_bytes(prepared)

        return await self._run_with_recovery(operation, send, budget)

    async def execute_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path:
        request_options = options or RequestOptions()
        budget = self._operations.create_budget(operation)
        target = FileTarget(Path(destination))

        async def send() -> Path:
            prepared = await self._prepared(operation, request_options, budget)
            return await self._operations.send_file(prepared, target)

        return await self._run_with_recovery(operation, send, budget)


__all__ = [
    "BytesTransport",
    "DefaultRequestExecutor",
    "FileTransport",
    "JsonTransport",
    "OperationExecutor",
    "Transport",
]
