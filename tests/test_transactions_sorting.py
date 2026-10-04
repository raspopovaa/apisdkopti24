import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.services.transactions import TransactionsService
from apisdkopti24.session import SessionManager
from tests.service_support import RecordingRequestExecutor, StubSessionGate

FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60" / "transactions"


def _service() -> TransactionsService:
    return TransactionsService(
        RecordingRequestExecutor({}),
        SessionManager(),
        StubSessionGate(),
        logging.getLogger("transaction-sorting-test"),
    )


def test_transaction_sorting_uses_requested_field() -> None:
    service = _service()
    items = [SimpleNamespace(amount=20), SimpleNamespace(amount=10)]

    result = service._filter_and_sort(items, sort_by="amount")

    assert [item.amount for item in result] == [10, 20]


def test_transaction_sorting_keeps_input_when_field_is_missing(caplog) -> None:
    service = _service()
    items = [SimpleNamespace(amount=20), SimpleNamespace(amount=10)]

    with caplog.at_level(logging.WARNING, logger="transaction-sorting-test"):
        result = service._filter_and_sort(items, sort_by="missing")

    assert result == items
    assert "Не удалось отсортировать транзакции по полю missing" in caplog.text


def _page_service(
    operation: str, total_count: int
) -> tuple[TransactionsService, RecordingRequestExecutor]:
    fixture = json.loads((FIXTURES / f"{operation}.success.json").read_text(encoding="utf-8"))
    fixture["data"]["total_count"] = total_count
    executor = RecordingRequestExecutor({operation: fixture})
    session = SessionManager()
    session.mark_authenticated("session-1", "contract-1")
    service = TransactionsService(
        executor, session, StubSessionGate(), logging.getLogger("transaction-iter-test")
    )
    return service, executor


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("get_transactions_v2", {}),
        ("get_card_transactions_v2", {"card_id": "card-1"}),
        ("get_transactions_v1", {}),
    ],
)
@pytest.mark.asyncio
async def test_unknown_sort_field_is_rejected_before_request(method, kwargs) -> None:
    executor = RecordingRequestExecutor({})
    service = TransactionsService(
        executor, SessionManager(), StubSessionGate(), logging.getLogger("transaction-sort")
    )
    period = {} if method.endswith("v1") else {"date_from": "2026-09-01", "date_to": "2026-09-30"}

    with pytest.raises(RequestValidationError, match="summ"):
        await getattr(service, method)(sort_by="summ", contract_id="contract-1", **period, **kwargs)

    assert executor.calls == []


@pytest.mark.parametrize(
    ("iterator", "operation", "kwargs"),
    [
        ("iter_transactions_v2", "get_transactions_v2", {}),
        ("iter_card_transactions_v2", "get_card_transactions_v2", {"card_id": "card-1"}),
    ],
)
@pytest.mark.asyncio
async def test_transaction_iterators_page_by_offset_until_total(
    iterator, operation, kwargs
) -> None:
    # Страница отдаёт 2 транзакции, всего 3: нужны 2 запроса со смещениями 0 и 2.
    service, executor = _page_service(operation, total_count=3)

    items = [
        item
        async for item in getattr(service, iterator)(
            date_from="2026-09-01", date_to="2026-09-30", page_limit=2, **kwargs
        )
    ]

    assert len(items) == 4
    assert [call["query"]["page_offset"] for _, call in executor.calls] == [0, 2]
