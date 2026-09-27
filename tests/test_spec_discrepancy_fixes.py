"""Сквозные проверки исправлений расхождений SDK со спецификацией.

Запросы проходят через APIClient, исполнитель и транспорт до подставного HTTP-сервера,
поэтому проверяется то, что реально уходит на сервер.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, RequestValidationError

BASE_URL = "https://api.example.test/vip/"
FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"
AUTH_BODY = json.loads((FIXTURES / "auth" / "auth_user.success.json").read_text(encoding="utf-8"))
VIRTUAL_CARD_BODY = {
    "status": {"code": 200},
    "data": {"id": "1-VC", "number": "7000", "carrier": "Virtual Card", "product": "wallet"},
    "timestamp": 1710000000,
}


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


def _form(request: httpx.Request) -> dict[str, list[str]]:
    return parse_qs(request.content.decode())


@pytest.mark.asyncio
async def test_create_virtual_card_accepts_explicit_contract_id() -> None:
    requests: list[httpx.Request] = []
    async with _client(VIRTUAL_CARD_BODY, requests) as client:
        await client.virtual_cards.create_virtual_card(user_id="1-USER", contract_id="1-2Q4CNBH")

    assert requests[0].headers["contract_id"] == "1-2Q4CNBH"
    assert _form(requests[0])["contract_id"] == ["1-2Q4CNBH"]


@pytest.mark.asyncio
async def test_release_virtual_card_sends_selected_contract() -> None:
    requests: list[httpx.Request] = []
    async with _client(VIRTUAL_CARD_BODY, requests) as client:
        await client.virtual_cards.release_virtual_card(type_="wallet", contract_id="1-2Q4CNBH")

    assert requests[0].headers["contract_id"] == "1-2Q4CNBH"
    assert _form(requests[0]) == {"contract_id": ["1-2Q4CNBH"], "type": ["wallet"]}


@pytest.mark.asyncio
async def test_get_invites_sends_filter_as_json_string() -> None:
    requests: list[httpx.Request] = []
    body = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
    async with _client(body, requests) as client:
        await client.invites.get_invites(filter={"status": "Finished", "role": "Driver"})

    query = parse_qs(urlsplit(str(requests[0].url)).query)
    assert json.loads(query["filter"][0]) == {"status": "Finished", "role": "Driver"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("poi_id", "goods"),
    [("366038", []), ("  ", ["00000000000007"])],
)
async def test_get_final_prices_rejects_empty_goods_and_poi(poi_id: str, goods: list[str]) -> None:
    requests: list[httpx.Request] = []
    async with _client({"status": {"code": 200}}, requests) as client:
        with pytest.raises(RequestValidationError):
            await client.final_prices.get_final_prices(card_id="989666", poi_id=poi_id, goods=goods)

    assert requests == []
