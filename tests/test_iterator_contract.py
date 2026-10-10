import copy
import json
import logging
from pathlib import Path
from typing import Any

import pytest

from apisdkopti24.errors import PaginationLimitError
from apisdkopti24.requests import RequestOptions
from apisdkopti24.services._shared import paginate
from apisdkopti24.services.cards import CardsService
from apisdkopti24.services.transactions import TransactionsService
from apisdkopti24.session import SessionManager
from tests.service_support import StubSessionGate

FIXTURES = Path(__file__).parent / "fixtures" / "live" / "1.1.60"


def _one_item_page(domain: str, operation: str) -> dict[str, Any]:
    payload = json.loads((FIXTURES / domain / f"{operation}.success.json").read_text("utf-8"))
    payload["data"]["result"] = payload["data"]["result"][:1]
    payload["data"]["total_count"] = 2
    return payload


class ContractSwitchingExecutor:
    """Отдать страницы по одному элементу; после первой приложение выбирает другой договор."""

    def __init__(self, session: SessionManager, page: dict[str, Any]) -> None:
        self.session = session
        self.page = page
        self.contract_headers: list[str | None] = []

    async def execute(self, operation: Any, options: RequestOptions | None = None) -> Any:
        assert options is not None
        self.contract_headers.append(options.contract_id)
        if len(self.contract_headers) == 1:
            self.session.select_contract("contract-b")
        assert operation.response_type is not None
        return operation.response_type.model_validate(copy.deepcopy(self.page))


def _service(service_type: type, domain: str, operation: str) -> tuple[Any, Any]:
    session = SessionManager()
    session.mark_authenticated("session-1", "contract-a")
    executor = ContractSwitchingExecutor(session, _one_item_page(domain, operation))
    service = service_type(executor, session, StubSessionGate(), logging.getLogger("iterators"))
    return service, executor


@pytest.mark.asyncio
async def test_card_iterator_keeps_the_contract_it_started_with() -> None:
    cards, executor = _service(CardsService, "cards", "get_cards_v2")

    items = [item async for item in cards.iter_cards_v2(onpage=1, max_pages=5)]

    assert len(items) == 2
    assert executor.contract_headers == ["contract-a", "contract-a"]


@pytest.mark.asyncio
async def test_transaction_iterators_keep_the_contract_they_started_with() -> None:
    transactions, executor = _service(TransactionsService, "transactions", "get_transactions_v2")

    items = [
        item
        async for item in transactions.iter_transactions_v2(
            date_from="2026-01-01", date_to="2026-01-31", page_limit=1, max_pages=5
        )
    ]
    card_items = [
        item
        async for item in transactions.iter_card_transactions_v2(
            card_id="card-1", date_from="2026-01-01", date_to="2026-01-31", page_limit=1
        )
    ]

    assert len(items) == 2
    assert len(card_items) == 2
    # Первый итератор начат с contract-a; второй — уже после select_contract("contract-b").
    assert executor.contract_headers == ["contract-a", "contract-a", "contract-b", "contract-b"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("pages", "total_count", "max_pages", "expected", "requested"),
    [
        ([[1, 2], [3]], 3, 10, [1, 2, 3], 2),  # остановка по total_count
        ([[1], []], 99, 10, [1], 2),  # остановка на пустой странице
        ([[1], [2], [3]], 99, 2, [1, 2], 2),  # не больше max_pages страниц
    ],
)
async def test_paginate_stops_at_total_empty_page_or_page_limit(
    pages, total_count, max_pages, expected, requested
) -> None:
    requested_pages: list[int] = []

    async def fetch_page(page_index: int) -> tuple[list[int], int]:
        requested_pages.append(page_index)
        return pages[page_index], total_count

    items = [
        item
        async for item in paginate(
            fetch_page,
            max_pages=max_pages,
            operation="iter_test",
            logger=logging.getLogger("paginate-test"),
        )
    ]

    assert items == expected
    assert requested_pages == list(range(requested))


async def _three_records(page_index: int) -> tuple[list[str], int]:
    return [f"record-{page_index}"], 3


@pytest.mark.asyncio
async def test_page_limit_before_total_is_logged_without_record_values(caplog) -> None:
    logger = logging.getLogger("paginate-limit")

    with caplog.at_level(logging.WARNING, logger="paginate-limit"):
        items = [
            item
            async for item in paginate(
                _three_records, max_pages=2, operation="iter_test", logger=logger
            )
        ]

    assert items == ["record-0", "record-1"]
    assert "iter_test остановлен на max_pages=2: получено 2 из 3 записей" in caplog.text
    assert "record-" not in caplog.text


@pytest.mark.asyncio
async def test_strict_page_limit_raises_after_yielding_received_records() -> None:
    received: list[str] = []

    with pytest.raises(PaginationLimitError) as captured:
        async for item in paginate(
            _three_records,
            max_pages=2,
            operation="iter_test",
            logger=logging.getLogger("paginate-strict"),
            strict=True,
        ):
            received.append(item)

    assert received == ["record-0", "record-1"]
    error = captured.value
    assert (error.operation, error.max_pages, error.received, error.total_count) == (
        "iter_test",
        2,
        2,
        3,
    )


@pytest.mark.asyncio
async def test_complete_iteration_does_not_warn(caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="paginate-complete"):
        items = [
            item
            async for item in paginate(
                _three_records,
                max_pages=3,
                operation="iter_test",
                logger=logging.getLogger("paginate-complete"),
                strict=True,
            )
        ]

    assert len(items) == 3
    assert caplog.text == ""


@pytest.mark.asyncio
async def test_card_iterator_strict_mode_reports_incomplete_export() -> None:
    cards, _ = _service(CardsService, "cards", "get_cards_v2")

    with pytest.raises(PaginationLimitError, match="iter_cards_v2"):
        _ = [card async for card in cards.iter_cards_v2(onpage=1, max_pages=1, strict=True)]
