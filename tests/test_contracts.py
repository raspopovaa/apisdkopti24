from decimal import Decimal

import pytest

from api_client_opti24.models.contracts import (
    ContractDataResponse,
    ContractResponse,
    DocumentsOrderResponse,
    DocumentsResponse,
    InvoiceOrderResponse,
    InvoicesResponse,
    OrderCardsResponse,
    PaymentsResponse,
)
from api_client_opti24.services.contract import ContractsService
from api_client_opti24.session import SessionManager
from tests.service_support import service_dependencies, typed_request_stub


class MockContractClient(ContractsService):
    """Мок для ContractsService."""

    def __init__(self):
        session_manager = SessionManager()
        session_manager.mark_authenticated("mock-session", "1-1FLKAJQ")
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
                        "contract_id": "1-1FLKAJQ",
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
                            "contract_id": "1-1FLKAJQ",
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
                            "contract_id": "1-1FLKAJQ",
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
                            "contract_id": "1-1FLKAJQ",
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
    result = await mock_contract_client.get_contract_data(contract_id="1-1FLKAJQ")
    assert isinstance(result, ContractDataResponse)
    assert isinstance(result.data, ContractResponse)
    assert result.data.mpc is True
    assert result.data.contractData.contract_id == "1-1FLKAJQ"


def test_contract_response_allows_missing_manager_data():
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
            "contract_id": "1-1FLKAJQ",
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

    result = ContractResponse(**payload)

    assert result.managerData is None


@pytest.mark.asyncio
async def test_get_payments(mock_contract_client):
    result = await mock_contract_client.get_payments(contract_id="1-1FLKAJQ")
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
        ids=["DOC1"], fmt="pdf", emails=["test@test.ru"]
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
        email="test@test.ru",
    )
    assert isinstance(result, InvoiceOrderResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_get_invoices(mock_contract_client):
    result = await mock_contract_client.get_invoices()
    assert isinstance(result, InvoicesResponse)
    assert result.data.total_count == 1
    assert result.data.result[0].id == "INV1"
