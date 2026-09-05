from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar, overload

from .config import TimeoutPolicy
from .endpoints import EndpointSpec, RouteVariant
from .errors import NotAuthenticatedError
from .execution_budget import OperationBudget
from .logger import LoggerLike
from .modeling import ResponseModel, decode_model
from .operations import Operation
from .registry import MethodRegistry
from .response import DecodedPayload
from .runtime import Clock
from .service_base import (
    APIKeyProvider,
    JSONPayload,
    PathParams,
    SessionContext,
    SessionGate,
    SessionRecovery,
)
from .session import RequestContext
from .utils import sanitize_for_logging

ResultT = TypeVar("ResultT")
ResponseT = TypeVar("ResponseT", bound=ResponseModel)


@dataclass(frozen=True, slots=True)
class PreparedOperation(Generic[ResultT]):
    operation: Operation[ResultT] | None
    spec: EndpointSpec
    route: RouteVariant
    endpoint: str
    request_context: RequestContext
    timeout: float
    budget: OperationBudget


class Transport(Protocol):
    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> DecodedPayload: ...

    async def request_stream(
        self,
        method: str,
        endpoint: str,
        *,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> bytes: ...

    async def request_stream_to_file(
        self,
        method: str,
        endpoint: str,
        destination: str | Path,
        *,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> Path: ...

    async def aclose(self) -> None: ...


class OperationExecutor:
    def __init__(
        self,
        *,
        api_key_provider: APIKeyProvider,
        transport: Transport,
        session_context: SessionContext,
        registry: MethodRegistry,
        timeouts: TimeoutPolicy,
        logger: LoggerLike,
        clock: Clock,
        max_attempts: int = 5,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.__api_key_provider = api_key_provider
        self.__transport = transport
        self.__session_context = session_context
        self.__registry = registry
        self.__timeouts = timeouts
        self.__logger = logger
        self.__clock = clock
        self.__max_attempts = max_attempts

    def headers(
        self,
        include_session: bool = False,
        content_type_json: bool = False,
        *,
        request_context: RequestContext | None = None,
    ) -> dict[str, str]:
        api_key = self.__api_key_provider.get_api_key()
        if not api_key:
            raise ValueError("API key provider returned an empty value")
        headers = {
            "api_key": api_key,
            "date_time": self.__clock.now().strftime("%Y-%m-%d %H:%M:%S"),
            "User-Agent": "apiclientopti24",
            "Content-Type": (
                "application/json" if content_type_json else "application/x-www-form-urlencoded"
            ),
        }
        context = request_context or self.__session_context.request_context()
        if include_session and context.session_id:
            headers["session_id"] = context.session_id
            if context.contract_id:
                headers["contract_id"] = context.contract_id
        self.__logger.debug("Prepared headers: %s", sanitize_for_logging(headers))
        return headers

    def resolve(
        self,
        operation_name: str,
        *,
        api_version: str | None,
        route_name: str,
    ) -> tuple[EndpointSpec, RouteVariant]:
        spec = self.__registry.get(operation_name)
        route = spec.resolve_route(api_version=api_version, route_name=route_name)
        return spec, route

    def create_budget(self, spec: EndpointSpec) -> OperationBudget:
        return OperationBudget(
            deadline_at=self.__clock.monotonic()
            + self.__timeouts.resolve_total(spec.timeout_class),
            max_attempts=self.__max_attempts,
        )

    def prepare(
        self,
        operation: Operation[ResultT] | None,
        spec: EndpointSpec,
        route: RouteVariant,
        *,
        path_params: PathParams | None,
        request_context: RequestContext,
        budget: OperationBudget,
    ) -> PreparedOperation[ResultT]:
        return PreparedOperation(
            operation=operation,
            spec=spec,
            route=route,
            endpoint=route.render(path_params),
            request_context=request_context,
            timeout=self.__timeouts.resolve(spec.timeout_class),
            budget=budget,
        )

    def _request_headers(
        self,
        prepared: PreparedOperation[Any],
        kwargs: dict[str, Any],
    ) -> dict[str, str]:
        custom_headers = kwargs.pop("headers", None)
        if custom_headers is not None and not isinstance(custom_headers, Mapping):
            raise TypeError("headers must be a mapping of strings")
        headers = self.headers(
            include_session=prepared.spec.requires_session,
            content_type_json="json" in kwargs,
            request_context=prepared.request_context,
        )
        for name, value in dict(custom_headers or {}).items():
            normalized_name = name.lower().replace("-", "_")
            if normalized_name in {"api_key", "session_id", "date_time"}:
                raise ValueError(f"Header override is not allowed: {name}")
            headers[name] = value
        return headers

    async def _request_json(
        self,
        prepared: PreparedOperation[Any],
        kwargs: dict[str, Any],
    ) -> JSONPayload:
        result = await self.__transport.request(
            prepared.route.http_method,
            prepared.endpoint,
            api_version=prepared.route.api_version,
            headers=self._request_headers(prepared, kwargs),
            timeout=prepared.timeout,
            method_name=prepared.spec.name,
            retry_class=prepared.spec.retry_class,
            idempotent=prepared.spec.idempotent,
            operation_budget=prepared.budget,
            **kwargs,
        )
        if not isinstance(result, dict):
            self.__logger.error(
                "Unexpected API response operation=%s response_type=%s",
                prepared.spec.name,
                type(result).__name__,
            )
            raise TypeError("Expected API response to be a JSON object")
        self.__logger.debug("Received response type: %s", type(result).__name__)
        return result

    async def execute_prepared(
        self,
        prepared: PreparedOperation[Any],
        **kwargs: Any,
    ) -> JSONPayload:
        self.__logger.debug(
            "Preparing API request operation=%s version=%s route=%s",
            prepared.spec.name,
            prepared.route.api_version,
            prepared.route.name,
        )
        return await self._request_json(prepared, dict(kwargs))

    @overload
    async def execute(
        self,
        operation: Operation[ResponseT],
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> ResponseT: ...

    @overload
    async def execute(
        self,
        operation: str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> JSONPayload: ...

    async def execute(
        self,
        operation: Operation[ResponseT] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> ResponseT | JSONPayload:
        operation_name = operation.name if isinstance(operation, Operation) else operation
        spec, route = self.resolve(
            operation_name,
            api_version=api_version,
            route_name=route_name,
        )
        prepared: PreparedOperation[Any] = self.prepare(
            operation if isinstance(operation, Operation) else None,
            spec,
            route,
            path_params=path_params,
            request_context=self.__session_context.request_context(contract_id=request_contract_id),
            budget=self.create_budget(spec),
        )
        payload = await self.execute_prepared(prepared, **kwargs)
        if not isinstance(operation, Operation):
            return payload
        if operation.response_type is None:
            raise TypeError(f"JSON operation {operation.name!r} has no response type")
        return decode_model(operation.response_type, payload)

    async def _request_bytes(
        self,
        prepared: PreparedOperation[Any],
        kwargs: dict[str, Any],
    ) -> bytes:
        return await self.__transport.request_stream(
            prepared.route.http_method,
            prepared.endpoint,
            api_version=prepared.route.api_version,
            headers=self._request_headers(prepared, kwargs),
            timeout=prepared.timeout,
            method_name=prepared.spec.name,
            retry_class=prepared.spec.retry_class,
            idempotent=prepared.spec.idempotent,
            operation_budget=prepared.budget,
            **kwargs,
        )

    async def execute_stream_prepared(
        self,
        prepared: PreparedOperation[bytes],
        **kwargs: Any,
    ) -> bytes:
        return await self._request_bytes(prepared, dict(kwargs))

    async def execute_stream_to_file_prepared(
        self,
        prepared: PreparedOperation[bytes],
        destination: str | Path,
        **kwargs: Any,
    ) -> Path:
        return await self.__transport.request_stream_to_file(
            prepared.route.http_method,
            prepared.endpoint,
            destination,
            api_version=prepared.route.api_version,
            headers=self._request_headers(prepared, kwargs),
            timeout=prepared.timeout,
            method_name=prepared.spec.name,
            retry_class=prepared.spec.retry_class,
            idempotent=prepared.spec.idempotent,
            operation_budget=prepared.budget,
            **kwargs,
        )


class DefaultRequestExecutor:
    def __init__(
        self,
        *,
        operation_executor: OperationExecutor,
        session_gate: SessionGate,
        session_recovery: SessionRecovery,
        session_context: SessionContext,
        logger: LoggerLike,
    ) -> None:
        self.__operation_executor = operation_executor
        self.__session_gate = session_gate
        self.__session_recovery = session_recovery
        self.__session_context = session_context
        self.__logger = logger

    def headers(
        self,
        include_session: bool = False,
        content_type_json: bool = False,
    ) -> dict[str, str]:
        return self.__operation_executor.headers(
            include_session=include_session,
            content_type_json=content_type_json,
        )

    @staticmethod
    def _operation_name(operation: Operation[Any] | str) -> str:
        return operation.name if isinstance(operation, Operation) else operation

    def _prepare(
        self,
        operation: Operation[ResultT] | str,
        spec: EndpointSpec,
        route: RouteVariant,
        *,
        path_params: PathParams | None,
        request_contract_id: str | None,
        budget: OperationBudget,
    ) -> PreparedOperation[ResultT]:
        typed_operation = operation if isinstance(operation, Operation) else None
        return self.__operation_executor.prepare(
            typed_operation,
            spec,
            route,
            path_params=path_params,
            request_context=self.__session_context.request_context(contract_id=request_contract_id),
            budget=budget,
        )

    def _audit(
        self,
        event: str,
        spec: EndpointSpec,
        route: RouteVariant,
        *,
        recovered: bool = False,
    ) -> None:
        self.__logger.info(
            "API request audit",
            extra={
                "request_audit": True,
                "event": event,
                "operation": spec.name,
                "api_version": route.api_version,
                "route_name": route.name,
                "http_method": route.http_method,
                "recovered": recovered,
            },
        )

    async def _run_with_recovery(
        self,
        spec: EndpointSpec,
        route: RouteVariant,
        request: Callable[[], Awaitable[ResultT]],
    ) -> ResultT:
        self._audit("started", spec, route)
        try:
            result = await request()
        except NotAuthenticatedError:
            if not spec.requires_session:
                self._audit("failed", spec, route)
                raise
            self._audit("session_recovery", spec, route)
            await self.__session_recovery.recover()
            try:
                result = await request()
            except Exception:
                self._audit("failed", spec, route, recovered=True)
                raise
            self._audit("completed", spec, route, recovered=True)
            return result
        except Exception:
            self._audit("failed", spec, route)
            raise
        self._audit("completed", spec, route)
        return result

    @overload
    async def execute(
        self,
        operation: Operation[ResponseT],
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> ResponseT: ...

    @overload
    async def execute(
        self,
        operation: str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> JSONPayload: ...

    async def execute(
        self,
        operation: Operation[ResponseT] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> ResponseT | JSONPayload:
        operation_name = self._operation_name(operation)
        spec, route = self.__operation_executor.resolve(
            operation_name, api_version=api_version, route_name=route_name
        )
        budget = self.__operation_executor.create_budget(spec)
        if spec.requires_session:
            await self.__session_gate.ensure_authenticated()
        raw = await self._run_with_recovery(
            spec,
            route,
            lambda: self.__operation_executor.execute_prepared(
                self._prepare(
                    operation,
                    spec,
                    route,
                    path_params=path_params,
                    request_contract_id=request_contract_id,
                    budget=budget,
                ),
                **kwargs,
            ),
        )
        if not isinstance(operation, Operation):
            return raw
        if operation.response_type is None:
            raise TypeError(f"JSON operation {operation.name!r} has no response type")
        return decode_model(operation.response_type, raw)

    async def execute_stream(
        self,
        operation: Operation[bytes] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> bytes:
        operation_name = self._operation_name(operation)
        spec, route = self.__operation_executor.resolve(
            operation_name, api_version=api_version, route_name=route_name
        )
        budget = self.__operation_executor.create_budget(spec)
        if spec.requires_session:
            await self.__session_gate.ensure_authenticated()
        return await self._run_with_recovery(
            spec,
            route,
            lambda: self.__operation_executor.execute_stream_prepared(
                self._prepare(
                    operation,
                    spec,
                    route,
                    path_params=path_params,
                    request_contract_id=request_contract_id,
                    budget=budget,
                ),
                **kwargs,
            ),
        )

    async def execute_stream_to_file(
        self,
        operation: Operation[bytes] | str,
        destination: str | Path,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> Path:
        operation_name = self._operation_name(operation)
        spec, route = self.__operation_executor.resolve(
            operation_name, api_version=api_version, route_name=route_name
        )
        budget = self.__operation_executor.create_budget(spec)
        if spec.requires_session:
            await self.__session_gate.ensure_authenticated()
        return await self._run_with_recovery(
            spec,
            route,
            lambda: self.__operation_executor.execute_stream_to_file_prepared(
                self._prepare(
                    operation,
                    spec,
                    route,
                    path_params=path_params,
                    request_contract_id=request_contract_id,
                    budget=budget,
                ),
                destination,
                **kwargs,
            ),
        )
