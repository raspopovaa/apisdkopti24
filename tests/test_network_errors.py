from pathlib import Path

import httpx
import pytest

from apisdkopti24 import (
    APIConnectionError,
    APINetworkError,
    APIResponseTimeoutError,
    AsyncTransport,
    SDKConfigurationError,
    TimeoutPolicy,
)
from apisdkopti24.error_reporting import classify_exception
from apisdkopti24.policies import RetryPolicy
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
