from pathlib import Path

import httpx
import pytest

from apisdkopti24 import (
    APIConnectionError,
    APINetworkError,
    APIResponseTimeoutError,
    AsyncTransport,
    RateLimitError,
    SDKConfigurationError,
    TimeoutPolicy,
)
from apisdkopti24.error_reporting import classify_exception
from apisdkopti24.policies import RateLimitPolicy, RetryPolicy
from apisdkopti24.registry import build_default_registry
from apisdkopti24.requests import FileTarget
from tests.prepared_request_support import prepared_request

NO_BACKOFF = RetryPolicy(network_backoff_min_seconds=0, network_backoff_max_seconds=0)


def _failing_transport(error: Exception) -> tuple[AsyncTransport, list[str]]:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.method)
        raise error

    transport = AsyncTransport(
        "https://api.example.test/vip/",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        retry_policy=NO_BACKOFF,
    )
    return transport, calls


@pytest.mark.parametrize(
    ("raw_error", "expected"),
    [
        (httpx.ConnectError("refused"), APIConnectionError),
        (httpx.ConnectTimeout("connect timed out"), APIConnectionError),
        (httpx.ReadTimeout("read timed out"), APIResponseTimeoutError),
        (httpx.WriteTimeout("write timed out"), APIResponseTimeoutError),
        (httpx.PoolTimeout("pool timed out"), APIResponseTimeoutError),
        (httpx.ReadError("connection reset"), APINetworkError),
        (httpx.RemoteProtocolError("server disconnected"), APINetworkError),
    ],
)
@pytest.mark.asyncio
async def test_httpx_network_errors_become_typed_sdk_errors(raw_error, expected) -> None:
    transport, _ = _failing_transport(raw_error)

    with pytest.raises(APINetworkError) as caught:
        await transport.request(prepared_request("post", "removeCardGroup", retry_class="never"))

    assert type(caught.value) is expected
    assert caught.value.host == "api.example.test"
    assert caught.value.__cause__ is raw_error
    await transport.aclose()


@pytest.mark.asyncio
async def test_safe_read_is_retried_before_the_timeout_is_reported() -> None:
    transport, calls = _failing_transport(httpx.ReadTimeout("read timed out"))

    with pytest.raises(APIResponseTimeoutError):
        await transport.request(prepared_request("get", "cards", retry_class="safe"))

    assert len(calls) == NO_BACKOFF.network_attempts
    await transport.aclose()


@pytest.mark.asyncio
async def test_unsafe_operation_is_sent_once_and_reported_as_timeout() -> None:
    transport, calls = _failing_transport(httpx.ReadTimeout("read timed out"))

    with pytest.raises(APIResponseTimeoutError):
        await transport.request(prepared_request("post", "removeCardGroup", retry_class="never"))

    assert calls == ["POST"]
    await transport.aclose()


@pytest.mark.asyncio
async def test_downloads_report_network_errors_with_the_same_types(tmp_path: Path) -> None:
    transport, _ = _failing_transport(httpx.ReadTimeout("read timed out"))

    with pytest.raises(APIResponseTimeoutError):
        await transport.request_stream(prepared_request("get", "reports/job/file"))
    with pytest.raises(APIResponseTimeoutError):
        await transport.request_stream_to_file(
            prepared_request("get", "reports/job/file"),
            FileTarget(tmp_path / "report.xlsx"),
        )

    assert not (tmp_path / "report.xlsx").exists()
    await transport.aclose()


@pytest.mark.asyncio
async def test_error_text_does_not_include_the_httpx_message() -> None:
    transport, _ = _failing_transport(httpx.ReadError("reset while sending session_id=secret"))

    with pytest.raises(APINetworkError) as caught:
        await transport.request(prepared_request("post", "invoice", retry_class="never"))

    assert "secret" not in str(caught.value)
    assert "api.example.test" in str(caught.value)
    await transport.aclose()


@pytest.mark.parametrize(
    ("error", "code"),
    [
        (APIConnectionError("api.example.test"), "network_connect_failed"),
        (APIResponseTimeoutError("api.example.test"), "network_timeout"),
        (APINetworkError("api.example.test"), "network_error"),
    ],
)
def test_audit_codes_stay_stable_and_respect_idempotency(error, code) -> None:
    registry = build_default_registry()

    safe_read = classify_exception(error, registry.get("get_cards_v2"))
    mutation = classify_exception(error, registry.get("remove_card_group"))

    assert safe_read.sdk_error_code == mutation.sdk_error_code == code
    assert safe_read.error_source == "network"
    assert safe_read.transient is True
    assert safe_read.retry_allowed is True
    assert mutation.retry_allowed is False


