"""Сервис итоговой стоимости: calculatePrices и checkPurchase."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, RequestValidationError
from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.final_prices import CheckPurchaseResponse
from apisdkopti24.services.final_prices import FinalPricesService
from apisdkopti24.session import SessionManager
from tests.service_support import (
    CountingSessionGate,
    FrozenClock,
    RecordingRequestExecutor,
    StubSessionGate,
)


class StubSessionContext:
    session_id = "session"
    contract_id = "contract"


def recording_dependencies(executor: RecordingRequestExecutor) -> tuple[object, ...]:
    return (
        executor,
        StubSessionContext(),
        StubSessionGate(),
        logging.getLogger("service-model-boundary-test"),
    )


@pytest.mark.asyncio
async def test_check_purchase_validates_payload_and_uses_typed_operation():
    executor = RecordingRequestExecutor(
        {"check_purchase": {"status": {"code": 200}, "data": True, "timestamp": 1}}
    )
    service = FinalPricesService(*recording_dependencies(executor))
    result = await service.check_purchase(
        card_id="card-1",
        poi_id="poi-1",
        goods=[{"code": "fuel", "quantity": "2", "price": "51.5"}],
    )

    assert isinstance(result, CheckPurchaseResponse)
    assert executor.calls[0][1]["form"] is None
    assert executor.calls[0][1]["json_body"] == {
        "poi_id": "poi-1",
        "goods": [{"code": "fuel", "quantity": 2.0, "price": 51.5}],
    }


@pytest.mark.asyncio
async def test_get_final_prices_sends_goods_as_json_array():
    # В форме список из одного товара превращается в строку, и API отвечает 400
    # «Поле goods должно быть массивом».
    executor = RecordingRequestExecutor(
        {
            "get_final_prices": {
                "status": {"code": 200},
                "data": {"total_count": 1, "goods": [{"code": "fuel", "price": 51.5}]},
                "timestamp": 1,
            }
        }
    )
    service = FinalPricesService(*recording_dependencies(executor))

    await service.get_final_prices(card_id="card-1", poi_id="poi-1", goods=["fuel"])

    assert executor.calls[0][1]["form"] is None
    assert executor.calls[0][1]["json_body"] == {"poi_id": "poi-1", "goods": ["fuel"]}


@pytest.mark.asyncio
async def test_check_purchase_rejects_invalid_nested_item_before_request():
    executor = RecordingRequestExecutor({})
    service = FinalPricesService(*recording_dependencies(executor))

    with pytest.raises(ValidationError):
        await service.check_purchase(
            card_id="card-1",
            poi_id="poi-1",
            goods=[{"code": "fuel", "quantity": 2}],
        )

    assert executor.calls == []


BASE_URL = "https://api.example.test/vip/"


FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"


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
@pytest.mark.parametrize(
    ("poi_id", "goods"),
    [("900019", []), ("  ", ["00000000000007"])],
)
async def test_get_final_prices_rejects_empty_goods_and_poi(poi_id: str, goods: list[str]) -> None:
    requests: list[httpx.Request] = []
    async with _client({"status": {"code": 200}}, requests) as client:
        with pytest.raises(RequestValidationError):
            await client.final_prices.get_final_prices(card_id="900042", poi_id=poi_id, goods=goods)

    assert requests == []


def _gated_service() -> tuple[FinalPricesService, RecordingRequestExecutor, CountingSessionGate]:
    executor = RecordingRequestExecutor({})
    gate = CountingSessionGate()
    service = FinalPricesService(
        executor, SessionManager(), gate, logging.getLogger("final-prices-validation")
    )
    return service, executor, gate


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "goods_item",
    [
        {"code": "fuel", "qty": 2, "quantity": 2, "price": 51.5},
        {"code": "", "quantity": 2, "price": 51.5},
        {"code": "fuel", "quantity": 0, "price": 51.5},
        {"code": "fuel", "quantity": 2, "price": -1},
    ],
    ids=["unknown-field", "empty-code", "zero-quantity", "negative-price"],
)
async def test_check_purchase_rejects_invalid_goods_before_login(
    goods_item: dict[str, Any],
) -> None:
    service, executor, gate = _gated_service()

    with pytest.raises(ValidationError):
        await service.check_purchase(card_id="card-1", poi_id="poi-1", goods=[goods_item])

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get_final_prices", "check_purchase"])
async def test_final_prices_reject_empty_card_id_before_login(method: str) -> None:
    service, executor, gate = _gated_service()
    goods: list[Any] = (
        ["fuel"]
        if method == "get_final_prices"
        else [{"code": "fuel", "quantity": 1, "price": 51.5}]
    )

    with pytest.raises(RequestValidationError, match="card_id"):
        await getattr(service, method)(card_id="  ", poi_id="poi-1", goods=goods)

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
async def test_get_final_prices_rejects_empty_poi_before_login() -> None:
    service, executor, gate = _gated_service()

    with pytest.raises(RequestValidationError, match="poi_id"):
        await service.get_final_prices(card_id="card-1", poi_id=" ", goods=["fuel"])

    assert gate.calls == 0
    assert executor.calls == []
