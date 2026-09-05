import asyncio
import logging
from datetime import datetime
from typing import Any

import pytest

from api_client_opti24.authentication import (
    AuthenticationCoordinator,
    DefaultAuthenticator,
)
from api_client_opti24.config import TimeoutPolicy
from api_client_opti24.credentials import StaticAPIKeyProvider
from api_client_opti24.errors import NotAuthenticatedError
from api_client_opti24.executor import DefaultRequestExecutor, OperationExecutor
from api_client_opti24.registry import build_default_registry
from api_client_opti24.response import DecodedPayload
from api_client_opti24.session import SessionManager


class StubTransport:
    def __init__(self, *responses: DecodedPayload | Exception) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str, str, dict[str, Any]]] = []

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> DecodedPayload:
        self.calls.append((method, endpoint, api_version, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    async def request_stream(
        self,
        method: str,
        endpoint: str,
        *,
        api_version: str = "v1",
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> bytes:
        self.calls.append((method, endpoint, api_version, {"headers": headers, **kwargs}))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        assert isinstance(response, bytes)
        return response

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


@pytest.mark.asyncio
async def test_executor_builds_headers_and_rejects_non_object_json() -> None:
    session = SessionManager()
    session.mark_authenticated("session-1", "contract-1")
    executor, _ = build_executor(StubTransport([]), session)

    assert executor.headers(include_session=True) == {
        "api_key": "secret-key",
        "date_time": "2026-07-19 12:30:00",
        "User-Agent": "apiclientopti24",
        "Content-Type": "application/x-www-form-urlencoded",
        "session_id": "session-1",
        "contract_id": "contract-1",
    }
    with pytest.raises(TypeError, match="JSON object"):
        await executor.execute("get_cards_v2")


@pytest.mark.asyncio
async def test_executor_allows_contract_override_but_protects_credentials() -> None:
    session = SessionManager()
    session.mark_authenticated("session-1", "default-contract")
    transport = StubTransport({"status": {"code": 200}, "data": {}})
    executor, _ = build_executor(transport, session)

    await executor.execute(
        "get_documents",
        headers={"contract_id": "explicit-contract"},
        params={"date_start": "2026-01-01", "date_end": "2026-01-31"},
    )

    assert transport.calls[0][3]["headers"]["contract_id"] == "explicit-contract"
    with pytest.raises(ValueError, match="not allowed"):
        await executor.execute("get_documents", headers={"api_key": "replaced"})


@pytest.mark.asyncio
async def test_executor_resolves_and_escapes_operation_path() -> None:
    transport = StubTransport({"status": {"code": 200}, "data": {}})
    executor, _ = build_executor(transport)

    await executor.execute(
        "get_card_drivers",
        path_params={"card_id": "карта 1"},
    )

    method, endpoint, version, _ = transport.calls[0]
    assert method == "GET"
    assert endpoint == "cards/%D0%BA%D0%B0%D1%80%D1%82%D0%B0%201/drivers"
    assert version == "v2"


@pytest.mark.asyncio
@pytest.mark.parametrize("unsafe_value", ["..", "../admin", "card/other", "card?admin=1"])
async def test_executor_rejects_unsafe_path_segments(unsafe_value: str) -> None:
    executor, _ = build_executor(StubTransport({"status": {"code": 200}}))

    with pytest.raises(ValueError, match="Unsafe path parameter"):
        await executor.execute(
            "get_card_drivers",
            path_params={"card_id": unsafe_value},
        )


@pytest.mark.asyncio
async def test_executor_recovers_protected_operation_once() -> None:
    transport = StubTransport(
        NotAuthenticatedError(401, "expired"),
        {"status": {"code": 200}, "data": {}},
    )
    executor, controller = build_executor(transport)

    await executor.execute("get_cards_v2")

    assert controller.ensure_calls == 1
    assert controller.recover_calls == 1
    assert transport.calls[1][3]["headers"]["session_id"] == "recovered-session"


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
        StubTransport({"status": {"code": 200}, "data": {}}),
        logger=audit_logger,
    )

    await executor.execute("get_card_drivers", path_params={"card_id": "secret-card-id"})

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    assert [record.event for record in audit_records] == ["started", "completed"]
    assert all(record.operation == "get_card_drivers" for record in audit_records)
    assert all(not hasattr(record, "endpoint") for record in audit_records)


@pytest.mark.asyncio
async def test_auth_operation_never_starts_recursive_recovery() -> None:
    transport = StubTransport(NotAuthenticatedError(401, "invalid credentials"))
    executor, controller = build_executor(transport)

    with pytest.raises(NotAuthenticatedError):
        await executor.execute("auth_user")

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
        await asyncio.wait_for(executor.execute("get_cards_v2"), timeout=0.1)


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

    assert operation_executor.headers()["api_key"] == "first-key"
    provider.value = "rotated-key"
    assert operation_executor.headers()["api_key"] == "rotated-key"
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
