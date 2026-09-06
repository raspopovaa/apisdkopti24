import asyncio
import logging
from datetime import datetime
from pathlib import Path

import pytest

from apisdkopti24.authentication import (
    AuthenticationCoordinator,
    DefaultAuthenticator,
)
from apisdkopti24.config import TimeoutPolicy
from apisdkopti24.credentials import StaticAPIKeyProvider
from apisdkopti24.errors import NotAuthenticatedError
from apisdkopti24.executor import DefaultRequestExecutor, OperationExecutor
from apisdkopti24.registry import build_default_registry
from apisdkopti24.requests import FileTarget, PreparedRequest, RequestOptions
from apisdkopti24.response import DecodedPayload
from apisdkopti24.session import SessionManager

LIST_RESPONSE = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}


class StubTransport:
    def __init__(self, *responses: DecodedPayload | Exception) -> None:
        self.responses = list(responses)
        self.calls: list[PreparedRequest] = []

    async def request(
        self,
        request: PreparedRequest,
    ) -> DecodedPayload:
        self.calls.append(request)
        response = (
            self.responses[0]
            if len(self.responses) == 1 and isinstance(self.responses[0], Exception)
            else self.responses.pop(0)
        )
        if isinstance(response, Exception):
            raise response
        return response

    async def request_stream(
        self,
        request: PreparedRequest,
    ) -> bytes:
        self.calls.append(request)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        assert isinstance(response, bytes)
        return response

    async def request_stream_to_file(self, request: PreparedRequest, target: FileTarget) -> Path:
        self.calls.append(request)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        assert isinstance(response, bytes)
        target.path.write_bytes(response)
        return target.path

    async def aclose(self) -> None:
        return None


class FrozenClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 19, 12, 30, 0)

    def monotonic(self) -> float:
        return 0.0

    async def sleep(self, seconds: float) -> None:
        del seconds


class SessionController:
    def __init__(self, session: SessionManager) -> None:
        self.session = session
        self.ensure_calls = 0
        self.recover_calls = 0

    async def ensure_authenticated(self) -> str:
        self.ensure_calls += 1
        if not self.session.session_id:
            self.session.mark_authenticated("initial-session", "contract-1")
        assert self.session.session_id is not None
        return self.session.session_id

    async def recover(self) -> str:
        self.recover_calls += 1
        self.session.mark_authenticated("recovered-session", "contract-1")
        return "recovered-session"


def build_executor(
    transport: StubTransport,
    session: SessionManager | None = None,
    logger: logging.Logger | None = None,
) -> tuple[DefaultRequestExecutor, SessionController]:
    active_session = session or SessionManager()
    controller = SessionController(active_session)
    registry = build_default_registry()
    active_logger = logger or logging.getLogger("test-executor")
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=transport,
        session_context=active_session,
        registry=registry,
        timeouts=TimeoutPolicy(),
        logger=active_logger,
        clock=FrozenClock(),
    )
    return (
        DefaultRequestExecutor(
            operation_executor=operation_executor,
            session_gate=controller,
            session_recovery=controller,
            session_context=active_session,
            logger=active_logger,
        ),
        controller,
    )


def op(name: str):
    return build_default_registry().get(name)


@pytest.mark.asyncio
async def test_executor_builds_headers_and_rejects_non_object_json() -> None:
    session = SessionManager()
    session.mark_authenticated("session-1", "contract-1")
    transport = StubTransport(LIST_RESPONSE)
    executor, _ = build_executor(transport, session)
    await executor.execute(op("get_cards_v2"))

    assert transport.calls[0].headers == {
        "api_key": "secret-key",
        "date_time": "2026-07-19 12:30:00",
        "User-Agent": "apisdkopti24",
        "Content-Type": "application/x-www-form-urlencoded",
        "session_id": "session-1",
        "contract_id": "contract-1",
    }


@pytest.mark.asyncio
async def test_executor_allows_contract_override_but_protects_credentials() -> None:
    session = SessionManager()
    session.mark_authenticated("session-1", "default-contract")
    transport = StubTransport(LIST_RESPONSE)
    executor, _ = build_executor(transport, session)

    await executor.execute(
        op("get_documents"),
        RequestOptions(
            contract_id="explicit-contract",
            query={"date_start": "2026-01-01", "date_end": "2026-01-31"},
        ),
    )

    assert transport.calls[0].headers["contract_id"] == "explicit-contract"
    with pytest.raises(ValueError, match="not allowed"):
        await executor.execute(op("get_documents"), RequestOptions(headers={"api_key": "replaced"}))


@pytest.mark.asyncio
async def test_executor_resolves_and_escapes_operation_path() -> None:
    transport = StubTransport(LIST_RESPONSE)
    executor, _ = build_executor(transport)

    await executor.execute(
        op("get_card_drivers"),
        RequestOptions(path_params={"card_id": "карта 1"}),
    )

    request = transport.calls[0]
    assert request.method == "GET"
    assert request.endpoint == "cards/%D0%BA%D0%B0%D1%80%D1%82%D0%B0%201/drivers"
    assert request.api_version == "v2"


