"""Ответы шлюза на изменения и повтор входа после 5xx."""

from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, ConnectionSettings, ServerError
from apisdkopti24.credentials import StaticCredentialsProvider
from apisdkopti24.error_reporting import classify_exception
from apisdkopti24.errors import KNOWN_ERROR_REASONS, ValidationError, build_api_error
from apisdkopti24.policies import RetryPolicy
from tests.service_support import UNTHROTTLED
from tests.test_contract_placement import _auth_payload

BASE_URL = "https://api.example.test/vip/"
TECH = {
    "status": {
        "code": 502,
        "errors": [{"type": "internalError", "message": "У нас возникли технические проблемы"}],
    }
}


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> APIClient:
    return APIClient(
        settings=ConnectionSettings(base_url=BASE_URL),
        transport=AsyncTransport(
            BASE_URL,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
            rate_limit_policy=UNTHROTTLED,
            retry_policy=RetryPolicy(auth_retry_min_interval_seconds=0),
        ),
        # Случайные значения: тест не зависит от учётных данных.
        credentials_provider=StaticCredentialsProvider(
            api_key=uuid4().hex, login=uuid4().hex, password=uuid4().hex
        ),
    )


def _error(status: int, *, mutation: bool, method: str = "remove_card_group") -> ServerError:
    error = build_api_error(
        status_code=status,
        body=TECH,
        endpoint="/vip/v1/removeCardGroup",
        method_name=method,
        http_status_code=status,
        mutation=mutation,
    )
    assert isinstance(error, ServerError)
    return error


@pytest.mark.parametrize("status", [502, 503, 504])
def test_gateway_error_on_mutation_has_unknown_outcome(status: int) -> None:
    error = _error(status, mutation=True)

    assert type(error) is ServerError
    assert error.context.reason == "outcome_unknown"
    assert error.context.retryable is False
    assert error.context.hint is not None
    assert "могло выполниться" in error.context.hint
    assert "outcome_unknown" in KNOWN_ERROR_REASONS
    assert classify_exception(error).error_reason == "outcome_unknown"


@pytest.mark.parametrize("status", [502, 503, 504])
def test_gateway_error_on_read_stays_retryable(status: int) -> None:
    error = _error(status, mutation=False, method="get_card_groups")

    assert error.context.reason is None
    assert error.context.retryable is True


def test_server_error_500_on_mutation_is_not_outcome_unknown() -> None:
    error = _error(500, mutation=True)

    assert error.context.reason is None


def test_recognized_response_wins_over_outcome_unknown() -> None:
    error = _error(502, mutation=True, method="move_to_card")

    assert error.context.reason == "transfer_failed"


@pytest.mark.asyncio
async def test_mutation_gateway_timeout_through_client_reports_unknown_outcome() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/authUser"):
            return httpx.Response(200, json=_auth_payload(), request=request)
        return httpx.Response(504, json=TECH, request=request)

    client = _client(handler)
    await client.auth.auth_user()
    with pytest.raises(ServerError) as captured:
        await client.card_groups.remove_card_group(group_id="group-1")
    await client.aclose()

    assert captured.value.context.reason == "outcome_unknown"
    assert captured.value.context.retryable is False
    assert sum(path.endswith("/removeCardGroup") for path in calls) == 1


@pytest.mark.asyncio
async def test_read_gateway_timeout_through_client_has_no_unknown_outcome() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/authUser"):
            return httpx.Response(200, json=_auth_payload(), request=request)
        return httpx.Response(504, json=TECH, request=request)

    client = _client(handler)
    await client.auth.auth_user()
    with pytest.raises(ServerError) as captured:
        await client.card_groups.get_card_groups()
    await client.aclose()

    assert captured.value.context.reason is None


def _auth_handler(
    statuses: list[int], calls: list[int]
) -> Callable[[httpx.Request], httpx.Response]:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/authUser")
        status = statuses[min(len(calls), len(statuses) - 1)]
        calls.append(status)
        if status == 200:
            return httpx.Response(200, json=_auth_payload(), request=request)
        body = {"status": {"code": status, "errors": [{"type": "internalError", "message": "x"}]}}
        return httpx.Response(status, json=body, request=request)

    return handler


@pytest.mark.asyncio
async def test_auth_user_is_retried_once_after_server_error() -> None:
    calls: list[int] = []
    client = _client(_auth_handler([500, 200], calls))

    response = await client.auth.auth_user()
    await client.aclose()

    assert response.data.session_id == "session-1"
    assert calls == [500, 200]


@pytest.mark.asyncio
async def test_auth_user_gives_up_after_second_server_error() -> None:
    calls: list[int] = []
    client = _client(_auth_handler([500, 502, 200], calls))

    with pytest.raises(ServerError):
        await client.auth.auth_user()
    await client.aclose()

    assert calls == [500, 502]


@pytest.mark.asyncio
async def test_auth_user_is_not_retried_after_client_error() -> None:
    calls: list[int] = []
    client = _client(_auth_handler([400, 200], calls))

    with pytest.raises(ValidationError):
        await client.auth.auth_user()
    await client.aclose()

    assert calls == [400]


def test_outcome_unknown_keeps_server_secrets_redacted() -> None:
    body = {
        "status": {
            "code": 504,
            "errors": [{"type": "internalError", "message": "сбой password=secret"}],
        }
    }
    error = build_api_error(
        status_code=504,
        body=body,
        endpoint="/vip/v1/blockCard",
        method_name="block_card",
        http_status_code=504,
        mutation=True,
    )

    assert error.context.reason == "outcome_unknown"
    assert "secret" not in str(error)
    assert all("secret" not in message for message in error.server_messages)
