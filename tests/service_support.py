import logging
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

from apisdkopti24.operations import Operation
from apisdkopti24.requests import RequestOptions


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
        options = kwargs.pop("options", None)
        if isinstance(options, RequestOptions):
            kwargs.update(
                api_version=options.api_version,
                route_name=options.route_name,
                path_params=options.path_params or None,
                request_contract_id=options.contract_id,
                params=dict(options.query) or None,
                data=dict(options.form) if options.form is not None else None,
                json=options.json_body,
            )
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
        operation: Operation[Any],
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        raise AssertionError(
            f"Unexpected request: {(options or RequestOptions()).api_version} "
            f"{operation_name(operation)}"
        )

    async def execute_stream(
        self,
        operation: Operation[bytes],
        options: RequestOptions | None = None,
    ) -> bytes:
        raise AssertionError(f"Unexpected stream request: {options} {operation}")

    async def execute_stream_to_file(
        self,
        operation: Operation[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path:
        del destination
        raise AssertionError(f"Unexpected file stream request: {options} {operation}")


class RecordingRequestExecutor:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def execute(
        self,
        operation: Operation[Any],
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        request_options = options or RequestOptions()
        call = {
            "api_version": request_options.api_version,
            "route_name": request_options.route_name,
            "path_params": request_options.path_params or None,
            "request_contract_id": request_options.contract_id,
            "params": dict(request_options.query) or None,
            "data": dict(request_options.form) if request_options.form is not None else None,
            "json": request_options.json_body,
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
        operation: Operation[bytes],
        options: RequestOptions | None = None,
    ) -> bytes:
        del operation, options
        raise AssertionError("Unexpected stream request")

    async def execute_stream_to_file(
        self,
        operation: Operation[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path:
        del operation, destination, options
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