@pytest.mark.asyncio
@pytest.mark.parametrize("unsafe_value", ["..", "../admin", "card/other", "card?admin=1"])
async def test_executor_rejects_unsafe_path_segments(unsafe_value: str) -> None:
    executor, _ = build_executor(StubTransport(LIST_RESPONSE))

    with pytest.raises(ValueError, match="Unsafe path parameter"):
        await executor.execute(
            op("get_card_drivers"),
            RequestOptions(path_params={"card_id": unsafe_value}),
        )


@pytest.mark.asyncio
async def test_executor_recovers_protected_operation_once() -> None:
    transport = StubTransport(
        NotAuthenticatedError(401, "expired"),
        LIST_RESPONSE,
    )
    executor, controller = build_executor(transport)

    await executor.execute(op("get_cards_v2"))

    assert controller.ensure_calls == 2
    assert controller.recover_calls == 1
    assert transport.calls[1].headers["session_id"] == "recovered-session"


@pytest.mark.asyncio
async def test_executor_emits_structured_audit_events_without_endpoint_values() -> None:
    records: list[logging.LogRecord] = []

    class CapturingHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    audit_logger = logging.getLogger("test-executor-audit")
    audit_logger.handlers.clear()
    audit_logger.propagate = False
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(CapturingHandler())
    executor, _ = build_executor(
        StubTransport(LIST_RESPONSE),
        logger=audit_logger,
    )

    await executor.execute(
        op("get_card_drivers"), RequestOptions(path_params={"card_id": "secret-card-id"})
    )

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    assert [record.event for record in audit_records] == ["started", "completed"]
    assert all(record.operation == "get_card_drivers" for record in audit_records)
    assert all(not hasattr(record, "endpoint") for record in audit_records)


@pytest.mark.asyncio
async def test_auth_operation_never_starts_recursive_recovery() -> None:
    transport = StubTransport(
        *(NotAuthenticatedError(401, "invalid credentials") for _ in range(10))
    )
    executor, controller = build_executor(transport)

    with pytest.raises(NotAuthenticatedError):
        await executor.execute(op("auth_user"))

    assert controller.ensure_calls == 0
    assert controller.recover_calls == 0
    assert len(transport.calls) == 1


@pytest.mark.asyncio
async def test_failed_authentication_releases_real_session_lock() -> None:
    session = SessionManager()
    transport = StubTransport(NotAuthenticatedError(401, "invalid credentials"))
    registry = build_default_registry()
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=transport,
        session_context=session,
        registry=registry,
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("test-auth-deadlock"),
        clock=FrozenClock(),
    )

    class Credentials:
        def get_credentials(self) -> tuple[str, str]:
            return "invalid-login", "invalid-password"

    authenticator = DefaultAuthenticator(
        operation_executor,
        session,
        Credentials(),
        logging.getLogger("test-auth-deadlock"),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)
    executor = DefaultRequestExecutor(
        operation_executor=operation_executor,
        session_gate=coordinator,
        session_recovery=coordinator,
        session_context=session,
        logger=logging.getLogger("test-auth-deadlock"),
    )

    with pytest.raises(NotAuthenticatedError):
        await asyncio.wait_for(executor.execute(op("get_cards_v2")), timeout=0.1)


def test_executor_resolves_api_key_for_every_request() -> None:
    class RotatingAPIKeyProvider:
        def __init__(self) -> None:
            self.value = "first-key"

        def get_api_key(self) -> str:
            return self.value

    provider = RotatingAPIKeyProvider()
    operation_executor = OperationExecutor(
        api_key_provider=provider,
        transport=StubTransport(),
        session_context=SessionManager(),
        registry=build_default_registry(),
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("test-dynamic-api-key"),
        clock=FrozenClock(),
    )

    options = RequestOptions()
    assert operation_executor._headers(op("auth_user"), options)["api_key"] == "first-key"
    provider.value = "rotated-key"
    assert operation_executor._headers(op("auth_user"), options)["api_key"] == "rotated-key"
    assert "first-key" not in repr(vars(operation_executor))


def test_executor_uses_configured_operation_attempt_budget() -> None:
    registry = build_default_registry()
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=StubTransport(),
        session_context=SessionManager(),
        registry=registry,
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("test-operation-budget"),
        clock=FrozenClock(),
        max_attempts=2,
    )

    budget = operation_executor.create_budget(registry.get("get_cards_v2"))

    assert budget.max_attempts == 2
    with pytest.raises(ValueError, match="max_attempts"):
        OperationExecutor(
            api_key_provider=StaticAPIKeyProvider("secret-key"),
            transport=StubTransport(),
            session_context=SessionManager(),
            registry=registry,
            timeouts=TimeoutPolicy(),
            logger=logging.getLogger("test-invalid-operation-budget"),
            clock=FrozenClock(),
            max_attempts=0,
        )
