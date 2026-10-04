import inspect
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, RequestValidationError
from apisdkopti24.modeling import ValidationError
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
from tests.service_support import (
    RecordingRequestExecutor,
    service_dependencies,
    typed_request_stub,
)


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
        raise AssertionError(f"Неожиданный запрос: {operation}")


@pytest.mark.asyncio
async def test_virtual_card_release_methods_return_models():
    client = DummyClient()

    created = await client.create_virtual_card(user_id="1-USER", contract_id="1-CONTRACT")
    released = await client.release_virtual_card(
        type_="wallet", user_id="1-USER", contract_id="1-CONTRACT"
    )

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

    with pytest.raises(ValueError, match="от 4 до 8 цифр"):
        await client.generate_payment_qr(card_id="1-CARD", pin="12ab", contract_id="1-CONTRACT")
    with pytest.raises(ValueError, match="ResetCounterCode"):
        await client.reset_mpc(
            card_id="1-CARD", type_="unknown", contract_id="1-CONTRACT"  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "method_name",
    [
        "get_mpc_qr_list",
        "generate_payment_qr",
        "init_mpc",
        "confirm_mpc",
        "update_mpc",
        "delete_mpc",
        "reset_mpc",
    ],
)
def test_qr_mpc_methods_accept_keyword_arguments_only(method_name: str) -> None:
    parameters = list(
        inspect.signature(getattr(VirtualCardsService, method_name)).parameters.values()
    )[1:]

    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters)


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


class _CountingGate:
    def __init__(self) -> None:
        self.calls = 0

    async def ensure_authenticated(self) -> str:
        self.calls += 1
        return "session"


def _recording_service(
    session: SessionManager,
) -> tuple[VirtualCardsService, RecordingRequestExecutor, _CountingGate]:
    card = {"status": {"code": 200}, "data": {"id": "vc-1"}, "timestamp": 1}
    executor = RecordingRequestExecutor({"create_virtual_card": card, "release_virtual_card": card})
    gate = _CountingGate()
    service = VirtualCardsService(executor, session, gate, logging.getLogger("vc-test"))
    return service, executor, gate


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("create_virtual_card", {"template_id": "tpl-1"}),
        ("release_virtual_card", {"type_": "limit"}),
    ],
)
async def test_virtual_card_issue_uses_selected_session_contract(
    method: str, kwargs: dict[str, Any]
) -> None:
    # Без договора сервер выпустил бы карту на первый договор пользователя.
    session = SessionManager()
    session.mark_authenticated("session", "selected-contract")
    service, executor, _ = _recording_service(session)

    await getattr(service, method)(**kwargs)

    call = executor.calls[0][1]
    assert call["contract_header"] == "selected-contract"
    assert call["form"]["contract_id"] == "selected-contract"


@pytest.mark.asyncio
async def test_virtual_card_issue_without_any_contract_is_rejected() -> None:
    session = SessionManager()
    session.mark_authenticated("session")
    service, executor, _ = _recording_service(session)

    with pytest.raises(RequestValidationError, match="contract_id"):
        await service.release_virtual_card(type_="wallet")

    assert executor.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs",
    [{"type_": "wallet", "template_id": "tpl-1"}, {}, {"type_": "credit"}],
    ids=["both-sources", "no-source", "unknown-type"],
)
async def test_release_virtual_card_validates_before_login(kwargs: dict[str, Any]) -> None:
    service, executor, gate = _recording_service(SessionManager())

    with pytest.raises(ValidationError):
        await service.release_virtual_card(**kwargs)

    assert gate.calls == 0
    assert executor.calls == []


def test_unsourced_virtual_card_models_are_removed() -> None:
    import apisdkopti24.models.virtual_cards as vc_models

    for name in (
        "ConfirmVirtualCardRequest",
        "ConfirmVirtualCardResponse",
        "ResendSMSRequest",
        "ResendSMSResponse",
        "RerunVirtualCardReleaseRequest",
        "RerunVirtualCardReleaseResponse",
        "DeleteVirtualCardResponse",
        "DeleteMPCResponse",
        "ResetMPCRequest",
    ):
        assert not hasattr(vc_models, name), name


