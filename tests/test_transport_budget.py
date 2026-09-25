from dataclasses import replace

import httpx
import pytest

from apisdkopti24 import (
    APIConnectionError,
    AsyncTransport,
    OperationBudget,
    OperationTimeoutError,
    RetryBudgetExceededError,
)
from apisdkopti24.policies import RetryPolicy
from tests.prepared_request_support import prepared_request


def _response(status_code: int = 200) -> httpx.Response:
    request = httpx.Request("GET", "https://example.com/v1/endpoint")
    if status_code == 200:
        return httpx.Response(status_code, json={"ok": True}, request=request)
    return httpx.Response(status_code, text="error", request=request)


@pytest.mark.asyncio
async def test_attempt_timeout_is_capped_by_remaining_operation_deadline(monkeypatch) -> None:
    captured_timeouts: list[float | None] = []
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(network_attempts=1, rate_limit_attempts=1),
        monotonic=lambda: 2.0,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        del method, url, headers, kwargs
        captured_timeouts.append(timeout)
        return _response()

    monkeypatch.setattr(transport.client, "request", fake_request)

    await transport.request(
        prepared_request(
            "GET",
            "endpoint",
            timeout=30.0,
            budget=OperationBudget(deadline_at=7.0, max_attempts=1),
        )
    )

    assert captured_timeouts == [5.0]
    await transport.aclose()


@pytest.mark.asyncio
async def test_full_jitter_is_injected_and_used_for_network_backoff(monkeypatch) -> None:
    now = 0.0
    sleep_calls: list[float] = []
    calls = 0

    def monotonic() -> float:
        return now

    async def sleep(delay: float) -> None:
        nonlocal now
        sleep_calls.append(delay)
        now += delay

    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_attempts=2,
            rate_limit_attempts=1,
            network_backoff_min_seconds=4.0,
            network_backoff_max_seconds=4.0,
        ),
        monotonic=monotonic,
        sleep=sleep,
        jitter=lambda cap: cap / 2,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal calls
        del method, url, headers, timeout, kwargs
        calls += 1
        if calls == 1:
            raise httpx.RequestError("temporary failure")
        return _response()

    monkeypatch.setattr(transport.client, "request", fake_request)

    result = await transport.request(
        prepared_request(
            "GET", "endpoint", budget=OperationBudget(deadline_at=20.0, max_attempts=2)
        )
    )

    assert result == {"ok": True}
    assert sleep_calls == [2.0]
    assert calls == 2
    await transport.aclose()


@pytest.mark.asyncio
async def test_operation_attempt_budget_caps_nested_rate_limit_retries(monkeypatch) -> None:
    calls = 0
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_attempts=3,
            rate_limit_attempts=3,
            rate_limit_backoff_seconds=0,
        ),
        monotonic=lambda: 0.0,
        jitter=lambda _cap: 0.0,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal calls
        del method, url, headers, timeout, kwargs
        calls += 1
        return _response(509)

    monkeypatch.setattr(transport.client, "request", fake_request)

    with pytest.raises(RetryBudgetExceededError, match="лимит попыток"):
        await transport.request(
            prepared_request(
                "GET", "endpoint", budget=OperationBudget(deadline_at=100.0, max_attempts=2)
            )
        )

    assert calls == 2
    await transport.aclose()


@pytest.mark.asyncio
async def test_operation_deadline_prevents_backoff_after_network_error(monkeypatch) -> None:
    calls = 0
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_attempts=2,
            rate_limit_attempts=1,
            network_backoff_min_seconds=2.0,
            network_backoff_max_seconds=2.0,
        ),
        monotonic=lambda: 0.0,
        jitter=lambda cap: cap,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal calls
        del method, url, headers, timeout, kwargs
        calls += 1
        raise httpx.RequestError("temporary failure")

    monkeypatch.setattr(transport.client, "request", fake_request)

    with pytest.raises(OperationTimeoutError, match="Ожидание перед повтором"):
        await transport.request(
            prepared_request(
                "GET", "endpoint", budget=OperationBudget(deadline_at=1.0, max_attempts=2)
            )
        )

    assert calls == 1
    await transport.aclose()


@pytest.mark.asyncio
async def test_connect_timeout_is_separate_and_capped_by_attempt_timeout(monkeypatch) -> None:
    captured_timeouts: list[object] = []
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(network_attempts=1, rate_limit_attempts=1),
        monotonic=lambda: 0.0,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        del method, url, headers, kwargs
        captured_timeouts.append(timeout)
        return _response()

    monkeypatch.setattr(transport.client, "request", fake_request)

    for deadline in (60.0, 4.0):
        await transport.request(
            replace(
                prepared_request(
                    "GET",
                    "endpoint",
                    timeout=30.0,
                    budget=OperationBudget(deadline_at=deadline, max_attempts=1),
                ),
                connect_timeout=10.0,
            )
        )

    assert captured_timeouts == [
        httpx.Timeout(30.0, connect=10.0),
        httpx.Timeout(4.0, connect=4.0),
    ]
    await transport.aclose()


@pytest.mark.asyncio
async def test_operation_timeout_keeps_connection_error_as_cause(monkeypatch) -> None:
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_attempts=2,
            rate_limit_attempts=1,
            network_backoff_min_seconds=2.0,
            network_backoff_max_seconds=2.0,
        ),
        monotonic=lambda: 0.0,
        jitter=lambda cap: cap,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        del method, url, headers, timeout, kwargs
        raise httpx.ConnectTimeout("connect timed out")

    monkeypatch.setattr(transport.client, "request", fake_request)

    with pytest.raises(APIConnectionError, match="example.com") as caught:
        await transport.request(
            prepared_request(
                "GET", "endpoint", budget=OperationBudget(deadline_at=1.0, max_attempts=2)
            )
        )

    assert isinstance(caught.value.__cause__, OperationTimeoutError)
    assert isinstance(caught.value.__cause__.__cause__, httpx.ConnectTimeout)
    await transport.aclose()


@pytest.mark.asyncio
async def test_connection_error_after_last_attempt_becomes_api_connection_error(
    monkeypatch,
) -> None:
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(network_attempts=1, rate_limit_attempts=1),
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        del method, url, headers, timeout, kwargs
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(transport.client, "request", fake_request)

    with pytest.raises(APIConnectionError) as caught:
        await transport.request(prepared_request("POST", "authUser"))

    assert caught.value.host == "example.com"
    assert isinstance(caught.value.__cause__, httpx.ConnectError)
    await transport.aclose()


@pytest.mark.asyncio
async def test_read_timeout_is_not_reported_as_connection_error(monkeypatch) -> None:
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(network_attempts=1, rate_limit_attempts=1),
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        del method, url, headers, timeout, kwargs
        raise httpx.ReadTimeout("slow response")

    monkeypatch.setattr(transport.client, "request", fake_request)

    with pytest.raises(httpx.ReadTimeout):
        await transport.request(prepared_request("GET", "endpoint"))
    await transport.aclose()
