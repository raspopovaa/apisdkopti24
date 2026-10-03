"""Где сервисы кладут contract_id и что об этом записано в каталоге операций.

Во время работы `contract_locations` определяет только заголовок; в query и тело
договор кладут сами сервисы. Тест сверяет настоящий HTTP-запрос с каталогом, чтобы
описание (матрица запросов, справочник моделей) не расходилось с поведением.
"""

import contextlib
import json
from collections.abc import Awaitable, Callable
from decimal import Decimal
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, ConnectionSettings
from apisdkopti24.credentials import StaticCredentialsProvider
from apisdkopti24.registry import build_default_registry

CONTRACT_ID = "contract-1"

CALLS: dict[str, Callable[[APIClient], Awaitable[Any]]] = {
    "get_cards_v2": lambda c: c.cards.get_cards_v2(contract_id=CONTRACT_ID),
    "get_card_drivers": lambda c: c.cards.get_card_drivers(
        card_id="card-1", contract_id=CONTRACT_ID
    ),
    "get_card_transactions_v2": lambda c: c.transactions.get_card_transactions_v2(
        card_id="card-1", contract_id=CONTRACT_ID, date_from="2026-09-01", date_to="2026-09-30"
    ),
    "get_transactions_v2": lambda c: c.transactions.get_transactions_v2(
        contract_id=CONTRACT_ID, date_from="2026-09-01", date_to="2026-09-30"
    ),
    "get_transaction_detail": lambda c: c.transactions.get_transaction_detail(
        transaction_id="1", contract_id=CONTRACT_ID
    ),
    "move_to_card": lambda c: c.ewallet.move_to_card(
        contract_id=CONTRACT_ID, card_id="card-1", amount=Decimal("1.00")
    ),
    "remove_card_group": lambda c: c.card_groups.remove_card_group(
        group_id="group-1", contract_id=CONTRACT_ID
    ),
    "remove_limit": lambda c: c.limits.remove_limit(contract_id=CONTRACT_ID, limit_id="limit-1"),
    "remove_region_limit": lambda c: c.region_limits.remove_region_limit(
        contract_id=CONTRACT_ID, regionlimit_id="1"
    ),
    "remove_restriction": lambda c: c.restrictions.remove_restriction(
        contract_id=CONTRACT_ID, restriction_id="1"
    ),
    "set_card_comment": lambda c: c.cards.set_card_comment(
        card_id="card-1", comment="Водитель", contract_id=CONTRACT_ID
    ),
    "set_card_product": lambda c: c.ewallet.set_card_product(
        contract_id=CONTRACT_ID, card_ids=["card-1"], product="wallet"
    ),
    "set_cards_to_group": lambda c: c.card_groups.set_cards_to_group(
        group_id="group-1",
        cards_list=[{"id": "card-1", "type": "Attach"}],
        contract_id=CONTRACT_ID,
    ),
    "update_template": lambda c: c.templates.update_template(
        template_id="template-1", type_="Limit", name="Шаблон", contract_id=CONTRACT_ID
    ),
}


def _auth_payload() -> dict[str, Any]:
    return {
        "status": {"code": 200},
        "data": {
            "session_id": "session-1",
            "client_id": "client-1",
            "client_status": "Active",
            "org_name": "Test organization",
            "user_id": "user-1",
            "contracts": [
                {
                    "id": CONTRACT_ID,
                    "number": "C-1",
                    "mpc": False,
                    "cards_count": 0,
                    "one_price": False,
                }
            ],
            "role_id": "Supervisor",
            "role_name": "Administrator",
            "access": {"web": True, "api": True, "mobile": True},
            "email": "user@example.test",
            "read_only": False,
        },
    }


def _placement(request: httpx.Request) -> set[str]:
    locations = set()
    if request.headers.get("contract_id") == CONTRACT_ID:
        locations.add("header")
    if CONTRACT_ID in parse_qs(request.url.query.decode()).get("contract_id", []):
        locations.add("query")
    body = request.content.decode()
    content_type = request.headers.get("content-type", "")
    if body and "form" in content_type and CONTRACT_ID in json.dumps(parse_qs(body)):
        locations.add("form")
    if body and "json" in content_type and CONTRACT_ID in body:
        locations.add("json")
    return locations


@pytest.mark.parametrize("operation", CALLS, ids=CALLS)
@pytest.mark.asyncio
async def test_contract_placement_matches_catalog(operation: str) -> None:
    sent: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/authUser"):
            return httpx.Response(200, json=_auth_payload(), request=request)
        sent.append(request)
        return httpx.Response(200, json={"status": {"code": 200}, "data": True}, request=request)

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = APIClient(
        settings=ConnectionSettings(base_url="https://api.example.test/vip/"),
        transport=AsyncTransport("https://api.example.test/vip/", http_client=http_client),
        credentials_provider=StaticCredentialsProvider(
            api_key="api-key", login="login", password="password"
        ),
    )
    # Ответ-заглушка не совпадает с моделями чтения: проверяется только запрос.
    with contextlib.suppress(ValueError):
        await CALLS[operation](client)
    await client.aclose()
    await http_client.aclose()

    spec = build_default_registry().get(operation)
    assert len(sent) == 1
    assert _placement(sent[0]) == set(spec.request.contract_locations)
