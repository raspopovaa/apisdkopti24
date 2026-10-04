from decimal import Decimal

import pytest
from pydantic import ValidationError

from apisdkopti24.models.contracts import (
    ContractDataResponse,
    ContractResponse,
    DocumentsOrderResponse,
    DocumentsResponse,
    InvoiceOrderResponse,
    InvoicesResponse,
    OrderCardsResponse,
    PaymentsResponse,
)
from apisdkopti24.services.contract import ContractsService
from apisdkopti24.session import SessionManager
from tests.service_support import service_dependencies, typed_request_stub


class MockContractClient(ContractsService):
    """Мок для ContractsService."""

    def __init__(self):
        session_manager = SessionManager()
        session_manager.mark_authenticated("mock-session", "1-T000002")
        super().__init__(*service_dependencies(session_manager))
        self.session_id = "mock-session"

    @typed_request_stub
    async def _request(self, operation, api_version="v1", **kwargs):
        if operation == "get_contract_data":
            return {
                "status": {"code": 200},
                "data": {
                    "mpc": True,
                    "template_id": "TEMPLATE1",
                    "status": "Active",
                    "status_crm": "CRM_OK",
                    "payment_term_id": "PT1",
                    "payment_scheme_id": "PS1",
                    "is_dealer": False,  # 👈 фикс: раньше было "Is_dealer"
                    "balanceData": {
                        "available_amount": "1000",
                        "own_balance": "500",
                        "balance": "1500",
                        "consumption_for_month": "200",
                        "consumption_for_month_volume": "100",
                        "consumption_for_prev_month_volume": "90",
                        "currency": "RUB",
                    },
                    "contractData": {
                        "contract_id": "1-T000002",
                        "way_id": "WAY1",
                        "contract_number": "C12345",
                        "unique_payment_id": "U123",
                        "client": "CLIENT1",
                        "client_category": "VIP",
                        "contract_category": "Standard",
                        "country": "RU",
                        "region": "77",
                        "fin_institution": "Bank",
                        "invoice_scheme": "Monthly",
                        "contract_status": "Active",
                        "contract_status_name": "Активен",
                        "pay_scheme": "Prepaid",
                        "discount_scheme": "DS1",
                        "auto_pay": "true",
                        "auto_pay_type": "card",
                        "current_amount_limiter": "100000",
                        "date_open": "2020-01-01",
                        "effective_date": "2020-01-01",
                        "end_date": "2030-01-01",
                        "date_expire": "2031-01-01",
                        "product_type": True,
                        "type_code": "STD",
                        "supplier_name": "SupplierX",
                    },
                    "managerData": {
                        "email": "manager@test.ru",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                    },
                    "cardsData": {
                        "cards_quantity_all": "100",
                        "cards_quantity_active": "90",
                    },
                },
                "timestamp": 1710000000,
            }
        elif operation == "get_payments":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "PAY1",
                            "contract_id": "1-T000002",
                            "date": "2025-01-01T10:00:00",
                            "amount": "1000",
                            "currency": "810;RUR",
                            "amount_client": "1000",
                            "description": "Payment",
                            "payment_name": "Payment To Client Contract",
                            "payment_type": "P;Advice",
                            "payment_number": "12345",
                        }
                    ],
                },
                "timestamp": 1710000000,
            }
        elif operation == "get_documents":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "DOC1",
                            "name": "УПД",
                            "name_doc": "Invoice",
                            "number": "DOC-1",
                            "date": 1710000000,
                            "total": 500.0,
                            "vat": 100.0,
                            "sum": 400.0,
                            "currency": "руб.",
                            "consignee": "Demo",
                            "contract_id": "1-T000002",
                            "contract_name": "C12345",
                        }
                    ],
                },
                "timestamp": 1710000000,
            }
        elif (
            operation == "order_documents_email"
            or operation == "order_cards"
            or operation == "order_invoice"
        ):
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        elif operation == "get_invoices":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "INV1",
                            "contract_id": "1-T000002",
                            "ref_number": "INV-1",
                            "date_start": "2025-01-01",
                            "date_end": "2025-01-31",
                            "last_update": "2025-02-01T00:00:00",
                            "currency": "810",
                            "amount": "15000",
                            "paid_amount": "0",
                            "status": "OPEN",
                            "comment": "Intermediate Invoice",
                        }
                    ],
                },
                "timestamp": 1710000000,
            }
        return {"status": {"code": 200}, "data": {}, "timestamp": 1710000000}


