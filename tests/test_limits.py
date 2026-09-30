"""Сервис продуктовых лимитов."""

import json
import logging
from typing import Any, TypeVar

import pytest

from apisdkopti24.models.limits import LimitRequestItem
from apisdkopti24.services.limits import LimitsService
from apisdkopti24.session import SessionManager
from tests.service_support import RecordingRequestExecutor, StubSessionGate

ServiceT = TypeVar("ServiceT")


def _response(data: Any) -> dict[str, Any]:
    return {"status": {"code": 200}, "data": data, "timestamp": 1710000000}


def _service(
    service_type: type[ServiceT],
    responses: dict[str, dict[str, Any]],
    *,
    contract_id: str = "session-contract",
) -> tuple[ServiceT, RecordingRequestExecutor]:
    executor = RecordingRequestExecutor(responses)
    session = SessionManager()
    session.mark_authenticated("session-id", contract_id)
    service = service_type(
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("section-2b-test"),
    )
    return service, executor


@pytest.mark.asyncio
async def test_target_exclusivity_prevents_request() -> None:
    service, executor = _service(LimitsService, {})

    with pytest.raises(ValueError, match="нельзя задавать одновременно"):
        await service.get_limits(card_id="card-1", group_id="group-1")

    assert executor.calls == []


@pytest.mark.asyncio
async def test_limit_alias_and_session_contract_serialization() -> None:
    service, executor = _service(
        LimitsService,
        {"set_limit": _response(["limit-1"])},
    )
    item = LimitRequestItem.model_validate(
        {
            "card_id": "card-1",
            "productType": "fuel",
            "sum": {"currency": "810", "value": 5000},
            "time": {"number": 1, "type": 5},
        }
    )

    response = await service.set_limit(limits=[item])

    body = json.loads(executor.calls[0][1]["form"]["limit"])
    assert response.status.code == 200
    assert body[0]["contract_id"] == "session-contract"
    assert body[0]["productType"] == "fuel"
    assert "product_type" not in body[0]


@pytest.mark.asyncio
async def test_batch_services_reject_mixed_contract_context_before_request() -> None:
    service, executor = _service(LimitsService, {})
    first = LimitRequestItem.model_validate(
        {
            "contract_id": "contract-a",
            "card_id": "card-1",
            "productType": "fuel",
            "sum": {"currency": "810", "value": 10},
            "time": {"number": 1, "type": 5},
        }
    )
    second = LimitRequestItem.model_validate(
        {
            "contract_id": "contract-b",
            "card_id": "card-2",
            "productType": "fuel",
            "sum": {"currency": "810", "value": 20},
            "time": {"number": 1, "type": 5},
        }
    )

    with pytest.raises(ValueError, match="одинаковый contract_id"):
        await service.set_limit(limits=[first, second])

    assert executor.calls == []
