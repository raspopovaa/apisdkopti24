import asyncio

import httpx
import pytest
from httpx import Request, Response

from api_client_opti24 import AsyncTransport
from api_client_opti24.errors import (
    AccessDeniedError,
    APIError,
    NotAuthenticatedError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from api_client_opti24.policies import ConcurrencyPolicy, RateLimitPolicy, RetryPolicy


class DummyResp(Response):
    """Простейший заглушка для имитации ответов httpx.Response"""

    def __init__(self, status_code, text=None, json_data=None):
        self._text = text
        self._json_data = json_data
        self._request = Request(method="GET", url="http://example.com/endpoint")
        super().__init__(status_code=status_code, content=text.encode() if text else b"")

    def json(self):
        if self._json_data is not None:
            return self._json_data
        return self.text  # Возвращаем текст вместо исключения

    @property
    def text(self):
        return self._text or ""


@pytest.mark.parametrize("base_url", ["", "   "])
def test_transport_rejects_empty_base_url(base_url):
    with pytest.raises(ValueError, match="base_url is empty"):
        AsyncTransport(base_url=base_url)


@pytest.mark.parametrize("base_url", ["api.example.com/vip", "/vip/"])
def test_transport_rejects_base_url_without_protocol(base_url):
    with pytest.raises(ValueError, match="starting with http:// or https://"):
        AsyncTransport(base_url=base_url)


def test_transport_normalizes_base_url():
    transport = AsyncTransport(base_url="  https://api.example.com/vip/  ")

    assert transport.base_url == "https://api.example.com/vip/"


def test_transport_rejects_plain_http_for_remote_host():
    with pytest.raises(ValueError, match="must use https"):
        AsyncTransport(base_url="http://api.example.com/vip/")


def test_transport_allows_plain_http_for_loopback():
    transport = AsyncTransport(base_url="http://127.0.0.1:8080/vip/")

    assert transport.base_url == "http://127.0.0.1:8080/vip/"


def test_handle_response_success_json():
    t = AsyncTransport(base_url="https://example.com")
    resp = DummyResp(200, json_data={"ok": True})
    result = t._handle_response(resp, "test")
    assert result == {"ok": True}


def test_handle_response_success_text_fallback():
    t = AsyncTransport(base_url="https://example.com")
    resp = DummyResp(200, text="plain text")
    result = t._handle_response(resp, "test")
    assert result == "plain text"


def test_handle_response_raises_on_payload_error_inside_http_200():
    t = AsyncTransport(base_url="https://example.com")
    resp = DummyResp(
        200,
        json_data={
            "status": {
                "code": 401,
                "errors": [{"type": "notAuthenticated", "message": "Session expired"}],
            }
        },
    )

    with pytest.raises(NotAuthenticatedError) as exc_info:
        t._handle_response(resp, "info")

    assert exc_info.value.http_status_code == 200
    assert exc_info.value.api_status_code == 401


@pytest.mark.parametrize(
    "status,exc_type",
    [
        (403, AccessDeniedError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (418, APIError),  # I'm a teapot :)
    ],
)
def test_handle_response_errors(status, exc_type):
    t = AsyncTransport(base_url="https://example.com")
    resp = DummyResp(status, text="error response")
    with pytest.raises(exc_type):
        t._handle_response(resp, "endpoint")


@pytest.mark.asyncio
async def test_request_retries_rate_limit_then_succeeds(monkeypatch):
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(rate_limit_backoff_seconds=0),
    )
    calls = 0

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal calls
        calls += 1
        if calls < 3:
            return DummyResp(509, text="rate limited")
        return DummyResp(200, json_data={"ok": True})

    monkeypatch.setattr(transport.client, "request", fake_request)

    result = await transport.request("get", "endpoint")

    assert result == {"ok": True}
    assert calls == 3


@pytest.mark.asyncio
async def test_request_retries_network_errors_then_succeeds(monkeypatch):
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_backoff_min_seconds=0,
            network_backoff_max_seconds=0,
        ),
    )
    calls = 0

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal calls
        calls += 1
        if calls < 3:
            raise httpx.RequestError("temporary network failure")
        return DummyResp(200, json_data={"ok": True})

    monkeypatch.setattr(transport.client, "request", fake_request)

    result = await transport.request("get", "endpoint")

    assert result == {"ok": True}
    assert calls == 3


@pytest.mark.asyncio
async def test_request_does_not_retry_unsafe_post_after_network_error(monkeypatch):
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_attempts=5,
            network_backoff_min_seconds=0,
            network_backoff_max_seconds=0,
        ),
    )
    calls = 0

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal calls
        calls += 1
        raise httpx.RequestError("response state is unknown")

    monkeypatch.setattr(transport.client, "request", fake_request)

    with pytest.raises(httpx.RequestError):
        await transport.request("post", "invoice", retry_class="never")

    assert calls == 1


