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
from apisdkopti24.execution_budget import OperationBudget, OperationTimeoutError
from apisdkopti24.executor import DefaultRequestExecutor, OperationExecutor
from apisdkopti24.registry import build_default_registry
from apisdkopti24.requests import FileTarget, PreparedRequest, RequestOptions
from apisdkopti24.response import DecodedPayload
from apisdkopti24.session import SessionManager

LIST_RESPONSE = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
AUTH_RESPONSE = {
    "status": {"code": 200},
    "data": {
        "session_id": "session-id",
        "client_id": "client-id",
        "client_status": "active",
        "org_name": "Test organization",
        "user_id": "user-id",
        "contracts": [
            {
                "id": "contract-a",
                "number": "A-001",
                "mpc": False,
                "cards_count": 1,
                "one_price": False,
            },
            {
                "id": "contract-b",
                "number": "B-001",
                "mpc": False,
                "cards_count": 1,
                "one_price": False,
            },
        ],
        "role_id": "Supervisor",
        "role_name": "Administrator",
        "access": {"web": True, "api": True, "mobile": True},
        "email": "user@example.test",
        "read_only": False,
    },
    "timestamp": 1710000000,
}


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

    async def recover(self, budget: OperationBudget) -> str:
        del budget
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
    active_logger = logger or logging.getLogger("test-executor")
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=transport,
        session_context=active_session,
        timeouts=TimeoutPolicy(),
        logger=active_logger,
        clock=FrozenClock(),
    )
    return (
        DefaultRequestExecutor(
            operation_executor=operation_executor,
            session_gate=controller,
            session_recovery=controller,
            logger=active_logger,
            clock=FrozenClock(),
        ),
        controller,
    )


def op(name: str):
    return build_default_registry().get(name)


def capturing_audit_logger(name: str) -> tuple[logging.Logger, list[logging.LogRecord]]:
    records: list[logging.LogRecord] = []

    class CapturingHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    audit_logger = logging.getLogger(name)
    audit_logger.handlers.clear()
    audit_logger.propagate = False
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(CapturingHandler())
    return audit_logger, records


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
    for header_name in ("api_key", "session-id", "contract_id", "Content-Type"):
        with pytest.raises(ValueError, match="запрещено"):
            await executor.execute(
                op("get_documents"),
                RequestOptions(headers={header_name: "replaced"}),
            )


def test_preview_headers_redacts_sensitive_values() -> None:
    session = SessionManager()
    session.mark_authenticated("session-1", "contract-1")
    executor, _ = build_executor(StubTransport(LIST_RESPONSE), session)

    headers = executor.preview_headers(op("get_cards_v2"))

    assert headers["api_key"] == "***"
    assert headers["session_id"] == "***"
    assert headers["contract_id"] == "***"
    assert "secret-key" not in repr(headers)
    assert "session-1" not in repr(headers)
    assert "contract-1" not in repr(headers)


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

    with pytest.raises(ValueError, match="Небезопасный параметр пути"):
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
async def test_executor_passes_business_budget_to_session_recovery() -> None:
    session = SessionManager()
    session.mark_authenticated("expired-session", "contract-1")
    transport = StubTransport(NotAuthenticatedError(401, "expired"), LIST_RESPONSE)
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=transport,
        session_context=session,
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("test-shared-recovery-budget"),
        clock=FrozenClock(),
    )

    class Recovery:
        def __init__(self) -> None:
            self.budget: OperationBudget | None = None

        async def ensure_authenticated(self) -> str:
            assert session.session_id is not None
            return session.session_id

        async def recover(self, budget: OperationBudget) -> str:
            self.budget = budget
            session.mark_authenticated("recovered-session", "contract-1")
            return "recovered-session"

    recovery = Recovery()
    executor = DefaultRequestExecutor(
        operation_executor=operation_executor,
        session_gate=recovery,
        session_recovery=recovery,
        logger=logging.getLogger("test-shared-recovery-budget"),
        clock=FrozenClock(),
    )

    await executor.execute(op("get_cards_v2"))

    assert recovery.budget is transport.calls[0].operation_budget
    assert transport.calls[1].operation_budget is recovery.budget


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
    assert len({record.operation_id for record in audit_records}) == 1
    assert audit_records[-1].elapsed_ms == 0.0
    assert audit_records[-1].attempts_used == 0


@pytest.mark.asyncio
async def test_executor_does_not_audit_unvalidated_route_values() -> None:
    audit_logger, records = capturing_audit_logger("test-invalid-route-audit")
    executor, _ = build_executor(StubTransport(LIST_RESPONSE), logger=audit_logger)
    secret = "secret-route-value"

    with pytest.raises(ValueError, match="не имеет однозначного маршрута"):
        await executor.execute(
            op("get_cards_v2"),
            RequestOptions(api_version=secret, route_name=secret),
        )

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    assert [record.event for record in audit_records] == ["started", "failed"]
    assert all(record.api_version == "invalid" for record in audit_records)
    assert all(record.route_name == "invalid" for record in audit_records)
    assert secret not in " ".join(record.getMessage() for record in audit_records)


