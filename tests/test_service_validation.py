import logging
from decimal import Decimal
from typing import Any, TypeVar

import pytest

from apisdkopti24.errors import RequestValidationError
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
from tests.service_support import RecordingRequestExecutor, StubSessionGate


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
        logging.getLogger("section-2b-test"),
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
