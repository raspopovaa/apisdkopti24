import copy
import json
import logging
from pathlib import Path
from typing import Any

import pytest

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

    items = [item async for item in paginate(fetch_page, max_pages=max_pages)]

    assert items == expected
    assert requested_pages == list(range(requested))
