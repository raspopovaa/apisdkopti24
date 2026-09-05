import logging
from decimal import Decimal
from typing import Any

import pytest

from api_client_opti24.services.card_group import CardGroupsService
from api_client_opti24.services.cards import CardsService
from api_client_opti24.services.ewallet import EwalletService
from api_client_opti24.services.invites import InvitesService
from api_client_opti24.services.reports import ReportsService
from api_client_opti24.services.transactions import TransactionsService
from api_client_opti24.services.users import UsersService
from api_client_opti24.session import SessionManager
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

    assert executor.calls[0][1]["params"]["contract_id"] == "selected-contract"


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

    assert executor.calls[0][1]["params"]["contract_id"] == "explicit-contract"
