import pytest

from apisdkopti24.models.virtual_cards import (
    MPCActionResponse,
    MPCListResponse,
    PaymentQRResponse,
    ResetMPCResponse,
    SimpleActionResponse,
    VirtualCardResponse,
)
from apisdkopti24.services.virtual_cards import VirtualCardsService
from apisdkopti24.session import SessionManager
from tests.service_support import service_dependencies, typed_request_stub


class DummyClient(VirtualCardsService):
    def __init__(self):
        session_manager = SessionManager()
        session_manager.mark_authenticated("mock-session")
        super().__init__(*service_dependencies(session_manager))
        self.session_id = "mock-session"
        self._called = []

    @typed_request_stub
    async def _request(self, operation, api_version="v2", **kwargs):
        self._called.append((operation, api_version, kwargs))
        if operation == "get_mpc_qr_list":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "_id": "1-MPC",
                            "client_id": "1-CLIENT",
                            "user_id": "1-USER",
                            "login": "79999999999",
                            "role": "Driver",
                            "contract_id": "1-CONTRACT",
                            "card_id": "1-CARD",
                            "card_number": "7005839990006653",
                            "device_id": "device-1",
                            "device_name": "Phone 799999",
                            "tries": 20,
                            "transaction_count": 3,
                            "use_mpc": True,
                            "updated_at": "2020-04-08 13:17:59",
                            "created_at": "2020-04-08 04:20:43",
                        }
                    ],
                },
                "timestamp": 1710000000,
            }
        if operation == "release_virtual_card":
            return {
                "status": {"code": 200},
                "data": {
                    "id": "1-VC",
                    "number": "7005830900073164",
                    "carrier": "Virtual Card",
                    "product": "wallet",
                    "status": "Active",
                },
                "timestamp": 1710000000,
            }
        if operation == "generate_payment_qr":
            return {
                "status": {"code": 200},
                "data": {
                    "code": "85054350563031613B4F07A0700583F",
                    "end_date": 1710000600,
                    "transaction_count": 3,
                    "tries": 20,
                },
                "timestamp": 1710000000,
            }
        if operation in {"init_mpc", "confirm_mpc", "update_mpc"}:
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        if operation == "delete_mpc":
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        if operation == "reset_mpc":
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        if operation == "create_virtual_card":
            return {
                "status": {"code": 200},
                "data": {
                    "id": "1-VC",
                    "number": "7005830900073164",
                    "carrier": "Virtual Card",
                    "product": "wallet",
                    "status": "Active",
                },
                "timestamp": 1710000000,
            }
        raise AssertionError(f"Unexpected request: {operation}")


@pytest.mark.asyncio
async def test_virtual_card_release_methods_return_models():
    client = DummyClient()

    created = await client.create_virtual_card(user_id="1-USER")
    released = await client.release_virtual_card(user_id="1-USER")

    assert isinstance(created, VirtualCardResponse)
    assert isinstance(released, VirtualCardResponse)
    assert created.data.id == "1-VC"
    assert released.data.status == "Active"


@pytest.mark.asyncio
async def test_mpc_methods_return_models():
    client = DummyClient()

    mpc_list = await client.get_mpc_qr_list(contract_id="1-CONTRACT")
    qr = await client.generate_payment_qr(card_id="1-CARD", pin="1234", contract_id="1-CONTRACT")
    init = await client.init_mpc(
        card_id="1-CARD",
        user_id="1-USER",
        pin="1234",
        device_id="device-1",
        device_name="Phone 799999",
        contract_id="1-CONTRACT",
    )
    confirm = await client.confirm_mpc(card_id="1-CARD", code="432245", contract_id="1-CONTRACT")
    update = await client.update_mpc(
        card_id="1-CARD", pin="1234", new_pin="4321", contract_id="1-CONTRACT"
    )
    deleted = await client.delete_mpc(card_id="1-CARD", contract_id="1-CONTRACT")
    reset = await client.reset_mpc(
        card_id="1-CARD", type_="ResetCounterCode", contract_id="1-CONTRACT"
    )

    assert isinstance(mpc_list, MPCListResponse)
    assert isinstance(qr, PaymentQRResponse)
    assert isinstance(init, MPCActionResponse)
    assert isinstance(confirm, MPCActionResponse)
    assert isinstance(update, MPCActionResponse)
    assert isinstance(deleted, SimpleActionResponse)
    assert isinstance(reset, ResetMPCResponse)
    assert mpc_list.result[0].id == "1-MPC"
    assert qr.code == "85054350563031613B4F07A0700583F"


@pytest.mark.asyncio
async def test_qr_methods_send_documented_payloads():
    client = DummyClient()

    await client.generate_payment_qr(card_id="1-CARD", pin="1234", contract_id="1-CONTRACT")
    _, _, kwargs = client._called[-1]
    assert kwargs["path_params"] == {"card_id": "1-CARD"}
    assert kwargs["form"] == {"pin": "1234"}
    assert kwargs["contract_header"] == "1-CONTRACT"


@pytest.mark.asyncio
async def test_qr_methods_validate_pin_and_reset_type():
    client = DummyClient()

    with pytest.raises(ValueError, match="4 to 8 digits"):
        await client.generate_payment_qr(card_id="1-CARD", pin="12ab", contract_id="1-CONTRACT")
    with pytest.raises(ValueError, match="ResetCounterCode"):
        await client.reset_mpc("1-CARD", "unknown", contract_id="1-CONTRACT")
