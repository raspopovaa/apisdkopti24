import logging
from types import SimpleNamespace

from api_client_opti24.services.transactions import TransactionsService
from api_client_opti24.session import SessionManager
from tests.service_support import RecordingRequestExecutor, StubSessionGate


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
    assert "Transaction sorting failed sort_by=missing" in caplog.text
