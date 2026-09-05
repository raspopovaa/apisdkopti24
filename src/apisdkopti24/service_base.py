from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol, TypeAlias, TypeVar, overload

from .logger import LoggerLike
from .modeling import ResponseModel
from .operations import Operation
from .session import RequestContext, SessionSnapshot
from .validation import require_identifier

JSONPayload: TypeAlias = dict[str, Any]
PathParams: TypeAlias = Mapping[str, str | int]
ResponseT = TypeVar("ResponseT", bound=ResponseModel)


class RequestExecutor(Protocol):
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

    async def execute_stream(
        self,
        operation: Operation[bytes] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> bytes: ...

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
    ) -> Path: ...


class SessionContext(Protocol):
    @property
    def session_id(self) -> str | None: ...

    @property
    def contract_id(self) -> str | None: ...

    def snapshot(self) -> SessionSnapshot: ...

    def request_context(self, *, contract_id: str | None = None) -> RequestContext: ...


class SessionGate(Protocol):
    async def ensure_authenticated(self) -> str: ...


class SessionRecovery(Protocol):
    async def recover(self) -> str: ...


class SessionMutator(SessionContext, Protocol):
    def mark_authenticated(
        self,
        session_id: str,
        contract_id: str | None = None,
    ) -> None: ...

    def set_contract(self, contract_id: str | None) -> None: ...

    def invalidate(self) -> None: ...

    def reset(self) -> None: ...


class CredentialsProvider(Protocol):
    def get_credentials(self) -> tuple[str, str]: ...


class APIKeyProvider(Protocol):
    def get_api_key(self) -> str: ...


class _BaseService:
    def __init__(
        self,
        request_executor: RequestExecutor,
        session_context: SessionContext,
        session_gate: SessionGate,
        logger: LoggerLike,
    ) -> None:
        self.__request_executor = request_executor
        self.__session_context = session_context
        self.__session_gate = session_gate
        self.__logger = logger

    @property
    def logger(self) -> LoggerLike:
        return self.__logger

    @property
    def contract_id(self) -> str | None:
        return self.__session_context.contract_id

    async def _resolve_contract_id(self, contract_id: str | None) -> str:
        if contract_id is not None:
            return require_identifier(contract_id, "contract_id")
        await self.__session_gate.ensure_authenticated()
        if self.__session_context.contract_id is None:
            raise ValueError("contract_id is required when no default contract is selected")
        return require_identifier(self.__session_context.contract_id, "contract_id")

    async def _resolve_batch_contract_id(
        self,
        *,
        contract_id: str | None,
        item_contract_ids: Sequence[str | None],
    ) -> str:
        """Resolve one contract for a batch and reject mixed contract payloads."""
        normalized_explicit = (
            require_identifier(contract_id, "contract_id") if contract_id is not None else None
        )
        normalized_items = {
            require_identifier(item_contract_id, "contract_id")
            for item_contract_id in item_contract_ids
            if item_contract_id is not None
        }
        if normalized_explicit is not None:
            conflicting = normalized_items - {normalized_explicit}
            if conflicting:
                raise ValueError("batch items must use the same contract_id as the request")
            return normalized_explicit
        if len(normalized_items) > 1:
            raise ValueError("batch items must use the same contract_id")
        if normalized_items:
            return next(iter(normalized_items))
        return await self._resolve_contract_id(None)

    @overload
    async def _request(
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
    async def _request(
        self,
        operation: str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> JSONPayload: ...

    async def _request(
        self,
        operation: Operation[ResponseT] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> ResponseT | JSONPayload:
        return await self.__request_executor.execute(
            operation,
            api_version=api_version,
            route_name=route_name,
            path_params=path_params,
            request_contract_id=request_contract_id,
            **kwargs,
        )

    async def _request_stream(
        self,
        operation: Operation[bytes] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        request_contract_id: str | None = None,
        **kwargs: Any,
    ) -> bytes:
        return await self.__request_executor.execute_stream(
            operation,
            api_version=api_version,
            route_name=route_name,
            path_params=path_params,
            request_contract_id=request_contract_id,
            **kwargs,
        )

    async def _request_stream_to_file(
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
        return await self.__request_executor.execute_stream_to_file(
            operation,
            destination,
            api_version=api_version,
            route_name=route_name,
            path_params=path_params,
            request_contract_id=request_contract_id,
            **kwargs,
        )
