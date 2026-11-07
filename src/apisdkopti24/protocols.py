"""Узкие протоколы зависимостей: их реализует ядро SDK, а используют сервисы."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, TypeVar

from .execution_budget import OperationBudget
from .modeling import ResponseModel
from .operations import OperationSpec
from .requests import RequestOptions
from .session import RequestContext, SessionSnapshot

ResponseT = TypeVar("ResponseT", bound=ResponseModel)


class JsonRequestExecutor(Protocol):
    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
    ) -> ResponseT: ...


class BytesRequestExecutor(Protocol):
    async def execute_stream(
        self,
        operation: OperationSpec[bytes],
        options: RequestOptions | None = None,
    ) -> bytes: ...


class FileRequestExecutor(Protocol):
    async def execute_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path: ...


class RequestExecutor(
    JsonRequestExecutor,
    BytesRequestExecutor,
    FileRequestExecutor,
    Protocol,
):
    """Полный интерфейс исполнителя для сервисов, использующих все виды ответов."""


class SessionContext(Protocol):
    @property
    def session_id(self) -> str | None: ...

    @property
    def contract_id(self) -> str | None: ...

    @property
    def available_contracts(self) -> tuple[tuple[str, str], ...]: ...

    def snapshot(self) -> SessionSnapshot: ...

    def request_context(self, *, contract_id: str | None = None) -> RequestContext: ...


class SessionGate(Protocol):
    async def ensure_authenticated(self, budget: OperationBudget | None = None) -> str: ...


class SessionRecovery(Protocol):
    async def recover(self, budget: OperationBudget) -> str: ...


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


__all__ = [
    "APIKeyProvider",
    "BytesRequestExecutor",
    "CredentialsProvider",
    "FileRequestExecutor",
    "JsonRequestExecutor",
    "RequestExecutor",
    "SessionContext",
    "SessionGate",
    "SessionMutator",
    "SessionRecovery",
]
