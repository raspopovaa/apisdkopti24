import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from apisdkopti24 import ContractSelectionError
from apisdkopti24.authentication import (
    AuthenticationCoordinator,
    DefaultAuthenticator,
)
from apisdkopti24.config import TimeoutPolicy
from apisdkopti24.errors import AccessDeniedError, NotAuthenticatedError
from apisdkopti24.executor import DefaultRequestExecutor, OperationExecutor
from apisdkopti24.modeling import ResponseModel
from apisdkopti24.models.auth import AuthUserResponse
from apisdkopti24.operations import Operation, OperationSpec
from apisdkopti24.policies import RetryPolicy
from apisdkopti24.requests import (
    FileTarget,
    PreparedRequest,
    RequestOptions,
    RequestSpec,
)
from apisdkopti24.session import SessionManager, SessionState
from apisdkopti24.transport import AsyncTransport
from tests.prepared_request_support import prepared_request


class FrozenClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 31, 12, 0, 0)

    def monotonic(self) -> float:
        return 0.0

    async def sleep(self, seconds: float) -> None:
        del seconds


class APIKeyProvider:
    def get_api_key(self) -> str:
        return "key"


class CountingRegistry:
    def __init__(self, spec: OperationSpec[object]) -> None:
        self.spec = spec
        self.get_calls = 0

    def get(self, name: str) -> OperationSpec[object]:
        self.get_calls += 1
        assert name == self.spec.name
        return self.spec


class RecordingTransport:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []
        self.stream_calls: list[dict[str, Any]] = []

    async def request(self, request: PreparedRequest) -> Any:
        self.calls.append(
            {"method": request.method, "endpoint": request.endpoint, "headers": request.headers}
        )
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    async def request_stream(self, request: PreparedRequest) -> bytes:
        self.stream_calls.append(
            {
                "method": request.method,
                "endpoint": request.endpoint,
                "headers": request.headers,
                "timeout": request.timeout,
                "retry_class": request.retry_class,
                "idempotent": request.idempotent,
            }
        )
        return b"file"

    async def request_stream_to_file(self, request: PreparedRequest, target: FileTarget) -> Path:
        del request
        return target.path

    async def aclose(self) -> None:
        return None


class SessionController:
    def __init__(self, session: SessionManager) -> None:
        self.session = session
        self.recover_calls = 0

    async def ensure_authenticated(self) -> str:
        if not self.session.session_id:
            self.session.mark_authenticated("session-1", "contract-1")
        assert self.session.session_id is not None
        return self.session.session_id

    async def recover(self) -> str:
        self.recover_calls += 1
        self.session.mark_authenticated("session-2", "contract-1")
        return "session-2"


def build_request_executor(transport: RecordingTransport):
    spec = OperationSpec(
        name="get_item",
        response_type=ResponseModel,
        domain="test",
        http_method="GET",
        endpoint="items/{item_id}",
        supported_versions=("v2",),
        default_version="v2",
        demo_available=True,
        idempotent=True,
        request=RequestSpec(has_path=True),
    )
    registry = CountingRegistry(spec)
    session = SessionManager()
    controller = SessionController(session)
    operation_executor = OperationExecutor(
        api_key_provider=APIKeyProvider(),
        transport=transport,
        session_context=session,
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("executor-test"),
        clock=FrozenClock(),
    )
    executor = DefaultRequestExecutor(
        operation_executor=operation_executor,
        session_gate=controller,
        session_recovery=controller,
        logger=logging.getLogger("executor-test"),
    )
    return executor, registry, controller, spec


@pytest.mark.asyncio
async def test_operation_is_resolved_once_and_reused_after_recovery() -> None:
    transport = RecordingTransport(
        [
            NotAuthenticatedError(401, "expired"),
            {"status": {"code": 200}, "data": {}},
        ]
    )
    executor, registry, controller, spec = build_request_executor(transport)

    await executor.execute(spec, RequestOptions(path_params={"item_id": "карта 1"}))

    assert registry.get_calls == 0
    assert controller.recover_calls == 1
    assert [call["endpoint"] for call in transport.calls] == [
        "items/%D0%BA%D0%B0%D1%80%D1%82%D0%B0%201",
        "items/%D0%BA%D0%B0%D1%80%D1%82%D0%B0%201",
    ]
    assert transport.calls[0]["headers"]["session_id"] == "session-1"
    assert transport.calls[1]["headers"]["session_id"] == "session-2"


