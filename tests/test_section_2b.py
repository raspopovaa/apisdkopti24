import inspect
import json
import logging
from decimal import Decimal
from typing import Any, TypeVar

import pytest
from pydantic import ValidationError

from api_client_opti24.models.limits import LimitRequestItem
from api_client_opti24.models.region_limits import (
    RegionLimitRequestItem,
    RegionLimitSetResponse,
)
from api_client_opti24.models.restrictions import RestrictionRequestItem
from api_client_opti24.services.contract import ContractsService
from api_client_opti24.services.ewallet import EwalletService
from api_client_opti24.services.limits import LimitsService
from api_client_opti24.services.region_limits import RegionLimitsService
from api_client_opti24.services.restrictions import RestrictionsService
from api_client_opti24.services.templates import TemplatesService
from api_client_opti24.session import SessionManager
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
async def test_contract_fallback_and_explicit_override() -> None:
    service, executor = _service(
        ContractsService,
        {"get_payments": _response({"total_count": 0, "result": []})},
    )

    await service.get_payments()
    await service.get_payments(contract_id="explicit-contract")

    assert executor.calls[0][1]["params"] == {"contract_id": "session-contract"}
    assert executor.calls[1][1]["params"] == {"contract_id": "explicit-contract"}


@pytest.mark.asyncio
async def test_header_contract_override_is_forwarded() -> None:
    service, executor = _service(
        ContractsService,
        {"get_documents": _response({"total_count": 0, "result": []})},
    )

    await service.get_documents(
        date_start="2026-01-01",
        date_end="2026-01-31",
        contract_id="explicit-contract",
    )

    assert executor.calls[0][1]["request_contract_id"] == "explicit-contract"


@pytest.mark.asyncio
async def test_target_exclusivity_prevents_request() -> None:
    service, executor = _service(LimitsService, {})

    with pytest.raises(ValueError, match="mutually exclusive"):
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

    body = json.loads(executor.calls[0][1]["data"]["limit"])
    assert response.status.code == 200
    assert body[0]["contract_id"] == "session-contract"
    assert body[0]["productType"] == "fuel"
    assert "product_type" not in body[0]


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

    payload = json.loads(executor.calls[0][1]["data"]["region_limit"])
    assert isinstance(response, RegionLimitSetResponse)
    assert response.status.code == 200
    assert response.data == ["region-limit-1"]
    assert payload[0]["contract_id"] == "session-contract"


@pytest.mark.asyncio
async def test_batch_services_reject_raw_mappings_before_request() -> None:
    limits, limit_executor = _service(LimitsService, {})
    regions, region_executor = _service(RegionLimitsService, {})
    restrictions, restriction_executor = _service(RestrictionsService, {})

    with pytest.raises(TypeError, match=r"limits\[0\]"):
        await limits.set_limit(limits=[{"card_id": "card-1"}])  # type: ignore[list-item]
    with pytest.raises(TypeError, match=r"region_limits\[0\]"):
        await regions.set_region_limit(
            region_limits=[{"card_id": "card-1"}]  # type: ignore[list-item]
        )
    with pytest.raises(TypeError, match=r"restrictions\[0\]"):
        await restrictions.set_restriction(
            restrictions=[{"card_id": "card-1"}]  # type: ignore[list-item]
        )

    assert limit_executor.calls == []
    assert region_executor.calls == []
    assert restriction_executor.calls == []


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

    with pytest.raises(ValueError, match="same contract"):
        await service.set_limit(limits=[first, second])

    assert executor.calls == []


@pytest.mark.asyncio
async def test_decimal_money_is_serialized_without_float_rounding() -> None:
    ewallet, ewallet_executor = _service(
        EwalletService,
        {"move_to_card": _response(True)},
    )
    contracts, contract_executor = _service(
        ContractsService,
        {"order_invoice": _response(True)},
    )

    await ewallet.move_to_card(card_id="card-1", amount=Decimal("10.50"))
    await contracts.order_invoice(
        amount=Decimal("12345.67"),
        email="billing@example.org",
    )

    assert ewallet_executor.calls[0][1]["data"]["amount"] == "10.50"
    assert contract_executor.calls[0][1]["data"]["sum"] == "12345.67"


@pytest.mark.asyncio
async def test_invalid_input_does_not_execute_http_request() -> None:
    contracts, contract_executor = _service(ContractsService, {})
    restrictions, restriction_executor = _service(RestrictionsService, {})
    restriction = RestrictionRequestItem.model_validate(
        {
            "card_id": "card-1",
            "group_id": "group-1",
            "productType": "fuel",
            "restriction_type": 1,
        }
    )

    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        await contracts.get_documents(date_start="01.01.2026", date_end="2026-01-31")
    with pytest.raises(ValueError, match="greater than zero"):
        await contracts.order_invoice(amount=Decimal("0"), email="billing@example.org")
    with pytest.raises(ValueError, match="1 to 5"):
        await contracts.order_documents_email(
            ids=["doc-1"],
            fmt="pdf",
            emails=[f"user{index}@example.org" for index in range(6)],
        )
    with pytest.raises(ValueError, match="mutually exclusive"):
        await restrictions.set_restriction(restrictions=[restriction])

    assert contract_executor.calls == []
    assert restriction_executor.calls == []


@pytest.mark.asyncio
async def test_template_contract_fallback_and_override() -> None:
    service, executor = _service(
        TemplatesService,
        {
            "create_template": _response("template-1"),
            "create_template_restriction": _response("restriction-1"),
        },
    )

    await service.create_template(type_="Limit", name="Default")
    await service.create_template_restriction(
        template_id="template-1",
        contract_id="explicit-contract",
        payload={
            "product_type": "fuel",
            "restriction_type": 1,
        },
    )

    assert executor.calls[0][1]["data"]["contract_id"] == "session-contract"
    assert executor.calls[1][1]["json"]["contract_id"] == "explicit-contract"


def test_section_2b_public_methods_are_keyword_only() -> None:
    service_types = (
        ContractsService,
        EwalletService,
        LimitsService,
        RegionLimitsService,
        RestrictionsService,
        TemplatesService,
    )
    for service_type in service_types:
        for name, method in vars(service_type).items():
            if name.startswith("_") or not inspect.iscoroutinefunction(method):
                continue
            parameters = list(inspect.signature(method).parameters.values())[1:]
            assert parameters
            assert all(
                parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters
            ), f"{service_type.__name__}.{name} has positional parameters"
