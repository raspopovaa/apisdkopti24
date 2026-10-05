import logging
from decimal import Decimal
from typing import Any, TypeVar

import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.models.region_limits import RegionLimitRequestItem
from apisdkopti24.models.restrictions import RestrictionRequestItem
from apisdkopti24.services.card_group import CardGroupsService
from apisdkopti24.services.cards import CardsService
from apisdkopti24.services.contract import ContractsService
from apisdkopti24.services.ewallet import EwalletService
from apisdkopti24.services.invites import InvitesService
from apisdkopti24.services.limits import LimitsService
from apisdkopti24.services.region_limits import RegionLimitsService
from apisdkopti24.services.reports import ReportsService
from apisdkopti24.services.restrictions import RestrictionsService
from apisdkopti24.services.transactions import TransactionsService
from apisdkopti24.services.users import UsersService
from apisdkopti24.session import SessionManager
from tests.service_support import CountingSessionGate, RecordingRequestExecutor, StubSessionGate


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("service_type", "method_name", "kwargs"),
    [
        (CardsService, "block_card", {"card_ids": []}),
        (CardsService, "get_card_drivers", {"card_id": "  "}),
        (UsersService, "get_users", {"page": 0}),
        (UsersService, "attach_contracts", {"user_id": "user-1", "contracts": []}),
        (InvitesService, "delete_invite", {"invite_id": " "}),
        (
            EwalletService,
            "set_card_product",
            {"card_ids": [], "product": "wallet"},
        ),
        (
            EwalletService,
            "move_to_card",
            {"card_id": " ", "amount": Decimal("1")},
        ),
        (
            CardGroupsService,
            "set_cards_to_group",
            {"group_id": "group-1", "cards_list": []},
        ),
        (ReportsService, "download_report_file", {"job_id": " "}),
        (
            ReportsService,
            "order_report_v1",
            {
                "contract_id": "contract-1",
                "start": "2026-02-01",
                "end": "2026-01-01",
                "report_format": "xlsx",
            },
        ),
        (
            TransactionsService,
            "get_transactions_v1",
            {"contract_id": "contract-1", "count": 0},
        ),
        (
            TransactionsService,
            "get_transactions_v2",
            {
                "contract_id": "contract-1",
                "date_from": "2026-01-01",
                "date_to": "2026-01-31",
                "page_offset": -1,
            },
        ),
    ],
)
async def test_invalid_service_input_never_reaches_executor(
    service_type: type[Any],
    method_name: str,
    kwargs: dict[str, Any],
) -> None:
    executor = RecordingRequestExecutor({})
    session = SessionManager()
    session.restore(session_id="session-1", contract_id="contract-1")
    service = service_type(
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("service-validation-test"),
    )

    with pytest.raises((ValueError, TypeError)):
        await getattr(service, method_name)(**kwargs)

    assert executor.calls == []


@pytest.mark.asyncio
async def test_transactions_v2_uses_selected_contract_when_contract_id_omitted() -> None:
    executor = RecordingRequestExecutor(
        {
            "get_transactions_v2": {
                "status": {"code": 200, "message": "OK"},
                "data": {"total_count": 0, "result": []},
            }
        }
    )
    session = SessionManager()
    session.restore(session_id="session-1", contract_id="selected-contract")
    service = TransactionsService(
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("service-validation-test"),
    )

    await service.get_transactions_v2(
        date_from="2026-01-01",
        date_to="2026-01-31",
    )

    assert executor.calls[0][1]["query"]["contract_id"] == "selected-contract"


@pytest.mark.asyncio
async def test_transactions_v2_explicit_contract_overrides_selected_contract() -> None:
    executor = RecordingRequestExecutor(
        {
            "get_transactions_v2": {
                "status": {"code": 200, "message": "OK"},
                "data": {"total_count": 0, "result": []},
            }
        }
    )
    session = SessionManager()
    session.restore(session_id="session-1", contract_id="selected-contract")
    service = TransactionsService(
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("service-validation-test"),
    )

    await service.get_transactions_v2(
        contract_id="explicit-contract",
        date_from="2026-01-01",
        date_to="2026-01-31",
    )

    assert executor.calls[0][1]["query"]["contract_id"] == "explicit-contract"


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
        logging.getLogger("service-validation-test"),
    )
    return service, executor