@pytest.mark.asyncio
async def test_stream_execution_receives_endpoint_policy_metadata() -> None:
    transport = RecordingTransport([])
    spec = OperationSpec(
        name="download",
        response_type=bytes,
        domain="reports",
        http_method="GET",
        endpoint="reports/{job_id}",
        supported_versions=("v2",),
        default_version="v2",
        demo_available=True,
        idempotent=True,
        timeout_class="read_heavy",
        retry_class="safe",
        request=RequestSpec(has_path=True),
    )
    registry = CountingRegistry(spec)
    session = SessionManager()
    controller = SessionController(session)
    operation_executor = OperationExecutor(
        api_key_provider=APIKeyProvider(),
        transport=transport,
        session_context=session,
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("executor-test"),
        clock=FrozenClock(),
    )
    executor = DefaultRequestExecutor(
        operation_executor=operation_executor,
        session_gate=controller,
        session_recovery=controller,
        logger=logging.getLogger("executor-test"),
    )

    result = await executor.execute_stream(
        spec,
        RequestOptions(path_params={"job_id": "job-1"}),
    )

    assert result == b"file"
    assert registry.get_calls == 0
    assert transport.stream_calls[0]["timeout"] == 120.0
    assert transport.stream_calls[0]["retry_class"] == "safe"
    assert transport.stream_calls[0]["idempotent"] is True


class StreamContext:
    def __init__(self, result: httpx.Response | Exception) -> None:
        self.result = result
        self.closed = False

    async def __aenter__(self) -> httpx.Response:
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    async def __aexit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb
        self.closed = True


class FakeHTTPClient:
    def __init__(self, stream_results: list[httpx.Response | Exception]) -> None:
        self.stream_results = stream_results
        self.stream_calls = 0
        self.contexts: list[StreamContext] = []

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        del method, url, kwargs
        raise AssertionError("Unexpected JSON request")

    def stream(self, method: str, url: str, **kwargs: Any) -> StreamContext:
        del method, url, kwargs
        self.stream_calls += 1
        context = StreamContext(self.stream_results.pop(0))
        self.contexts.append(context)
        return context

    async def aclose(self) -> None:
        return None


def response(status: int, content: bytes, content_type: str = "application/octet-stream"):
    return httpx.Response(
        status,
        content=content,
        headers={"content-type": content_type},
        request=httpx.Request("GET", "https://example.test/file"),
    )


@pytest.mark.asyncio
async def test_stream_retries_network_error_and_closes_each_context() -> None:
    client = FakeHTTPClient([httpx.RequestError("temporary"), response(200, b"report")])
    transport = AsyncTransport(
        "https://example.test/vip/",
        http_client=client,
        retry_policy=RetryPolicy(
            network_attempts=2,
            network_backoff_min_seconds=0,
            network_backoff_max_seconds=0,
        ),
    )

    result = await transport.request_stream(prepared_request("GET", "reports/1"))

    assert result == b"report"
    assert client.stream_calls == 2
    assert all(
        context.closed for context in client.contexts if not isinstance(context.result, Exception)
    )


@pytest.mark.asyncio
async def test_stream_retries_rate_limit_then_returns_bytes() -> None:
    client = FakeHTTPClient([response(509, b"limited"), response(200, b"report")])
    transport = AsyncTransport(
        "https://example.test/vip/",
        http_client=client,
        retry_policy=RetryPolicy(rate_limit_attempts=2, rate_limit_backoff_seconds=0),
    )

    result = await transport.request_stream(prepared_request("GET", "reports/1"))

    assert result == b"report"
    assert client.stream_calls == 2


@pytest.mark.asyncio
async def test_unsafe_stream_is_not_retried() -> None:
    client = FakeHTTPClient([httpx.RequestError("unknown outcome")])
    transport = AsyncTransport(
        "https://example.test/vip/",
        http_client=client,
        retry_policy=RetryPolicy(
            network_attempts=5,
            network_backoff_min_seconds=0,
            network_backoff_max_seconds=0,
        ),
    )

    with pytest.raises(httpx.RequestError):
        await transport.request_stream(
            prepared_request("POST", "commands", retry_class="never", idempotent=False)
        )

    assert client.stream_calls == 1


@pytest.mark.asyncio
async def test_stream_decodes_json_error_instead_of_returning_file() -> None:
    body = b'{"status":{"code":403,"errors":[{"type":"accessDenied","message":"denied"}]}}'
    client = FakeHTTPClient([response(200, body, "application/json")])
    transport = AsyncTransport("https://example.test/vip/", http_client=client)

    with pytest.raises(AccessDeniedError):
        await transport.request_stream(prepared_request("GET", "reports/1"))