def _mpc_service(
    session: SessionManager,
) -> tuple[VirtualCardsService, RecordingRequestExecutor, _CountingGate]:
    ok = {"status": {"code": 200}, "data": True, "timestamp": 1}
    qr = {
        "status": {"code": 200},
        "data": {"code": "PAYLOAD", "end_date": 2, "transaction_count": 0, "tries": 20},
        "timestamp": 1,
    }
    executor = RecordingRequestExecutor(
        {
            "generate_payment_qr": qr,
            "init_mpc": ok,
            "confirm_mpc": ok,
            "update_mpc": ok,
            "delete_mpc": ok,
            "reset_mpc": ok,
        }
    )
    gate = _CountingGate()
    service = VirtualCardsService(executor, session, gate, logging.getLogger("mpc-test"))
    return service, executor, gate


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("generate_payment_qr", {"card_id": "card-1", "pin": "12a4"}),
        ("generate_payment_qr", {"card_id": " ", "pin": "1234"}),
        (
            "init_mpc",
            {
                "card_id": "card-1",
                "user_id": "user-1",
                "pin": "1234",
                "device_id": "device-1",
                "device_name": "short",
            },
        ),
        ("confirm_mpc", {"card_id": "card-1", "code": ""}),
        ("update_mpc", {"card_id": "card-1", "pin": "1234", "new_pin": "12"}),
        ("delete_mpc", {"card_id": " "}),
        ("reset_mpc", {"card_id": "card-1", "type_": "ResetEverything"}),
    ],
    ids=[
        "qr-bad-pin",
        "qr-empty-card",
        "init-short-device-name",
        "confirm-empty-code",
        "update-short-new-pin",
        "delete-empty-card",
        "reset-unknown-type",
    ],
)
async def test_mpc_methods_validate_before_login(method: str, kwargs: dict[str, Any]) -> None:
    service, executor, gate = _mpc_service(SessionManager())

    with pytest.raises(ValueError):
        await getattr(service, method)(**kwargs)

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
async def test_generate_payment_qr_does_not_require_contract() -> None:
    # В спецификации QR у pay нет contract_id: без договора метод не входит и не падает.
    session = SessionManager()
    session.mark_authenticated("session")
    service, executor, gate = _mpc_service(session)

    await service.generate_payment_qr(card_id="card-1", pin="1234")

    assert gate.calls == 0
    assert executor.calls[0][1]["contract_header"] is None


@pytest.mark.asyncio
async def test_generate_payment_qr_sends_selected_contract_when_present() -> None:
    session = SessionManager()
    session.mark_authenticated("session", "selected-contract")
    service, executor, _ = _mpc_service(session)

    await service.generate_payment_qr(card_id="card-1", pin="1234")

    assert executor.calls[0][1]["contract_header"] == "selected-contract"


def test_qr_secrets_are_hidden_from_model_repr() -> None:
    payment = PaymentQRResponse.model_validate(
        {
            "status": {"code": 200},
            "data": {
                "code": "SECRET-PAYLOAD",
                "end_date": 2,
                "transaction_count": 0,
                "tries": 20,
            },
        }
    )
    profiles = MPCListResponse.model_validate(
        {
            "status": {"code": 200},
            "data": {
                "total_count": 1,
                "result": [
                    {
                        "_id": "mpc-1",
                        "client_id": "client-1",
                        "user_id": "user-1",
                        "login": "79990000000",
                        "role": "Driver",
                        "contract_id": "contract-1",
                        "card_id": "card-1",
                        "card_number": "7000000000000000",
                        "device_id": "SECRET-DEVICE",
                        "device_name": "Phone 79990000",
                        "tries": 20,
                        "transaction_count": 3,
                        "use_mpc": True,
                        "created_at": "2026-01-01 00:00:00",
                    }
                ],
            },
        }
    )

    assert payment.code == "SECRET-PAYLOAD"
    assert "SECRET-PAYLOAD" not in repr(payment)
    assert "7000000000000000" not in repr(profiles)
    assert "SECRET-DEVICE" not in repr(profiles)


def test_card_number_is_redacted_in_log_payloads() -> None:
    from apisdkopti24.sanitization import sanitize_for_logging

    assert "7000000000000000" not in str(sanitize_for_logging({"card_number": "7000000000000000"}))


@pytest.mark.parametrize(
    ("method_name", "expected"),
    [("init_mpc", ("Первое", "Второе")), ("get_cards_v2", ())],
)
def test_error_message_arrays_are_read_only_for_qr(
    method_name: str, expected: tuple[str, ...]
) -> None:
    from apisdkopti24.errors import build_api_error

    body = {
        "status": {
            "code": 400,
            "errors": [{"type": "validationFailed", "message": ["Первое", "Второе"]}],
        }
    }

    error = build_api_error(
        status_code=400, body=body, endpoint="cards", method_name=method_name, http_status_code=400
    )

    assert error.server_messages == expected