@pytest.mark.asyncio
async def test_request_retries_explicitly_idempotent_operation(monkeypatch):
    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_attempts=2,
            network_backoff_min_seconds=0,
            network_backoff_max_seconds=0,
        ),
    )
    calls = 0

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.RequestError("temporary network failure")
        return DummyResp(200, json_data={"ok": True})

    monkeypatch.setattr(transport.client, "request", fake_request)

    result = await transport.request(
        "post",
        "idempotent-command",
        retry_class="safe",
        idempotent=True,
    )

    assert result == {"ok": True}
    assert calls == 2


@pytest.mark.asyncio
async def test_concurrency_policy_bounds_active_requests(monkeypatch):
    release = asyncio.Event()
    two_started = asyncio.Event()
    active = 0
    maximum_active = 0

    transport = AsyncTransport(
        base_url="https://example.com",
        concurrency_policy=ConcurrencyPolicy(max_in_flight=2),
        retry_policy=RetryPolicy(network_attempts=1, rate_limit_attempts=1),
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        nonlocal active, maximum_active
        active += 1
        maximum_active = max(maximum_active, active)
        if active == 2:
            two_started.set()
        await release.wait()
        active -= 1
        return DummyResp(200, json_data={"ok": True})

    monkeypatch.setattr(transport.client, "request", fake_request)
    tasks = [asyncio.create_task(transport.request("get", f"item-{index}")) for index in range(5)]

    await asyncio.wait_for(two_started.wait(), timeout=1)
    assert maximum_active == 2
    release.set()
    await asyncio.gather(*tasks)

    assert maximum_active == 2


@pytest.mark.asyncio
async def test_request_stream_to_file_writes_binary_response_atomically(tmp_path):
    payload = b"report-data-" * 10_000

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/octet-stream"},
            content=payload,
            request=request,
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = AsyncTransport(
        base_url="https://example.com/vip/",
        http_client=http_client,
    )
    destination = tmp_path / "report.xlsx"

    result = await transport.request_stream_to_file(
        "GET",
        "reports/job/file",
        destination,
        api_version="v2",
        retry_class="safe",
        idempotent=True,
        chunk_size=1024,
        write_buffer_size=16 * 1024,
    )

    assert result == destination
    assert destination.read_bytes() == payload
    assert not list(tmp_path.glob("*.part"))
    await http_client.aclose()


@pytest.mark.asyncio
async def test_transport_rejects_invalid_stream_buffer_size():
    transport = AsyncTransport(base_url="https://example.com")

    with pytest.raises(ValueError, match="write_buffer_size"):
        await transport.request_stream_to_file(
            "GET",
            "reports/job/file",
            "report.bin",
            write_buffer_size=0,
        )
    await transport.aclose()


@pytest.mark.asyncio
async def test_rate_limiter_spaces_requests_without_real_sleep(monkeypatch):
    now = 0.0
    sleep_calls = []

    def monotonic():
        return now

    async def fake_sleep(delay):
        nonlocal now
        sleep_calls.append(delay)
        now += delay

    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(network_attempts=1, rate_limit_attempts=1),
        rate_limit_policy=RateLimitPolicy(requests_per_second=2),
        sleep=fake_sleep,
        monotonic=monotonic,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        return DummyResp(200, json_data={"ok": True})

    monkeypatch.setattr(transport.client, "request", fake_request)

    await transport.request("get", "first")
    await transport.request("get", "second")

    assert sleep_calls == [0.5]


@pytest.mark.asyncio
async def test_auth_limiter_spaces_repeated_authorizations(monkeypatch):
    now = 0.0
    sleep_calls = []

    def monotonic():
        return now

    async def fake_sleep(delay):
        nonlocal now
        sleep_calls.append(delay)
        now += delay

    transport = AsyncTransport(
        base_url="https://example.com",
        retry_policy=RetryPolicy(
            network_attempts=1,
            rate_limit_attempts=1,
            auth_retry_min_interval_seconds=5,
        ),
        sleep=fake_sleep,
        monotonic=monotonic,
    )

    async def fake_request(method, url, headers=None, timeout=None, **kwargs):
        return DummyResp(200, json_data={"ok": True})

    monkeypatch.setattr(transport.client, "request", fake_request)

    await transport.request("post", "authUser", retry_class="network_only")
    await transport.request("post", "authUser", retry_class="network_only")

    assert sleep_calls == [5]


@pytest.mark.asyncio
async def test_stream_builds_same_origin_url_without_duplicate_vip():
    seen_urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, content=b"report", request=request)

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = AsyncTransport(
        base_url="https://example.com/vip/",
        http_client=http_client,
    )

    content = await transport.request_stream(
        "get",
        "reports/jobs/job-1",
        api_version="v2",
    )

    assert content == b"report"
    assert seen_urls == ["https://example.com/vip/v2/reports/jobs/job-1"]
    await http_client.aclose()


@pytest.mark.asyncio
async def test_stream_rejects_absolute_external_url():
    transport = AsyncTransport(base_url="https://example.com/vip/")

    with pytest.raises(ValueError, match="must be relative"):
        await transport.request_stream("get", "https://attacker.invalid/report")

    await transport.aclose()
