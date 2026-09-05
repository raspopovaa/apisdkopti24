import logging
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

from api_client_opti24.operations import Operation


def operation_name(operation: Operation[Any] | str) -> str:
    return operation.name if isinstance(operation, Operation) else operation


def typed_request_stub(function: Callable[..., Any]) -> Callable[..., Any]:
    """Adapt legacy dictionary stubs to typed SDK operations."""

    @wraps(function)
    async def wrapper(
        self: object,
        operation: Operation[Any] | str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        payload = await function(self, operation_name(operation), *args, **kwargs)
        if isinstance(operation, Operation):
            if operation.response_type is None:
                raise TypeError(f"Operation {operation.name!r} has no response model")
            return operation.response_type.model_validate(payload)
        return payload

    return wrapper


class NoopRequestExecutor:
    async def execute(
        self,
        operation: Operation[Any] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: object = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        del route_name, path_params, kwargs
        raise AssertionError(f"Unexpected request: {api_version} {operation_name(operation)}")

    async def execute_stream(
        self,
        operation: Operation[bytes] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: object = None,
        **kwargs: Any,
    ) -> bytes:
        del route_name, path_params, kwargs
        raise AssertionError(f"Unexpected stream request: {api_version} {operation}")

    async def execute_stream_to_file(
        self,
        operation: Operation[bytes] | str,
        destination: str | Path,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: object = None,
        **kwargs: Any,
    ) -> Path:
        del destination, route_name, path_params, kwargs
        raise AssertionError(f"Unexpected file stream request: {api_version} {operation}")


class RecordingRequestExecutor:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def execute(
        self,
        operation: Operation[Any] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: object = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        call = {
            "api_version": api_version,
            "route_name": route_name,
            "path_params": path_params,
            **kwargs,
        }
        name = operation_name(operation)
        self.calls.append((name, call))
        payload = self.responses[name]
        if isinstance(operation, Operation):
            assert operation.response_type is not None
            return operation.response_type.model_validate(payload)
        return payload

    async def execute_stream(
        self,
        operation: Operation[bytes] | str,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: object = None,
        **kwargs: Any,
    ) -> bytes:
        del operation, api_version, route_name, path_params, kwargs
        raise AssertionError("Unexpected stream request")

    async def execute_stream_to_file(
        self,
        operation: Operation[bytes] | str,
        destination: str | Path,
        *,
        api_version: str | None = None,
        route_name: str = "default",
        path_params: object = None,
        **kwargs: Any,
    ) -> Path:
        del operation, destination, api_version, route_name, path_params, kwargs
        raise AssertionError("Unexpected file stream request")


class StubSessionGate:
    async def ensure_authenticated(self) -> str:
        return "test-session"

    async def recover(self) -> str:
        return "test-session"


class StubCredentialsProvider:
    def __init__(self, login: str = "test_user", password: str = "secret") -> None:
        self.__login = login
        self.__password = password

    def get_credentials(self) -> tuple[str, str]:
        return self.__login, self.__password


class FrozenClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 19, 12, 30, 0)

    def monotonic(self) -> float:
        return 0.0

    async def sleep(self, seconds: float) -> None:
        del seconds


def service_dependencies(session_manager: object) -> tuple[object, ...]:
    return (
        NoopRequestExecutor(),
        session_manager,
        StubSessionGate(),
        logging.getLogger("sdk-service-test"),
    )
