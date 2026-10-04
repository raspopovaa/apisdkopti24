"""Сервис региональных лимитов."""

import json
import logging
from typing import Any, TypeVar

import pytest
from pydantic import ValidationError

from apisdkopti24.models.limits import LimitRequestItem
from apisdkopti24.models.region_limits import (
    RegionLimitRequestItem,
    RegionLimitSetResponse,
)
from apisdkopti24.models.restrictions import RestrictionRequestItem
from apisdkopti24.services.region_limits import RegionLimitsService
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
        logging.getLogger("region-limits-test"),
    )
    return service, executor


def test_strict_request_models_and_regionlimit_alias() -> None:
    restriction = RestrictionRequestItem.model_validate(
        {
            "card_id": "card-1",
            "productType": "fuel",
            "restriction_type": 1,
        }
    )
    region = RegionLimitRequestItem.model_validate(
        {
            "regionlimit_id": "region-limit-1",
            "card_id": "card-1",
            "country": "RUS",
            "limit_type": 1,
        }
    )

    assert restriction.product_type == "fuel"
    assert restriction.model_dump(by_alias=True)["productType"] == "fuel"
    assert region.id == "region-limit-1"
    assert region.model_dump(by_alias=True)["id"] == "region-limit-1"

    with pytest.raises(ValidationError):
        LimitRequestItem.model_validate(
            {
                "card_id": "card-1",
                "time": {"number": 1, "type": 5},
                "unexpected": True,
            }
        )


@pytest.mark.asyncio
async def test_region_limit_returns_typed_envelope() -> None:
    service, executor = _service(
        RegionLimitsService,
        {"set_region_limit": _response(["region-limit-1"])},
    )
    item = RegionLimitRequestItem.model_validate(
        {
            "card_id": "card-1",
            "country": "RUS",
            "limit_type": 1,
        }
    )

    response = await service.set_region_limit(region_limits=[item])

    payload = json.loads(executor.calls[0][1]["form"]["region_limit"])
    assert isinstance(response, RegionLimitSetResponse)
    assert response.status.code == 200
    assert response.data == ["region-limit-1"]
    assert payload[0]["contract_id"] == "session-contract"
