import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar, cast

from apisdkopti24.execution_budget import OperationBudget
from apisdkopti24.operations import OperationSpec
from apisdkopti24.policies import RateLimitPolicy
from apisdkopti24.requests import RequestOptions
from apisdkopti24.service_base import RequestExecutor, SessionContext, SessionGate

# Без явной частоты транспорт берёт 1 запрос/с и ждёт по-настоящему; тестам,
# которые не проверяют сам ограничитель, она не нужна.
UNTHROTTLED = RateLimitPolicy(requests_per_second=10_000.0)

ResponseT = TypeVar("ResponseT")
# Порядок аргументов конструктора доменного сервиса.
ServiceDependencies = tuple[RequestExecutor, SessionContext, SessionGate, logging.Logger]


class ManualClock:
    """Часы теста: время и паузы задаёт сам тест."""

    def __init__(
        self,
        monotonic: Callable[[], float],
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._monotonic = monotonic
        self._sleep = sleep

    def now(self) -> datetime:
        return datetime.now()

    def monotonic(self) -> float:
        return self._monotonic()

    async def sleep(self, seconds: float) -> None:
        await self._sleep(seconds)


def operation_name(operation: OperationSpec[Any] | str) -> str:
    return operation.name if isinstance(operation, OperationSpec) else operation


def typed_request_stub(function: Callable[..., Any]) -> Callable[..., Any]:
    """Адаптировать словарные заглушки к типизированным операциям SDK."""

    @wraps(function)
    async def wrapper(
        self: object,
        operation: OperationSpec[Any] | str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        options = kwargs.pop("options", None)
        if isinstance(options, RequestOptions):
            kwargs.update(
                route_name=options.route_name,
                path_params=options.path_params or None,
                contract_header=options.contract_id,
                query=dict(options.query) or None,
                form=dict(options.form) if options.form is not None else None,
                json_body=options.json_body,
            )
        payload = await function(self, operation_name(operation), *args, **kwargs)
        if isinstance(operation, OperationSpec):
            if operation.response_type is None:
                raise TypeError(f"Операция {operation.name!r} не содержит модели ответа")
            return operation.response_type.model_validate(payload)
        return payload

    return wrapper


class NoopRequestExecutor:
    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
    ) -> ResponseT:
        raise AssertionError(f"Неожиданный запрос: {operation_name(operation)}")

    async def execute_stream(
        self,
        operation: OperationSpec[bytes],
        options: RequestOptions | None = None,
    ) -> bytes:
        raise AssertionError(f"Неожиданный запрос потоковой загрузки: {options} {operation}")

    async def execute_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path:
        del destination
        raise AssertionError(f"Неожиданный запрос загрузки в файл: {options} {operation}")


class RecordingRequestExecutor:
    """Записать параметры каждого запроса и вернуть заранее заданный ответ.

    ``omit_empty`` убирает из записи пустые ``query``, ``form`` и ``json_body``.
    """

    ALWAYS_RECORDED = frozenset({"route_name", "path_params", "contract_header"})

    def __init__(self, responses: dict[str, dict[str, Any]], *, omit_empty: bool = False) -> None:
        self.responses = responses
        self.omit_empty = omit_empty
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
    ) -> ResponseT:
        request_options = options or RequestOptions()
        call = {
            "route_name": request_options.route_name,
            "path_params": request_options.path_params or None,
            "contract_header": request_options.contract_id,
            "query": dict(request_options.query) or None,
            "form": dict(request_options.form) if request_options.form is not None else None,
            "json_body": request_options.json_body,
        }
        if self.omit_empty:
            call = {
                key: value
                for key, value in call.items()
                if value is not None or key in self.ALWAYS_RECORDED
            }
        name = operation_name(operation)
        self.calls.append((name, call))
        payload = self.responses[name]
        if isinstance(operation, OperationSpec):
            assert operation.response_type is not None
            return cast(ResponseT, cast(Any, operation.response_type).model_validate(payload))
        return cast(ResponseT, payload)

    async def execute_stream(
        self,
        operation: OperationSpec[bytes],
        options: RequestOptions | None = None,
    ) -> bytes:
        del operation, options
        raise AssertionError("Неожиданный запрос потоковой загрузки")

    async def execute_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path:
        del operation, destination, options
        raise AssertionError("Неожиданный запрос загрузки в файл")


class StubSessionGate:
    async def ensure_authenticated(self, budget: OperationBudget | None = None) -> str:
        return "test-session"

    async def recover(self, budget: OperationBudget) -> str:
        del budget
        return "test-session"


class StubCredentialsProvider:
    def __init__(self, login: str = "test_user", password: str = "secret") -> None:
        self.__login = login
        self.__password = password

    def get_credentials(self) -> tuple[str, str]:
        return self.__login, self.__password


class FrozenClock:
    """Часы с фиксированным now(); монотонное время стоит на месте, sleep не ждёт."""

    def __init__(self, now: datetime = datetime(2026, 7, 19, 12, 30, 0)) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def monotonic(self) -> float:
        return 0.0

    async def sleep(self, seconds: float) -> None:
        del seconds


def service_dependencies(session_manager: SessionContext) -> ServiceDependencies:
    return (
        NoopRequestExecutor(),
        session_manager,
        StubSessionGate(),
        logging.getLogger("sdk-service-test"),
    )


class CountingSessionGate:
    """Шлюз сессии, который считает попытки входа: проверки должны идти до входа."""

    def __init__(self) -> None:
        self.calls = 0

    async def ensure_authenticated(self, budget: OperationBudget | None = None) -> str:
        self.calls += 1
        return "session-id"