@pytest.mark.asyncio
async def test_batch_services_reject_raw_mappings_before_request() -> None:
    limits, limit_executor = _service(LimitsService, {})
    regions, region_executor = _service(RegionLimitsService, {})
    restrictions, restriction_executor = _service(RestrictionsService, {})

    with pytest.raises(RequestValidationError, match=r"limits\[0\]"):
        await limits.set_limit(limits=[{"card_id": "card-1"}])  # type: ignore[list-item]
    with pytest.raises(RequestValidationError, match=r"region_limits\[0\]"):
        await regions.set_region_limit(
            region_limits=[{"card_id": "card-1"}]  # type: ignore[list-item]
        )
    with pytest.raises(RequestValidationError, match=r"restrictions\[0\]"):
        await restrictions.set_restriction(
            restrictions=[{"card_id": "card-1"}]  # type: ignore[list-item]
        )

    assert limit_executor.calls == []
    assert region_executor.calls == []
    assert restriction_executor.calls == []


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

    assert ewallet_executor.calls[0][1]["form"]["amount"] == "10.50"
    assert contract_executor.calls[0][1]["form"]["sum"] == "12345.67"


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
    with pytest.raises(ValueError, match="больше нуля"):
        await contracts.order_invoice(amount=Decimal("0"), email="billing@example.org")
    with pytest.raises(ValueError, match="от 1 до 5"):
        await contracts.order_documents_email(
            ids=["doc-1"],
            fmt="pdf",
            emails=[f"user{index}@example.org" for index in range(6)],
        )
    with pytest.raises(ValueError, match="нельзя задавать одновременно"):
        await restrictions.set_restriction(restrictions=[restriction])

    assert contract_executor.calls == []
    assert restriction_executor.calls == []


def _gated(
    service_type: type[ServiceT],
) -> tuple[ServiceT, RecordingRequestExecutor, CountingSessionGate]:
    executor = RecordingRequestExecutor({})
    gate = CountingSessionGate()
    service = service_type(executor, SessionManager(), gate, logging.getLogger("money"))
    return service, executor, gate


@pytest.mark.parametrize(
    ("service_type", "call"),
    [
        (EwalletService, lambda s: s.move_to_card(card_id="card-1", amount=Decimal("10.005"))),
        (EwalletService, lambda s: s.move_to_contract(card_id="card-1", amount=Decimal("0.001"))),
        (
            ContractsService,
            lambda s: s.order_invoice(amount=Decimal("100.123"), email="user@example.com"),
        ),
    ],
)
@pytest.mark.asyncio
async def test_money_with_fractions_of_kopeck_is_rejected_before_login(service_type, call) -> None:
    service, executor, gate = _gated(service_type)

    with pytest.raises(RequestValidationError, match="двух знаков"):
        await call(service)

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
async def test_trailing_zeros_are_valid_kopecks() -> None:
    ewallet, executor = _service(EwalletService, {"move_to_card": _response(True)})

    await ewallet.move_to_card(card_id="card-1", contract_id="contract-1", amount=Decimal("10.500"))

    assert executor.calls[-1][1]["form"]["amount"] == "10.500"


@pytest.mark.asyncio
async def test_unknown_card_product_is_rejected_with_typed_error_before_login() -> None:
    service, executor, gate = _gated(EwalletService)

    with pytest.raises(RequestValidationError, match="product"):
        await service.set_card_product(card_ids=["card-1"], product="fuel")  # type: ignore[arg-type]

    assert gate.calls == 0
    assert executor.calls == []


