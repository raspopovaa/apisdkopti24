"""Формы реальных ответов API, которые расходятся со спецификацией 1.1.60.

Значения синтетические; сохранена только структура, полученная от API.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from apisdkopti24.executor import OperationExecutor
from apisdkopti24.models.dictionaries import AzsItemV2
from apisdkopti24.registry import build_default_registry

FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"
REGISTRY = build_default_registry()


def fixture(domain: str, name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / domain / name).read_text(encoding="utf-8"))


def decode(operation: str, payload: dict[str, Any]) -> Any:
    return OperationExecutor.decode_response(REGISTRY.get(operation), payload)


def test_transaction_without_storno_has_null_stor_transaction_id() -> None:
    payload = copy.deepcopy(fixture("transactions", "get_card_transactions_v2.success.json"))
    for item in payload["data"]["result"]:
        item["stor_transaction_id"] = None

    response = decode("get_card_transactions_v2", payload)

    assert all(item.stor_transaction_id is None for item in response.data.result)


def test_card_detail_accepts_null_transaction_timeout_type() -> None:
    payload = copy.deepcopy(fixture("cards", "get_card_detail.success.json"))
    payload["data"]["result"][0]["transaction_timeout"] = {"type": None, "value": 0}

    response = decode("get_card_detail", payload)

    timeout = response.data.result[0].transaction_timeout
    assert timeout is not None and timeout.type is None and timeout.value == 0


def test_dictionary_numeric_ids_become_strings() -> None:
    payload = {
        "status": {"code": 200},
        "data": {"total_count": 2, "result": [{"id": 84, "name": "Мойка"}, {"id": "LIT"}]},
        "timestamp": 1,
    }

    response = decode("get_dictionary", payload)

    assert [item.id for item in response.data.result] == ["84", "LIT"]


def test_azs_v2_accepts_null_utc_timezone() -> None:
    station = AzsItemV2.model_validate(
        {
            "id": "1-POI",
            "siebel_id": "RF000000",
            "status": "257",
            "own_type_name": "Собственная",
            "own_type_code": "1",
            "utc_timezone": None,
            "country_name": None,
            "country_code": None,
            "search_txt": None,
            "accept_cards": None,
        }
    )

    assert station.utc_timezone is None
