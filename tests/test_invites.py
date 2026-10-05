"""Сервис приглашений: сериализация запросов, проверки до отправки, ответы."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, RequestValidationError
from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.invites import (
    InviteCreateRequest,
    InviteListResponse,
    InviteResponse,
)
from apisdkopti24.services.invites import InvitesService
from apisdkopti24.session import SessionManager
from tests.service_support import FrozenClock, RecordingRequestExecutor, StubSessionGate

FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"


def fixture(domain: str, name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / domain / name).read_text(encoding="utf-8"))


def dependencies(
    executor: RecordingRequestExecutor,
    contract_id: str | None = "contract-selected",
) -> tuple[object, ...]:
    session = SessionManager()
    session.mark_authenticated("session", contract_id)
    return (
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("invites-test"),
    )


@pytest.mark.asyncio
async def test_create_invite_serializes_request_and_returns_full_envelope() -> None:
    executor = RecordingRequestExecutor(
        {"create_invite": fixture("invites", "create_invite.success.json")}, omit_empty=True
    )
    service = InvitesService(*dependencies(executor))

    result = await service.create_invite(
        data=InviteCreateRequest(
            role="Driver",
            mobile="79990000000",
            contracts=[{"sid": "contract-1"}],
        ),
        with_send=False,
    )

    assert isinstance(result, InviteResponse)
    assert result.status.code == 200
    assert result.timestamp == 1596024392
    assert executor.calls[0][1]["route_name"] == "without_send"
    assert executor.calls[0][1]["json_body"] == {
        "role": "Driver",
        "mobile": "79990000000",
        "contracts": [{"id": "contract-1"}],
    }


@pytest.mark.asyncio
async def test_create_invite_requires_recipient_before_request() -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = InvitesService(*dependencies(executor))

    with pytest.raises(ValidationError, match="mobile или email"):
        await service.create_invite(data={"role": "Driver"})

    assert executor.calls == []


@pytest.mark.asyncio
async def test_create_invite_rejects_unknown_fields_before_request() -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = InvitesService(*dependencies(executor))

    with pytest.raises(ValidationError):
        await service.create_invite(
            data={"role": "Driver", "mobile": "79990000000", "unexpected": True}
        )

    assert executor.calls == []


@pytest.mark.asyncio
async def test_get_invites_returns_full_envelope() -> None:
    executor = RecordingRequestExecutor(
        {"get_invites": fixture("invites", "get_invites.success.json")}, omit_empty=True
    )
    service = InvitesService(*dependencies(executor))

    result = await service.get_invites()

    assert isinstance(result, InviteListResponse)
    assert result.status.code == 200
    assert result.data.total_count == 1
    assert result.timestamp == 1591147422


BASE_URL = "https://api.example.test/vip/"


AUTH_BODY = json.loads((FIXTURES / "auth" / "auth_user.success.json").read_text(encoding="utf-8"))


def _client(body: dict[str, object], requests: list[httpx.Request]) -> APIClient:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/authUser"):
            return httpx.Response(200, json=AUTH_BODY)
        requests.append(request)
        return httpx.Response(200, json=body)

    logger = logging.getLogger("tests.spec_discrepancy_fixes")
    transport = AsyncTransport(
        BASE_URL,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        logger=logger,
        clock=FrozenClock(datetime(2026, 9, 27, 12, 0, 0)),
    )
    client = APIClient(
        base_url=BASE_URL,
        api_key="key",
        login="login",
        password="password",
        transport=transport,
        logger=logger,
        clock=FrozenClock(datetime(2026, 9, 27, 12, 0, 0)),
    )
    client.select_contract(contract_id="1-T000025")
    return client


@pytest.mark.asyncio
async def test_get_invites_sends_filter_as_json_string() -> None:
    requests: list[httpx.Request] = []
    body = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
    async with _client(body, requests) as client:
        await client.invites.get_invites(filter={"status": "Finished", "role": "Driver"})

    query = parse_qs(urlsplit(str(requests[0].url)).query)
    assert json.loads(query["filter"][0]) == {"status": "Finished", "role": "Driver"}


EMPTY_INVITES = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs",
    [
        {"role": "Admin"},
        {"status": "Deleted"},
        {"user_id": "user-1"},
        {"sort": "bogus"},
        {"sort": "sended_at,-unknown"},
    ],
    ids=[
        "unknown-role",
        "unknown-status",
        "user-id-as-string",
        "unknown-sort",
        "unknown-desc-sort",
    ],
)
async def test_get_invites_rejects_invalid_filters_before_request(kwargs: dict[str, Any]) -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = InvitesService(*dependencies(executor))

    with pytest.raises(RequestValidationError):
        await service.get_invites(**kwargs)

    assert executor.calls == []


@pytest.mark.asyncio
async def test_get_invites_sends_user_flag_and_sort_as_in_specification() -> None:
    executor = RecordingRequestExecutor({"get_invites": EMPTY_INVITES}, omit_empty=True)
    service = InvitesService(*dependencies(executor))

    await service.get_invites(
        role="Driver", status="Active", user_id=True, sort="sended_at, -expired_at"
    )

    assert executor.calls[0][1]["query"] == {
        "role": "Driver",
        "status": "Active",
        "user_id": "true",
        "sort": "sended_at,-expired_at",
    }


@pytest.mark.asyncio
async def test_iter_invites_passes_filters_and_sort_to_every_page() -> None:
    executor = RecordingRequestExecutor({"get_invites": EMPTY_INVITES}, omit_empty=True)
    service = InvitesService(*dependencies(executor))

    items = [
        item
        async for item in service.iter_invites(
            user_id=False, sort="-sended_at", filter={"role": "Driver"}, on_page=10
        )
    ]

    assert items == []
    query = executor.calls[0][1]["query"]
    assert query["user_id"] == "false"
    assert query["sort"] == "-sended_at"
    assert json.loads(query["filter"]) == {"role": "Driver"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {"role": "Admin", "mobile": "79990000000"},
        {"role": "Readonly", "mobile": "79990000000"},
        {"role": "Driver", "mobile": ""},
        {"role": "Driver", "email": ""},
        {"role": "Driver", "email": "not-an-email"},
    ],
    ids=["unknown-role", "filter-only-role", "empty-mobile", "empty-email", "invalid-email"],
)
async def test_create_invite_rejects_invalid_role_and_recipient_before_request(
    data: dict[str, Any],
) -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = InvitesService(*dependencies(executor))

    with pytest.raises(ValidationError):
        await service.create_invite(data=data)

    assert executor.calls == []