# Без contract_id договор известен только после входа. Каждая проверка параметра
# должна сработать раньше: иначе ошибка пользователя стоит authUser и слота лимитера.
_REJECTED_BEFORE_LOGIN = [
    (CardsService, lambda s: s.get_cards_v2(page=0)),
    (CardsService, lambda s: s.get_cards_by_group(group_id=" ")),
    (CardsService, lambda s: s.get_card_detail(card_id=" ")),
    (CardsService, lambda s: s.block_card(card_ids=[])),
    (CardsService, lambda s: s.set_card_comment(card_id="card-1", comment="x" * 91)),
    (CardsService, lambda s: s.verify_pin(card_id=" ")),
    (CardsService, lambda s: s.reset_pin(card_id="card-1", code="")),
    (CardGroupsService, lambda s: s.set_card_group(name="Группа", group_id=" ")),
    (CardGroupsService, lambda s: s.set_cards_to_group(group_id=" ", cards_list=[{}])),
    (CardGroupsService, lambda s: s.remove_card_group(group_id=" ")),
    (
        ContractsService,
        lambda s: s.get_documents(date_start="2026-02-01", date_end="2026-01-01"),
    ),
    (ContractsService, lambda s: s.order_documents_email(ids=[], fmt="pdf", emails=["a@b.ru"])),
    (ContractsService, lambda s: s.order_cards(count=0, office_id="office-1")),
    (LimitsService, lambda s: s.remove_limit(limit_id=" ")),
    (RestrictionsService, lambda s: s.remove_restriction(restriction_id=" ")),
    (RegionLimitsService, lambda s: s.remove_region_limit(regionlimit_id=" ")),
    (TransactionsService, lambda s: s.get_transactions_v1(count=0)),
    (TransactionsService, lambda s: s.get_transaction_detail(transaction_id=" ")),
    (
        TransactionsService,
        lambda s: s.get_card_transactions_v2(
            card_id=" ", date_from="2026-01-01", date_to="2026-01-31"
        ),
    ),
]


@pytest.mark.parametrize(("service_type", "call"), _REJECTED_BEFORE_LOGIN)
@pytest.mark.asyncio
async def test_invalid_parameters_are_rejected_before_lazy_login(service_type, call) -> None:
    service, executor, gate = _gated(service_type)

    with pytest.raises(ValueError):
        await call(service)

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.parametrize(
    ("service_type", "call"),
    [
        (
            ReportsService,
            lambda s: s.order_report_v1(
                start="2026-01-01", end="2026-01-31", report_format="xlsx", group_id="group-1"
            ),
        ),
        (
            ReportsService,
            lambda s: s.order_report_v1(
                start="2026-01-01", end="2026-01-31", report_format="xlsx", cards_list="card-1"
            ),
        ),
        (EwalletService, lambda s: s.set_card_product(card_ids="card-1", product="wallet")),
        (UsersService, lambda s: s.detach_contracts(user_id="user-1", contracts="contract-1")),
    ],
)
@pytest.mark.asyncio
async def test_single_string_is_not_split_into_identifier_characters(service_type, call) -> None:
    # str — тоже Sequence[str]: раньше "group-1" уходил списком из семи символов.
    service, executor, gate = _gated(service_type)

    with pytest.raises(RequestValidationError, match="а не строка"):
        await call(service)

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
async def test_amount_beyond_decimal_precision_is_a_validation_error() -> None:
    service, executor, gate = _gated(EwalletService)

    with pytest.raises(RequestValidationError, match="слишком большое"):
        await service.move_to_card(card_id="card-1", amount=Decimal("1e30"))

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.parametrize("email", [None, 123])
@pytest.mark.asyncio
async def test_non_string_email_is_a_validation_error(email) -> None:
    service, executor, gate = _gated(ContractsService)

    with pytest.raises(RequestValidationError, match="email"):
        await service.order_invoice(amount=Decimal("10"), email=email)

    assert gate.calls == 0


class _Captured(Exception):
    def __init__(self, options: Any) -> None:
        super().__init__("запрос перехвачен")
        self.options = options


class _CapturingExecutor:
    async def execute(self, operation: Any, options: Any = None) -> Any:
        raise _Captured(options)


@pytest.mark.parametrize(
    ("service_type", "call", "form_key"),
    [
        (
            RestrictionsService,
            lambda s: s.set_restriction(
                contract_id="contract-1",
                restrictions=[
                    RestrictionRequestItem(
                        card_id=" card-1 ", product_type="product", restriction_type=1
                    )
                ],
            ),
            "restriction",
        ),
        (
            RegionLimitsService,
            lambda s: s.set_region_limit(
                contract_id="contract-1",
                region_limits=[
                    RegionLimitRequestItem(group_id=" group-1 ", country="RU", limit_type=1)
                ],
            ),
            "region_limit",
        ),
    ],
)
@pytest.mark.asyncio
async def test_batch_items_send_the_trimmed_card_or_group_id(service_type, call, form_key) -> None:
    service = service_type(
        _CapturingExecutor(), SessionManager(), StubSessionGate(), logging.getLogger("trim")
    )

    with pytest.raises(_Captured) as captured:
        await call(service)

    sent = captured.value.options.form[form_key]
    assert '"card-1"' in sent or '"group-1"' in sent
    assert '" card-1 "' not in sent and '" group-1 "' not in sent