@pytest.mark.asyncio
async def test_executor_audit_describes_api_error_with_safe_codes_and_message() -> None:
    audit_logger, records = capturing_audit_logger("test-executor-api-error-audit")
    error = NotAuthenticatedError(
        401,
        "Необходима авторизация",
        http_status_code=200,
        api_status_code=401,
        error_type="notAuthenticated",
        method_name="auth_user",
    )
    executor, _ = build_executor(StubTransport(error), logger=audit_logger)

    with pytest.raises(NotAuthenticatedError):
        await executor.execute(op("auth_user"))

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    failed = audit_records[-1]
    assert [record.event for record in audit_records] == ["started", "failed"]
    assert failed.sdk_error_code == "api_not_authenticated"
    assert failed.error_source == "api"
    assert failed.exception_type == "NotAuthenticatedError"
    assert failed.error_message == "Необходима авторизация"
    assert failed.http_status_code == 200
    assert failed.api_status_code == 401
    assert failed.api_error_type == "notAuthenticated"
    assert failed.retryable is False
    assert failed.transient is False
    assert failed.retry_allowed is False
    assert failed.levelno == logging.WARNING


@pytest.mark.asyncio
async def test_executor_audit_describes_local_timeout_without_fake_http_code() -> None:
    audit_logger, records = capturing_audit_logger("test-executor-timeout-audit")
    executor, _ = build_executor(
        StubTransport(OperationTimeoutError("Превышен общий лимит времени операции")),
        logger=audit_logger,
    )

    with pytest.raises(OperationTimeoutError):
        await executor.execute(op("auth_user"))

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    failed = audit_records[-1]
    assert [record.event for record in audit_records] == ["started", "failed"]
    assert failed.sdk_error_code == "operation_timeout"
    assert failed.error_source == "sdk"
    assert failed.exception_type == "OperationTimeoutError"
    assert failed.error_message == "Превышен общий лимит времени операции"
    assert failed.http_status_code is None
    assert failed.api_status_code is None
    assert failed.retryable is True
    assert failed.transient is True
    assert failed.retry_allowed is True


@pytest.mark.asyncio
async def test_executor_audit_records_cancellation_and_propagates_it() -> None:
    audit_logger, records = capturing_audit_logger("test-executor-cancelled-audit")

    class CancellingTransport(StubTransport):
        async def request(self, request: PreparedRequest) -> DecodedPayload:
            self.calls.append(request)
            raise asyncio.CancelledError

    executor, _ = build_executor(CancellingTransport(), logger=audit_logger)

    with pytest.raises(asyncio.CancelledError):
        await executor.execute(op("auth_user"))

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    cancelled = audit_records[-1]
    assert [record.event for record in audit_records] == ["started", "cancelled"]
    assert cancelled.sdk_error_code == "operation_cancelled"
    assert cancelled.error_source == "application"
    assert cancelled.exception_type == "CancelledError"


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
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=transport,
        session_context=session,
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
        FrozenClock(),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)
    executor = DefaultRequestExecutor(
        operation_executor=operation_executor,
        session_gate=coordinator,
        session_recovery=coordinator,
        logger=logging.getLogger("test-auth-deadlock"),
        clock=FrozenClock(),
    )

    with pytest.raises(NotAuthenticatedError):
        await asyncio.wait_for(executor.execute(op("get_cards_v2")), timeout=0.1)


@pytest.mark.asyncio
async def test_direct_authentication_emits_terminal_audit_for_contract_selection() -> None:
    audit_logger, records = capturing_audit_logger("test-direct-auth-audit")
    session = SessionManager()
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=StubTransport(AUTH_RESPONSE),
        session_context=session,
        timeouts=TimeoutPolicy(),
        logger=audit_logger,
        clock=FrozenClock(),
    )

    class Credentials:
        def get_credentials(self) -> tuple[str, str]:
            return "login", "password"

    authenticator = DefaultAuthenticator(
        operation_executor,
        session,
        Credentials(),
        audit_logger,
        FrozenClock(),
    )

    with pytest.raises(ValueError, match="Доступно несколько договоров"):
        await authenticator.authenticate()

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    assert [record.event for record in audit_records] == ["started", "failed"]
    assert audit_records[-1].operation == "auth_user"
    assert audit_records[-1].sdk_error_code == "contract_selection_failed"
    assert audit_records[-1].levelno == logging.WARNING
    assert session.session_id is None


@pytest.mark.asyncio
async def test_direct_authentication_emits_terminal_audit_for_timeout() -> None:
    audit_logger, records = capturing_audit_logger("test-direct-auth-timeout-audit")
    session = SessionManager()
    session.mark_authenticated("existing-session", "contract-a")
    operation_executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("secret-key"),
        transport=StubTransport(OperationTimeoutError("Превышен общий лимит времени операции")),
        session_context=session,
        timeouts=TimeoutPolicy(),
        logger=audit_logger,
        clock=FrozenClock(),
    )

    class Credentials:
        def get_credentials(self) -> tuple[str, str]:
            return "login", "password"

    authenticator = DefaultAuthenticator(
        operation_executor,
        session,
        Credentials(),
        audit_logger,
        FrozenClock(),
    )

    with pytest.raises(OperationTimeoutError):
        await authenticator.authenticate(contract_id="contract-a")

    audit_records = [record for record in records if getattr(record, "request_audit", False)]
    assert [record.event for record in audit_records] == ["started", "failed"]
    assert audit_records[-1].operation == "auth_user"
    assert audit_records[-1].sdk_error_code == "operation_timeout"
    assert audit_records[-1].http_status_code is None
    assert session.session_id == "existing-session"


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
            timeouts=TimeoutPolicy(),
            logger=logging.getLogger("test-invalid-operation-budget"),
            clock=FrozenClock(),
            max_attempts=0,
        )