@pytest.mark.parametrize("operation", ["remove_card_group", "delete_user"])
def test_slow_deletions_wait_longer_than_heavy_reads(operation: str) -> None:
    # Удаление бывает дольше 120 (группа) и 30 (пользователь) секунд, хотя на
    # сервере объект удаляется: короткий timeout сообщал бы о ложном сбое.
    spec = build_default_registry().get(operation)
    policy = TimeoutPolicy()

    assert spec.timeout_class == "slow_mutation"
    assert policy.resolve(spec.timeout_class) == 300.0
    assert policy.resolve(spec.timeout_class) > policy.read_heavy
    assert policy.resolve_total(spec.timeout_class) >= policy.resolve(spec.timeout_class)


def test_slow_mutation_timeouts_are_validated() -> None:
    with pytest.raises(SDKConfigurationError):
        TimeoutPolicy(slow_mutation=0)
    with pytest.raises(SDKConfigurationError):
        TimeoutPolicy(total_slow_mutation=0)


@pytest.mark.parametrize("operation", ["resend_invite", "order_report_v1"])
def test_get_operations_with_side_effects_are_never_retried(operation: str) -> None:
    # GET, но вызов отправляет SMS или создаёт задачу отчёта: повтор после 429/509
    # или сетевого сбоя повторил бы побочный эффект.
    spec = build_default_registry().get(operation)
    policy = RetryPolicy()

    assert spec.http_method == "GET"
    assert spec.retry_class == "never"
    assert spec.idempotent is False
    assert (
        policy.network_attempt_count(spec.retry_class, spec.http_method, idempotent=spec.idempotent)
        == 1
    )
    assert (
        policy.rate_limit_attempt_count(
            spec.retry_class, spec.http_method, idempotent=spec.idempotent
        )
        == 1
    )


def _rate_limited_transport() -> tuple[AsyncTransport, list[str]]:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.method)
        return httpx.Response(509, json={"status": {"code": 509}}, request=request)

    transport = AsyncTransport(
        "https://api.example.test/vip/",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        retry_policy=RetryPolicy(rate_limit_backoff_seconds=0),
        rate_limit_policy=RateLimitPolicy(requests_per_second=1000),
    )
    return transport, calls


@pytest.mark.parametrize(("billable", "expected_calls"), [(True, 1), (False, 3)])
@pytest.mark.asyncio
async def test_billable_read_is_not_retried_after_rate_limit(
    billable: bool, expected_calls: int
) -> None:
    # Тарифицируется ли ответ 509, не описано: повтор платного чтения мог бы
    # стоить ещё одного запроса, поэтому платное чтение отправляется один раз.
    transport, calls = _rate_limited_transport()

    with pytest.raises(RateLimitError):
        await transport.request(prepared_request("get", "cards", billable=billable))

    assert len(calls) == expected_calls
    await transport.aclose()


@pytest.mark.parametrize(
    ("operation", "billable"),
    [("get_cards_v1", True), ("get_card_detail", True), ("get_cards_v2", False)],
)
def test_prepared_request_carries_route_billing(operation: str, billable: bool) -> None:
    spec = build_default_registry().get(operation)
    route = spec.resolve_route()

    assert bool(route.billable if route.billable is not None else spec.billable) is billable


@pytest.mark.asyncio
async def test_rate_limiter_queue_respects_operation_deadline() -> None:
    import asyncio
    import time

    from apisdkopti24.execution_budget import OperationBudget, OperationTimeoutError
    from apisdkopti24.resilience import RateLimiter

    class RealClock:
        def monotonic(self) -> float:
            return time.monotonic()

        async def sleep(self, seconds: float) -> None:
            await asyncio.sleep(seconds)

    clock = RealClock()
    limiter = RateLimiter(request_interval=1.0, auth_interval=5.0, clock=clock)
    await limiter.acquire("safe", None)  # первый запрос: дальше интервал 1 с
    holder = asyncio.create_task(limiter.acquire("safe", None))  # ждёт ~1 с под блокировкой
    await asyncio.sleep(0.05)

    started = time.monotonic()
    budget = OperationBudget(deadline_at=started + 0.2, max_attempts=5)
    with pytest.raises(OperationTimeoutError, match="очереди"):
        await limiter.acquire("safe", budget)

    assert time.monotonic() - started < 0.6
    await holder
