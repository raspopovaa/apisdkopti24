import logging
from typing import Any

import pytest

from api_client_opti24.modeling import ValidationError
from api_client_opti24.models.contracts import ContractDataResponse
from api_client_opti24.models.final_prices import CheckPurchaseResponse
from api_client_opti24.models.templates import (
    TemplateCreateResponse,
    TemplateLimitCreateResponse,
)
from api_client_opti24.operations import Operation
from api_client_opti24.services.final_prices import FinalPricesService
from api_client_opti24.services.templates import TemplatesService


class RecordingExecutor:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def execute(self, operation: Operation[Any] | str, **kwargs: Any) -> Any:
        operation_name = operation.name if isinstance(operation, Operation) else operation
        self.calls.append((operation_name, kwargs))
        payload = self.responses[operation_name]
        if isinstance(operation, Operation):
            assert operation.response_type is not None
            return operation.response_type.model_validate(payload)
        return payload

    async def execute_stream(self, operation: str, **kwargs: Any) -> bytes:
        del kwargs
        raise AssertionError(f"Unexpected stream request: {operation}")


class StubSessionContext:
    session_id = "session"
    contract_id = "contract"


class StubSessionGate:
    async def ensure_authenticated(self) -> str:
        return "session"


def service_dependencies(executor: RecordingExecutor) -> tuple[object, ...]:
    return (
        executor,
        StubSessionContext(),
        StubSessionGate(),
        logging.getLogger("service-model-boundary-test"),
    )


def test_contract_data_response_accepts_nullable_template_id() -> None:
    response = ContractDataResponse.model_validate(
        {
            "status": {"code": 200, "message": "OK"},
            "data": {
                "mpc": False,
                "template_id": None,
                "status": "active",
                "status_crm": "active",
                "payment_term_id": None,
                "payment_scheme_id": None,
                "is_dealer": False,
                "balanceData": {
                    "available_amount": "0",
                    "own_balance": "0",
                    "balance": "0",
                    "consumption_for_month": "0",
                    "consumption_for_month_volume": "0",
                    "consumption_for_prev_month_volume": "0",
                    "currency": "RUR",
                },
                "contractData": {
                    "contract_id": "contract-1",
                    "way_id": "way-1",
                    "contract_number": "number-1",
                    "unique_payment_id": "payment-1",
                    "client": "client-1",
                    "client_category": "category",
                    "contract_category": "category",
                    "country": "RU",
                    "region": "region",
                    "fin_institution": "institution",
                    "invoice_scheme": "scheme",
                    "contract_status": "active",
                    "contract_status_name": "Active",
                    "pay_scheme": "prepaid",
                    "discount_scheme": "default",
                    "auto_pay": "false",
                    "auto_pay_type": "none",
                    "current_amount_limiter": "0",
                    "date_open": "2026-01-01",
                    "effective_date": "2026-01-01",
                    "end_date": "2026-12-31",
                    "date_expire": "2026-12-31",
                    "product_type": False,
                    "type_code": "type",
                    "supplier_name": "supplier",
                },
                "cardsData": {
                    "cards_quantity_all": "0",
                    "cards_quantity_active": "0",
                },
            },
        }
    )

    assert response.status.message == "OK"
    assert response.data.template_id is None


@pytest.mark.asyncio
async def test_check_purchase_validates_payload_and_uses_typed_operation():
    executor = RecordingExecutor(
        {"check_purchase": {"status": {"code": 200}, "data": True, "timestamp": 1}}
    )
    service = FinalPricesService(*service_dependencies(executor))
    result = await service.check_purchase(
        card_id="card-1",
        poi_id="poi-1",
        goods=[{"code": "fuel", "quantity": "2", "price": "51.5"}],
    )

    assert isinstance(result, CheckPurchaseResponse)
    assert executor.calls[0][1]["data"] == {
        "poi_id": "poi-1",
        "goods": [{"code": "fuel", "quantity": 2.0, "price": 51.5}],
    }


@pytest.mark.asyncio
async def test_check_purchase_rejects_invalid_nested_item_before_request():
    executor = RecordingExecutor({})
    service = FinalPricesService(*service_dependencies(executor))

    with pytest.raises(ValidationError):
        await service.check_purchase(
            card_id="card-1",
            poi_id="poi-1",
            goods=[{"code": "fuel", "quantity": 2}],
        )

    assert executor.calls == []


@pytest.mark.asyncio
async def test_create_template_uses_request_model_and_typed_operation():
    executor = RecordingExecutor(
        {
            "create_template": {
                "status": {"code": 200},
                "data": "template-1",
                "timestamp": 1,
            }
        }
    )
    service = TemplatesService(*service_dependencies(executor))
    result = await service.create_template(
        contract_id="contract-1",
        type_="Wallet",
        name="Main",
    )

    assert isinstance(result, TemplateCreateResponse)
    assert executor.calls[0][1]["data"] == {
        "contract_id": "contract-1",
        "type": "Wallet",
        "name": "Main",
    }


@pytest.mark.asyncio
async def test_update_template_limit_serializes_aliases_and_method_override():
    executor = RecordingExecutor(
        {
            "update_template_limit": {
                "status": {"code": 200},
                "data": "limit-1",
                "timestamp": 1,
            }
        }
    )
    service = TemplatesService(*service_dependencies(executor))

    result = await service.update_template_limit(
        template_id="template-1",
        limit_id="limit-1",
        limits=[
            {
                "contract_id": "contract-1",
                "product_type": "fuel",
                "sum": {"currency": "810", "value": "5000"},
                "time": {"type": "5", "number": 1},
                "term": {"time": {"from": "03:00", "to": "08:00"}},
            }
        ],
    )

    assert isinstance(result, TemplateLimitCreateResponse)
    assert executor.calls[0][1]["json"] == [
        {
            "contract_id": "contract-1",
            "product_type": "fuel",
            "sum": {"currency": "810", "value": 5000.0},
            "time": {"type": 5, "number": 1},
            "term": {"time": {"from": "03:00", "to": "08:00"}},
            "_method": "PUT",
        }
    ]


@pytest.mark.asyncio
async def test_template_payload_rejects_unknown_fields_before_request():
    executor = RecordingExecutor({})
    service = TemplatesService(*service_dependencies(executor))

    with pytest.raises(ValidationError):
        await service.create_template_limit(
            template_id="template-1",
            payload={
                "contract_id": "contract-1",
                "product_type": "fuel",
                "sum": {"value": 5000},
                "time": {"type": 5, "number": 1},
                "unexpected": True,
            },
        )

    assert executor.calls == []


@pytest.mark.asyncio
async def test_template_limit_requires_amount_or_sum_before_request():
    executor = RecordingExecutor({})
    service = TemplatesService(*service_dependencies(executor))

    with pytest.raises(ValueError, match="amount.*sum"):
        await service.create_template_limit(
            template_id="template-1",
            payload={
                "contract_id": "contract-1",
                "product_type": "fuel",
                "time": {"type": 5, "number": 1},
            },
        )

    assert executor.calls == []