class StubRequestExecutor:
    def __init__(self, contracts: list[dict[str, Any]]) -> None:
        self.contracts = contracts
        self.calls = 0

    async def execute(
        self,
        operation: Operation[AuthUserResponse] | str,
        **kwargs: Any,
    ) -> AuthUserResponse | dict[str, Any]:
        del kwargs
        self.calls += 1
        operation_name = operation.name if isinstance(operation, Operation) else operation
        assert operation_name == "auth_user"
        payload = {
            "status": {"code": 200},
            "data": {
                "session_id": "new-session",
                "client_id": "client",
                "client_status": "active",
                "org_name": "Test organization",
                "user_id": "user",
                "contracts": self.contracts,
                "role_id": "Supervisor",
                "role_name": "Administrator",
                "access": {"web": True, "api": True, "mobile": True},
                "email": "user@example.test",
            },
            "timestamp": 1,
        }
        if isinstance(operation, Operation):
            assert operation.response_type is not None
            return operation.response_type.model_validate(payload)
        return payload


class Credentials:
    def get_credentials(self) -> tuple[str, str]:
        return "login", "password"


def contract(identifier: str, number: str) -> dict[str, Any]:
    return {"id": identifier, "number": number, "mpc": False}


@pytest.mark.asyncio
async def test_multiple_contracts_require_explicit_selection() -> None:
    session = SessionManager()
    executor = StubRequestExecutor([contract("A", "1"), contract("B", "2")])
    authenticator = DefaultAuthenticator(
        executor, session, Credentials(), logging.getLogger("auth-test")
    )

    with pytest.raises(ContractSelectionError) as exc_info:
        await authenticator.authenticate()

    assert exc_info.value.available_contracts == (("A", "1"), ("B", "2"))
    assert "A" not in str(exc_info.value)
    assert "B" not in str(exc_info.value)
    assert session.state == SessionState.INVALID
    assert session.session_id is None
    assert session.contract_id is None


@pytest.mark.asyncio
async def test_single_contract_is_selected_automatically() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    await authenticator.authenticate()

    assert session.contract_id == "A"


@pytest.mark.asyncio
async def test_both_contract_selectors_are_rejected_before_network() -> None:
    session = SessionManager()
    executor = StubRequestExecutor([contract("A", "1")])
    authenticator = DefaultAuthenticator(
        executor, session, Credentials(), logging.getLogger("auth-test")
    )

    with pytest.raises(ContractSelectionError):
        await authenticator.authenticate(contract_id="A", contract_number="1")

    assert executor.calls == 0


@pytest.mark.asyncio
async def test_recovery_preserves_selected_contract() -> None:
    session = SessionManager()
    session.mark_authenticated("expired-session", "B")
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1"), contract("B", "2")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)

    await coordinator.recover()

    assert session.session_id == "new-session"
    assert session.contract_id == "B"


@pytest.mark.asyncio
async def test_authentication_without_contracts_keeps_contract_unset() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    await authenticator.authenticate()

    assert session.session_id == "new-session"
    assert session.contract_id is None
    assert session.state == SessionState.AUTHENTICATED


@pytest.mark.asyncio
async def test_unknown_contract_does_not_fall_back_to_first() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1"), contract("B", "2")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    with pytest.raises(ContractSelectionError) as exc_info:
        await authenticator.authenticate(contract_id="missing")

    assert exc_info.value.available_contracts == (("A", "1"), ("B", "2"))
    assert session.session_id is None
    assert session.contract_id is None


@pytest.mark.asyncio
async def test_duplicate_contract_number_is_ambiguous() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "same"), contract("B", "same")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    with pytest.raises(ContractSelectionError):
        await authenticator.authenticate(contract_number="same")

    assert session.session_id is None
    assert session.contract_id is None


@pytest.mark.asyncio
async def test_lazy_authentication_uses_preselected_contract_once_concurrently() -> None:
    session = SessionManager()
    session.set_contract("B")
    executor = StubRequestExecutor([contract("A", "1"), contract("B", "2")])
    authenticator = DefaultAuthenticator(
        executor,
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)

    session_ids = await asyncio.gather(*(coordinator.ensure_authenticated() for _ in range(20)))

    assert session_ids == ["new-session"] * 20
    assert executor.calls == 1
    assert session.contract_id == "B"


@pytest.mark.asyncio
async def test_recovery_fails_if_selected_contract_is_no_longer_available() -> None:
    session = SessionManager()
    session.mark_authenticated("expired-session", "B")
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)

    with pytest.raises(ContractSelectionError):
        await coordinator.recover()

    assert session.session_id is None
    assert session.contract_id is None
    assert session.state == SessionState.INVALID
