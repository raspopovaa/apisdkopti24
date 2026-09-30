"""Сервис приглашений: сериализация запросов, проверки до отправки, ответы."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport
from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.invites import (
    InviteCreateRequest,
    InviteListResponse,
    InviteResponse,
)
from apisdkopti24.operations import Operation
from apisdkopti24.requests import RequestOptions
from apisdkopti24.services.invites import InvitesService
from apisdkopti24.session import SessionManager
from tests.service_support import StubSessionGate

FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"


class RecordingExecutor:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def execute(
        self, operation: Operation[Any] | str, options: RequestOptions | None = None
    ) -> Any:
        operation_name = operation.name if isinstance(operation, Operation) else operation
        request = options or RequestOptions()
        kwargs = {
            "api_version": request.api_version,
            "route_name": request.route_name,
            "path_params": request.path_params or None,
            "contract_header": request.contract_id,
            "query": dict(request.query) or None,
            "form": dict(request.form) if request.form is not None else None,
            "json_body": request.json_body,
        }
        kwargs = {
            key: value
            for key, value in kwargs.items()
            if value is not None
            or key in {"api_version", "route_name", "path_params", "contract_header"}
        }
        self.calls.append((operation_name, kwargs))
        payload = self.responses[operation_name]
        if isinstance(operation, Operation):
            assert operation.response_type is not None
            return operation.response_type.model_validate(payload)
        return payload

    async def execute_stream(self, operation: str, **kwargs: Any) -> bytes:
        del kwargs
        raise AssertionError(f"Неожиданный запрос потоковой загрузки: {operation}")


def fixture(domain: str, name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / domain / name).read_text(encoding="utf-8"))


def dependencies(
    executor: RecordingExecutor,
    contract_id: str | None = "contract-selected",
) -> tuple[object, ...]:
    session = SessionManager()
    session.mark_authenticated("session", contract_id)
    return (
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("section-2a-service-contracts"),
    )


@pytest.mark.asyncio
async def test_create_invite_serializes_request_and_returns_full_envelope() -> None:
    executor = RecordingExecutor(
        {"create_invite": fixture("invites", "create_invite.success.json")}
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
    executor = RecordingExecutor({})
    service = InvitesService(*dependencies(executor))

    with pytest.raises(ValidationError, match="mobile или email"):
        await service.create_invite(data={"role": "Driver"})

    assert executor.calls == []


@pytest.mark.asyncio
async def test_create_invite_rejects_unknown_fields_before_request() -> None:
    executor = RecordingExecutor({})
    service = InvitesService(*dependencies(executor))

    with pytest.raises(ValidationError):
        await service.create_invite(
            data={"role": "Driver", "mobile": "79990000000", "unexpected": True}
        )

    assert executor.calls == []


@pytest.mark.asyncio
async def test_get_invites_returns_full_envelope() -> None:
    executor = RecordingExecutor({"get_invites": fixture("invites", "get_invites.success.json")})
    service = InvitesService(*dependencies(executor))

    result = await service.get_invites()

    assert isinstance(result, InviteListResponse)
    assert result.status.code == 200
    assert result.data.total_count == 1
    assert result.timestamp == 1591147422


BASE_URL = "https://api.example.test/vip/"


AUTH_BODY = json.loads((FIXTURES / "auth" / "auth_user.success.json").read_text(encoding="utf-8"))


class _Clock:
    def now(self) -> datetime:
        return datetime(2026, 9, 27, 12, 0, 0)

    def monotonic(self) -> float:
        return 0.0

    async def sleep(self, seconds: float) -> None:
        del seconds


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
        clock=_Clock(),
    )
    client = APIClient(
        base_url=BASE_URL,
        api_key="key",
        login="login",
        password="password",
        transport=transport,
        logger=logger,
        clock=_Clock(),
    )
    client.select_contract(contract_id="1-2Q4CN99")
    return client


@pytest.mark.asyncio
async def test_get_invites_sends_filter_as_json_string() -> None:
    requests: list[httpx.Request] = []
    body = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
    async with _client(body, requests) as client:
        await client.invites.get_invites(filter={"status": "Finished", "role": "Driver"})

    query = parse_qs(urlsplit(str(requests[0].url)).query)
    assert json.loads(query["filter"][0]) == {"status": "Finished", "role": "Driver"}
