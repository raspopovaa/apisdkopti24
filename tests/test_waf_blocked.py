"""Страница WAF вместо JSON: ``403`` с HTML."""

from __future__ import annotations

from uuid import uuid4

import httpx
import pytest

from apisdkopti24 import (
    AccessDeniedError,
    APIClient,
    AsyncTransport,
    ConnectionSettings,
    WafBlockedError,
)
from apisdkopti24.credentials import StaticCredentialsProvider
from apisdkopti24.error_recognition import KNOWN_ERROR_REASONS, build_api_error
from apisdkopti24.error_reporting import classify_exception
from apisdkopti24.errors import APIError
from tests.service_support import UNTHROTTLED
from tests.test_contract_placement import _auth_payload

BASE_URL = "https://api.example.test/vip/"
WAF_PAGE = (
    "<!DOCTYPE html><HTML><head><title>Request Rejected</title></head>"
    "<body>The requested URL was rejected. Your support ID is: 1234567890</body></HTML>"
)


def _error(status: int, body: object) -> APIError:
    return build_api_error(
        status_code=status,
        body=body,
        endpoint="/vip/v2/cards",
        method_name="get_cards",
        http_status_code=status,
    )


def test_html_403_is_waf_blocked() -> None:
    error = _error(403, WAF_PAGE)

    assert isinstance(error, WafBlockedError)
    assert isinstance(error, AccessDeniedError)
    assert error.context.reason == "waf_blocked"
    assert "waf_blocked" in KNOWN_ERROR_REASONS
    assert error.context.transient is False
    assert error.context.hint is not None and "/vip/" in error.context.hint
    assert error.server_messages == ()
    assert "Request Rejected" not in str(error)
    assert "support ID" not in str(error)


def test_html_on_other_status_is_not_waf() -> None:
    error = _error(500, WAF_PAGE)

    assert not isinstance(error, WafBlockedError)
    assert error.context.reason is None


@pytest.mark.parametrize(
    "body",
    [
        {"status": {"code": 403, "errors": [{"type": "forbidden", "message": "Нет доступа"}]}},
        "Forbidden",
        None,
    ],
)
def test_json_or_plain_403_is_not_waf(body: object) -> None:
    error = _error(403, body)

    assert type(error) is AccessDeniedError
    assert error.context.reason is None


def test_audit_records_waf_reason() -> None:
    descriptor = classify_exception(_error(403, WAF_PAGE))

    assert descriptor.error_reason == "waf_blocked"


async def test_client_raises_waf_blocked_without_html() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/authUser"):
            return httpx.Response(200, json=_auth_payload(), request=request)
        return httpx.Response(403, text=WAF_PAGE, headers={"content-type": "text/html"})

    client = APIClient(
        settings=ConnectionSettings(base_url=BASE_URL),
        transport=AsyncTransport(
            BASE_URL,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
            rate_limit_policy=UNTHROTTLED,
        ),
        credentials_provider=StaticCredentialsProvider(
            api_key=uuid4().hex, login=uuid4().hex, password=uuid4().hex
        ),
    )
    async with client:
        with pytest.raises(WafBlockedError) as caught:
            await client.cards.get_cards_v2()

    assert "<html" not in str(caught.value).casefold()
