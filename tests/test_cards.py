import pytest

from api_client_opti24.modeling import ValidationError
from api_client_opti24.models.cards import (
    BoolResponse,
    CardDriversResponse,
    CardsV1Response,
    CardsV2Response,
    CardV2Item,
    IDListResponse,
)
from api_client_opti24.services.cards import CardsService
from api_client_opti24.session import SessionManager
from tests.service_support import service_dependencies, typed_request_stub


@pytest.fixture
def mock_client():
    """Создаём изолированный CardsService с заглушками request executor."""

    class MockClient(CardsService):
        def __init__(self):
            self._called = []
            session_manager = SessionManager()
            session_manager.mark_authenticated("fake-session", "1-1FLW4T7")
            super().__init__(*service_dependencies(session_manager))
            self.session_id = "fake-session"

        @typed_request_stub
        async def _request(self, operation, api_version="v1", **kwargs):
            self._called.append((operation, api_version, kwargs))
            # Заглушки ответов для тестов ↓
            if operation == "get_cards_v2":
                return {
                    "status": {"code": 200},
                    "data": {
                        "total_count": 1,
                        "result": [
                            {
                                "id": "19647206",
                                "group_id": "1-1F56KR",
                                "group_name": "Тестовая группа",
                                "contract_id": "1-1FLW4T7",
                                "contract_name": "СЗ01590002",
                                "number": "7005830900073164",
                                "status": "Active",
                                "status_name": "Активна",
                                "product": "limit",
                                "product_name": "Лимитная схема",
                                "carrier": "Virtual Card",
                                "carrier_name": "Виртуальная карта",
                                "platon": False,
                                "avtodor": True,
                                "sync_group_state": "Не синхронизирована",
                                "users": ["1-PBQRL0E"],
                                "mpc": True,
                            }
                        ],
                    },
                    "timestamp": 1710000000,
                }
            elif operation == "get_cards_v1":
                return {
                    "status": {"code": 200},
                    "data": {
                        "total_count": 1,
                        "result": [
                            {
                                "id": "382359",
                                "contract_id": "1-1FLKAJQ",
                                "number": "7005830001422138",
                                "status": "Active",
                                "can_work_offline": True,
                                "card_auth_type": "PIN",
                                "comment": "Комментарий",
                                "date_expired": "2034-09-30 23:59:59",
                                "date_last_usage": "2015-04-27 00:00:00",
                                "date_released": "2014-09-24 00:00:00",
                                "servicecenter_last_usage_name": "AZS103261",
                                "transaction_last_detail": "",
                                "transaction_timeout": {
                                    "type": "H",
                                    "value": "1",
                                },
                                "product": "limit",
                                "payment_of_tolls": "N",
                            }
                        ],
                    },
                    "timestamp": 1710000000,
                }
            elif operation == "get_card_drivers":
                return {
                    "status": {"code": 200},
                    "data": {
                        "total_count": 1,
                        "result": [
                            {
                                "id": "1-3AKNC9S",
                                "login": "79111111111",
                                "first_name": "Роман",
                                "last_name": "Петров",
                                "middle_name": "",
                                "date": "01/01/1970",
                                "position": "Водитель",
                                "role": "Водитель",
                                "mobile_phone": "+79111111111",
                                "email": "test@test.test",
                            }
                        ],
                    },
                    "timestamp": 1710000000,
                }
            elif operation == "block_card":
                return {
                    "status": {"code": 200},
                    "data": ["517945", "517946"],
                    "timestamp": 1710000000,
                }
            elif (
                operation == "set_card_comment"
                or operation == "verify_pin"
                or operation == "reset_pin"
            ):
                return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
            else:
                return {
                    "status": {"code": 200},
                    "data": {"total_count": 0, "result": []},
                    "timestamp": 1710000000,
                }

    return MockClient()


@pytest.mark.asyncio
async def test_get_cards_v2(mock_client):
    result = await mock_client.get_cards_v2()
    assert isinstance(result, CardsV2Response)
    assert result.total_count == 1
    assert result.result[0].id == "19647206"


@pytest.mark.asyncio
async def test_get_cards_v1(mock_client):
    result = await mock_client.get_cards_v1(contract_id="1-1FLKAJQ")
    assert isinstance(result, CardsV1Response)
    assert result.total_count == 1
    assert result.result[0].status == "Active"


@pytest.mark.asyncio
async def test_get_card_drivers(mock_client):
    result = await mock_client.get_card_drivers(card_id="382359", contract_id="1-1FLKAJQ")
    assert isinstance(result, CardDriversResponse)
    assert result.total_count == 1
    assert result.result[0].first_name == "Роман"


@pytest.mark.asyncio
async def test_block_card(mock_client):
    result = await mock_client.block_card(
        contract_id="1-B7C8D",
        card_ids=["517945", "517946"],
        block=True,
    )
    assert isinstance(result, IDListResponse)
    assert result.data == ["517945", "517946"]


@pytest.mark.asyncio
async def test_set_card_comment(mock_client):
    result = await mock_client.set_card_comment(
        card_id="517945",
        contract_id="1-B7C8D",
        comment="COMMENT",
    )
    assert isinstance(result, BoolResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_verify_and_reset_pin(mock_client):
    ok = await mock_client.verify_pin(card_id="382359", contract_id="1-B7C8D")
    assert isinstance(ok, BoolResponse)
    assert ok.data is True

    reset = await mock_client.reset_pin(
        card_id="382359",
        contract_id="1-B7C8D",
        code="TESTCODE",
    )
    assert isinstance(reset, BoolResponse)
    assert reset.data is True


@pytest.mark.asyncio
async def test_iter_cards_v2_is_sequential_and_stops_at_total(mock_client):
    items = [item async for item in mock_client.iter_cards_v2(onpage=1, max_pages=5)]

    assert [item.id for item in items] == ["19647206"]
    operation, _, kwargs = mock_client._called[-1]
    assert operation == "get_cards_v2"
    assert kwargs["params"]["page"] == 1


@pytest.mark.asyncio
async def test_iter_cards_v2_rejects_invalid_bounds_without_request(mock_client):
    before = len(mock_client._called)
    with pytest.raises(ValueError, match="greater than zero"):
        _ = [item async for item in mock_client.iter_cards_v2(max_pages=0)]
    assert len(mock_client._called) == before


def test_card_v2_requires_contract_name():
    with pytest.raises(ValidationError):
        CardV2Item(
            id="19647206",
            group_id="1-1F56KR",
            group_name="Тестовая группа",
            contract_id="1-1FLW4T7",
            number="7005830900073164",
            status="Active",
            product="limit",
            carrier="Virtual Card",
            platon=False,
            avtodor=True,
        )
