"""Регрессии находок ревью: журнал httpx, единый вход, срок операции, статус ответа."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator, Callable
from typing import Any
from uuid import uuid4

import httpx
import pytest

from apisdkopti24 import APIClient, correlation_scope
from apisdkopti24.config import ConnectionSettings, TimeoutPolicy
from apisdkopti24.credentials import StaticCredentialsProvider
from apisdkopti24.error_reporting import OperationAudit
from apisdkopti24.errors import (
    AccessDeniedError,
    APIResponseTimeoutError,
    ContractSelectionError,
    NotAuthenticatedError,
    SDKConfigurationError,
)
from apisdkopti24.execution_budget import (
    OperationBudget,
    OperationTimeoutError,
    RetryBudgetExceededError,
)
from apisdkopti24.models.auth import AuthUserResponse
from apisdkopti24.operations import operation
from apisdkopti24.policies import RateLimitPolicy, RetryPolicy
from apisdkopti24.resilience import RateLimiter
from apisdkopti24.runtime import SystemClock
from apisdkopti24.sanitization import scrub
from apisdkopti24.session import SessionManager
from apisdkopti24.transport import AsyncTransport

BASE_URL = "https://api.example.ru/vip/"
EMPTY_PAGE = {"status": {"code": 200}, "data": {"result": [], "total_count": 0}}
Handler = Callable[[httpx.Request], Any]


def make_client(
    handler: Handler,
    *,
    timeouts: TimeoutPolicy | None = None,
    base_url: str = BASE_URL,
) -> APIClient:
    settings = ConnectionSettings(
        base_url=base_url,
        retry_policy=RetryPolicy(
            auth_retry_min_interval_seconds=0.0, network_backoff_min_seconds=0.0
        ),
        rate_limit_policy=RateLimitPolicy(requests_per_second=1000),
        timeouts=timeouts or TimeoutPolicy(),
    )
    transport = AsyncTransport(
        settings.base_url,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        retry_policy=settings.retry_policy,
        rate_limit_policy=settings.rate_limit_policy,
    )
    return APIClient(
        settings=settings,
        transport=transport,
        credentials_provider=StaticCredentialsProvider(
            api_key=uuid4().hex, login=uuid4().hex, password=uuid4().hex
        ),
    )


def is_auth(request: httpx.Request) -> bool:
    return "authUser" in request.url.path


def rejected_login() -> httpx.Response:
    return httpx.Response(
        401,
        json={"status": {"code": 401, "errors": [{"type": "notAuthenticated", "message": "x"}]}},
    )


async def test_httpx_log_hides_sdk_path_and_query(caplog: pytest.LogCaptureFixture) -> None:
    client = make_client(lambda _request: httpx.Response(200, json=EMPTY_PAGE))
    client.restore_session(session_id="session-1", contract_id="contract-1")

    with caplog.at_level(logging.INFO, logger="httpx"):
        await client.cards.get_cards_v2(contract_id="contract-secret", q="ivanov")

    logged = [record.getMessage() for record in caplog.records if record.name == "httpx"]
    assert logged
    assert all("contract-secret" not in line and "ivanov" not in line for line in logged)
    assert all("api.example.ru" in line for line in logged)


@pytest.mark.parametrize(
    "base_url", ["https://API.Example.ru/vip/", "https://api.example.ru:443/vip/"]
)
async def test_httpx_log_hides_urls_for_any_spelling_of_base_url(
    base_url: str, caplog: pytest.LogCaptureFixture
) -> None:
    client = make_client(lambda _request: httpx.Response(200, json=EMPTY_PAGE), base_url=base_url)
    client.restore_session(session_id="session-1", contract_id="contract-1")

    with caplog.at_level(logging.INFO, logger="httpx"):
        await client.cards.get_cards_v2(contract_id="contract-secret", q="ivanov")

    logged = [record.getMessage() for record in caplog.records if record.name == "httpx"]
    assert logged
    assert all("contract-secret" not in line and "ivanov" not in line for line in logged)


async def test_httpx_log_keeps_urls_of_other_clients(caplog: pytest.LogCaptureFixture) -> None:
    make_client(lambda _request: httpx.Response(200, json=EMPTY_PAGE))
    other = httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200)))

    with caplog.at_level(logging.INFO, logger="httpx"):
        await other.get("https://other.example.org/items?page=2")

    assert any("other.example.org/items?page=2" in record.getMessage() for record in caplog.records)


async def test_concurrent_calls_share_one_failed_login() -> None:
    auth_calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal auth_calls
        auth_calls += 1
        await asyncio.sleep(0.01)
        return rejected_login()

    client = make_client(handler)

    results = await asyncio.gather(
        *(client.auth.get_info() for _ in range(10)), return_exceptions=True
    )

    assert auth_calls == 1
    assert all(isinstance(result, NotAuthenticatedError) for result in results)


async def test_new_call_after_failed_login_tries_again() -> None:
    auth_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal auth_calls
        auth_calls += 1
        return rejected_login()

    client = make_client(handler)

    for _ in range(2):
        with pytest.raises(NotAuthenticatedError):
            await client.auth.get_info()

    assert auth_calls == 2


@pytest.mark.parametrize("error_type", [OperationTimeoutError, RetryBudgetExceededError])
async def test_budget_failure_of_one_operation_is_not_shared_with_waiters(
    error_type: type[Exception],
) -> None:
    session = SessionManager()
    started = asyncio.Event()
    release = asyncio.Event()

    async def exhausted_login() -> None:
        started.set()
        await release.wait()
        raise error_type("срок другой операции")

    async def own_login() -> None:
        session.mark_authenticated("session-2")

    first = asyncio.create_task(session.ensure_authenticated(exhausted_login))
    await started.wait()
    waiter = asyncio.create_task(session.ensure_authenticated(own_login))
    await asyncio.sleep(0)
    release.set()

    with pytest.raises(error_type):
        await first
    assert await waiter == "session-2"


async def test_cancelled_login_is_not_shared_with_waiters() -> None:
    session = SessionManager()
    started = asyncio.Event()
    calls = 0

    async def authenticate() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            started.set()
            await asyncio.Event().wait()
        session.mark_authenticated("session-2")

    first = asyncio.create_task(session.ensure_authenticated(authenticate))
    await started.wait()
    waiter = asyncio.create_task(session.ensure_authenticated(authenticate))
    await asyncio.sleep(0)
    first.cancel()

    assert await waiter == "session-2"


async def test_waiting_for_login_respects_wait_limit() -> None:
    session = SessionManager()
    started = asyncio.Event()

    async def hang() -> None:
        started.set()
        await asyncio.Event().wait()

    first = asyncio.create_task(session.ensure_authenticated(hang))
    await started.wait()

    with pytest.raises(OperationTimeoutError):
        await session.ensure_authenticated(hang, wait_limit=0.01)

    first.cancel()


async def test_login_before_operation_waits_no_longer_than_total_auth() -> None:
    client = make_client(
        lambda _request: httpx.Response(200, json=EMPTY_PAGE),
        timeouts=TimeoutPolicy(total_auth=0.01),
    )
    started = asyncio.Event()

    async def hang() -> None:
        started.set()
        await asyncio.Event().wait()

    login = asyncio.create_task(client.session_manager.ensure_authenticated(hang))
    await started.wait()

    with pytest.raises(OperationTimeoutError):
        await asyncio.wait_for(client.cards.get_cards_v2(), timeout=1)

    login.cancel()


async def test_lazy_login_uses_operation_budget() -> None:
    client = make_client(lambda _request: rejected_login())
    budget = OperationBudget(deadline_at=SystemClock().monotonic() + 30, max_attempts=2)

    with pytest.raises(NotAuthenticatedError):
        await client.authentication.ensure_authenticated(budget)

    assert budget.attempts_used == 1


class SlowBody(httpx.AsyncByteStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        for _ in range(50):
            await asyncio.sleep(0.02)
            yield b" "
        yield json.dumps(EMPTY_PAGE).encode()


SHORT_DEADLINE = TimeoutPolicy(default=0.15, total_default=0.15, read_heavy=0.15)


async def test_operation_deadline_stops_slow_response_body() -> None:
    client = make_client(
        lambda _request: httpx.Response(200, stream=SlowBody()), timeouts=SHORT_DEADLINE
    )
    client.restore_session(session_id="session-1", contract_id="contract-1")
    started_at = time.monotonic()

    with pytest.raises((OperationTimeoutError, APIResponseTimeoutError)):
        await client.cards.block_card(contract_id="contract-1", card_ids=["card-1"])

    assert time.monotonic() - started_at < 0.6


async def test_attempt_deadline_on_mutation_reports_unknown_outcome() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, stream=SlowBody())

    client = make_client(handler, timeouts=SHORT_DEADLINE)
    client.restore_session(session_id="session-1", contract_id="contract-1")

    with pytest.raises(APIResponseTimeoutError):
        await client.cards.block_card(contract_id="contract-1", card_ids=["card-1"])

    assert calls == 1


async def test_http_401_with_access_denied_does_not_log_in_again() -> None:
    auth_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal auth_calls
        if is_auth(request):
            auth_calls += 1
        return httpx.Response(
            401,
            json={"status": {"code": 401, "errors": [{"type": "accessDenied", "message": "x"}]}},
        )

    client = make_client(handler)
    client.restore_session(session_id="session-1", contract_id="contract-1")

    with pytest.raises(NotAuthenticatedError):
        await client.cards.get_cards_v2(contract_id="contract-1")

    assert auth_calls == 0


@pytest.mark.parametrize("code", ["403", " 403 ", 403.0])
async def test_non_integer_status_code_does_not_mask_api_error(code: object) -> None:
    body = {
        "status": {"code": code, "errors": [{"type": "accessDenied", "message": "x"}]},
        "data": {"result": [], "total_count": 0},
    }
    client = make_client(lambda _request: httpx.Response(200, json=body))
    client.restore_session(session_id="session-1", contract_id="contract-1")

    with pytest.raises(AccessDeniedError):
        await client.cards.get_cards_v2(contract_id="contract-1")


@pytest.mark.parametrize(
    "base_url",
    [
        "https://@api.example.ru/vip/",
        "https://:@api.example.ru/vip/",
        "https://api.example.ru/vip?",
        "https://api.example.ru/vip#",
        "https://[::1/",
    ],
)
def test_base_url_rejects_empty_url_components(base_url: str) -> None:
    with pytest.raises(SDKConfigurationError):
        AsyncTransport(base_url)


def test_operation_id_survives_log_scrubbing() -> None:
    spec = operation("auth_user", AuthUserResponse)
    identifiers = {
        str(
            OperationAudit(
                operation=spec, logger=logging.getLogger("test-ids"), clock=SystemClock()
            )._fields["operation_id"]
        )
        for _ in range(2000)
    }

    assert len(identifiers) == 2000
    assert all(scrub(identifier) == identifier for identifier in identifiers)


async def test_auth_request_respects_common_interval_after_auth_wait() -> None:
    class FakeClock(SystemClock):
        current = 0.0

        def monotonic(self) -> float:
            return self.current

        async def sleep(self, seconds: float) -> None:
            self.current += seconds

    clock = FakeClock()
    limiter = RateLimiter(request_interval=1.0, auth_interval=5.0, clock=clock)

    await limiter.acquire("network_only", None)
    clock.current = 4.5
    await limiter.acquire("safe", None)
    await limiter.acquire("network_only", None)

    assert clock.current == 5.5


class AuditRecords(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(record, "request_audit", False):
            self.records.append(record)


def audit_records(client: APIClient) -> AuditRecords:
    records = AuditRecords()
    client.logger.setLevel(logging.INFO)
    client.logger.addHandler(records)
    return records


def session_without_contract(client: APIClient) -> None:
    client.session_manager.mark_authenticated("session-1")
    client.session_manager.remember_contracts((("contract-1", "1"), ("contract-2", "2")))


async def test_contract_selection_failure_is_audited_for_public_method() -> None:
    client = make_client(lambda _request: httpx.Response(200, json=EMPTY_PAGE))
    session_without_contract(client)
    audit = audit_records(client)

    with correlation_scope("step-1"), pytest.raises(ContractSelectionError):
        await client.cards.get_cards_v2()

    client.logger.removeHandler(audit)
    (record,) = audit.records
    assert record.__dict__["event"] == "failed"
    assert record.__dict__["operation"] == "get_cards_v2"
    assert record.__dict__["sdk_error_code"] == "contract_selection_failed"
    assert record.__dict__["attempts_used"] == 0
    assert record.__dict__["correlation_id"] == "step-1"


async def test_iterator_contract_failure_is_audited_and_keeps_original_error() -> None:
    client = make_client(lambda _request: httpx.Response(200, json=EMPTY_PAGE))
    session_without_contract(client)
    audit = audit_records(client)

    with pytest.raises(ContractSelectionError):
        async for _card in client.cards.iter_cards_v2():
            pass

    client.logger.removeHandler(audit)
    assert [record.__dict__["operation"] for record in audit.records] == ["iter_cards_v2"]


async def test_login_failure_before_operation_is_audited_for_both() -> None:
    client = make_client(lambda _request: rejected_login())
    audit = audit_records(client)

    with pytest.raises(NotAuthenticatedError):
        await client.cards.get_cards_v2()

    client.logger.removeHandler(audit)
    failed = [
        record.__dict__["operation"]
        for record in audit.records
        if record.__dict__["event"] == "failed"
    ]
    assert failed == ["auth_user", "get_cards_v2"]


async def test_explicit_contract_has_only_the_operation_audit() -> None:
    client = make_client(lambda _request: httpx.Response(200, json=EMPTY_PAGE))
    client.restore_session(session_id="session-1", contract_id="contract-1")
    audit = audit_records(client)

    await client.cards.get_cards_v2(contract_id="contract-1")

    client.logger.removeHandler(audit)
    assert [record.__dict__["event"] for record in audit.records] == ["started", "completed"]