# 🔹 фикстура
@pytest.fixture
def mock_contract_client():
    return MockContractClient()


# 🔹 Тесты
@pytest.mark.asyncio
async def test_get_contract_data(mock_contract_client):
    result = await mock_contract_client.get_contract_data(contract_id="1-T000002")
    assert isinstance(result, ContractDataResponse)
    assert isinstance(result.data, ContractResponse)
    assert result.data.mpc is True
    assert result.data.contractData.contract_id == "1-T000002"


def test_contract_response_requires_manager_data():
    payload = {
        "mpc": True,
        "template_id": "TEMPLATE1",
        "status": "Active",
        "status_crm": "CRM_OK",
        "payment_term_id": "PT1",
        "payment_scheme_id": "PS1",
        "is_dealer": False,
        "balanceData": {
            "available_amount": "1000",
            "own_balance": "500",
            "balance": "1500",
            "consumption_for_month": "200",
            "consumption_for_month_volume": "100",
            "consumption_for_prev_month_volume": "90",
            "currency": "RUB",
        },
        "contractData": {
            "contract_id": "1-T000002",
            "way_id": "WAY1",
            "contract_number": "C12345",
            "unique_payment_id": "U123",
            "client": "CLIENT1",
            "client_category": "VIP",
            "contract_category": "Standard",
            "country": "RU",
            "region": "77",
            "fin_institution": "Bank",
            "invoice_scheme": "Monthly",
            "contract_status": "Active",
            "contract_status_name": "Активен",
            "pay_scheme": "Prepaid",
            "discount_scheme": "DS1",
            "auto_pay": "true",
            "auto_pay_type": "card",
            "current_amount_limiter": "100000",
            "date_open": "2020-01-01",
            "effective_date": "2020-01-01",
            "end_date": "2030-01-01",
            "date_expire": "2031-01-01",
            "product_type": True,
            "type_code": "STD",
            "supplier_name": "SupplierX",
        },
        "cardsData": {
            "cards_quantity_all": "100",
            "cards_quantity_active": "90",
        },
    }

    with pytest.raises(ValidationError, match="managerData"):
        ContractResponse(**payload)


@pytest.mark.asyncio
async def test_get_payments(mock_contract_client):
    result = await mock_contract_client.get_payments(contract_id="1-T000002")
    assert isinstance(result, PaymentsResponse)
    assert result.data.total_count == 1
    assert result.data.result[0].id == "PAY1"


@pytest.mark.asyncio
async def test_get_documents(mock_contract_client):
    result = await mock_contract_client.get_documents(
        date_start="2025-01-01",
        date_end="2025-09-01",
    )
    assert isinstance(result, DocumentsResponse)
    assert result.data.total_count == 1
    assert result.data.result[0].id == "DOC1"


@pytest.mark.asyncio
async def test_order_documents_email(mock_contract_client):
    result = await mock_contract_client.order_documents_email(
        ids=["DOC1"], fmt="pdf", emails=["user8@example.com"]
    )
    assert isinstance(result, DocumentsOrderResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_order_cards(mock_contract_client):
    result = await mock_contract_client.order_cards(count=10, office_id="OFFICE1")
    assert isinstance(result, OrderCardsResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_order_invoice(mock_contract_client):
    result = await mock_contract_client.order_invoice(
        amount=Decimal("15000.00"),
        email="user8@example.com",
    )
    assert isinstance(result, InvoiceOrderResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_get_invoices(mock_contract_client):
    result = await mock_contract_client.get_invoices()
    assert isinstance(result, InvoicesResponse)
    assert result.data.total_count == 1
    assert result.data.result[0].id == "INV1"


def test_contract_data_response_requires_template_id() -> None:
    response = ContractDataResponse.model_validate(
        {
            "status": {"code": 200, "message": "OK"},
            "data": {
                "mpc": False,
                "template_id": "template-1",
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
                "managerData": {
                    "email": "manager@example.test",
                    "first_name": "Иван",
                    "last_name": "Иванов",
                },
            },
        }
    )

    assert response.status.message == "OK"
    assert response.data.template_id == "template-1"
