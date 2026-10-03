"""Формы реальных ответов API, которые расходятся со спецификацией 1.1.60.

Каждый случай берёт пример ответа из спецификации и вносит одно отличие, наблюдавшееся
в ответах рабочего API или DEMO-стенда. Значения синтетические; сохранена только
структура. Перечень расхождений — в docs/spec-compatibility.md.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from apisdkopti24.executor import OperationExecutor
from apisdkopti24.models.dictionaries import AzsItemV2
from apisdkopti24.registry import build_default_registry

FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"
REGISTRY = build_default_registry()

Payload = dict[str, Any]


def fixture(domain: str, name: str) -> Payload:
    return copy.deepcopy(json.loads((FIXTURES / domain / name).read_text(encoding="utf-8")))


def decode(operation: str, payload: Payload) -> Any:
    return OperationExecutor.decode_response(REGISTRY.get(operation), payload)


def results(payload: Payload) -> list[Payload]:
    data = payload["data"]
    return data["result"] if isinstance(data, dict) else data


# --- изменения ответов ---------------------------------------------------------------


def transactions_as_numbers(payload: Payload) -> Payload:
    for item in results(payload):
        item.update(
            id=9000000001,
            check_id=127000000001,
            stor_transaction_id=None,
            price=54.9,
            price_no_discount=56.1,
            sum=100.5,
            sum_no_discount=102.7,
            discount=2.2,
            qty=12.5,
            exchange_rate=1,
        )
    return payload


def manual_correction_without_typo(payload: Payload) -> Payload:
    for item in results(payload):
        item.pop("is_manual_corrention", None)
        item["is_manual_correction"] = True
    return payload


def invoice_values_as_strings(payload: Payload) -> Payload:
    for item in results(payload):
        item.update(
            amount="1500.00",
            currency="810",
            date_end="2026-10-14",
            last_update="2026-09-30 10:00:00",
        )
    return payload


def user_field_types(payload: Payload) -> Payload:
    for user in results(payload):
        user["date"] = None
        for item in (user.get("cards") or []) + (user.get("contracts") or []):
            item["available"] = True
    return payload


def users_without_contract_cards_count(payload: Payload) -> Payload:
    for user in results(payload):
        for contract in user.get("contracts") or []:
            contract.pop("cards_count", None)
    return payload


def user_card_without_product_and_status(payload: Payload) -> Payload:
    user = next(user for user in results(payload) if user.get("cards"))
    user["cards"][0].update(product=None, status=None)
    return payload


def invite_card_without_product_and_status(payload: Payload) -> Payload:
    invite = next(invite for invite in results(payload) if invite.get("cards"))
    invite["cards"][0].update(product=None, status=None, status_name="")
    return payload


def card_group_status_null(payload: Payload) -> Payload:
    results(payload)[0]["status"] = None
    return payload


def lowercase_is_dealer(payload: Payload) -> Payload:
    payload["data"]["is_dealer"] = payload["data"].pop("Is_dealer")
    return payload


def driver_role_as_string(payload: Payload) -> Payload:
    results(payload)[0]["role"] = "Driver"
    return payload


def report_parameter_without_label(payload: Payload) -> Payload:
    results(payload)[0]["parameters"][0]["label"] = None
    return payload


def cards_v1_without_offline_auth_type_and_expiry(payload: Payload) -> Payload:
    for card in results(payload):
        for field in ("can_work_offline", "card_auth_type", "date_expired"):
            card.pop(field, None)
    return payload


def detail_card_auth_type_null(payload: Payload) -> Payload:
    results(payload)[0]["card_auth_type"] = None
    return payload


def detail_timeout_type_null(payload: Payload) -> Payload:
    results(payload)[0]["transaction_timeout"] = {"type": None, "value": 0}
    return payload


def detail_timeout_type_letter(payload: Payload) -> Payload:
    results(payload)[0]["transaction_timeout"] = {"type": "H", "value": 1}
    return payload


def transaction_without_date(payload: Payload) -> Payload:
    for item in results(payload):
        item.pop("date", None)
    return payload


def transaction_without_storno(payload: Payload) -> Payload:
    for item in results(payload):
        item["stor_transaction_id"] = None
    return payload


# --- проверки разобранного ответа ---------------------------------------------------


def first(response: Any) -> Any:
    data = response.data
    return (data.result if hasattr(data, "result") else data)[0]


FromFixture = tuple[str, str, str, Callable[[Payload], Payload], Callable[[Any], bool]]

FIXTURE_CASES: dict[str, FromFixture] = {
    "транзакции v2: id и суммы числами, stor null": (
        "transactions",
        "get_transactions_v2.success.json",
        "get_transactions_v2",
        transactions_as_numbers,
        lambda r: first(r).id == 9000000001 and first(r).stor_transaction_id is None,
    ),
    "транзакции по карте: id и суммы числами": (
        "transactions",
        "get_card_transactions_v2.success.json",
        "get_card_transactions_v2",
        transactions_as_numbers,
        lambda r: first(r).check_id == 127000000001,
    ),
    "детали транзакции: id и суммы числами": (
        "transactions",
        "get_transaction_detail.success.json",
        "get_transaction_detail",
        transactions_as_numbers,
        lambda r: first(r).id == 9000000001,
    ),
    "транзакции по карте: без сторно stor_transaction_id = null": (
        "transactions",
        "get_card_transactions_v2.success.json",
        "get_card_transactions_v2",
        transaction_without_storno,
        lambda r: all(item.stor_transaction_id is None for item in r.data.result),
    ),
    "транзакции v2: is_manual_correction без опечатки": (
        "transactions",
        "get_transactions_v2.success.json",
        "get_transactions_v2",
        manual_correction_without_typo,
        lambda r: first(r).is_manual_correction is True,
    ),
    "детали транзакции: нет date": (
        "transactions",
        "get_transaction_detail.success.json",
        "get_transaction_detail",
        transaction_without_date,
        lambda r: all(item.date is None for item in r.data.result),
    ),
    "счета: суммы и даты строками": (
        "contracts",
        "get_invoices.success.json",
        "get_invoices",
        invoice_values_as_strings,
        lambda r: first(r) is not None,
    ),
    "договор: is_dealer вместо Is_dealer": (
        "contracts",
        "get_contract_data.success.json",
        "get_contract_data",
        lowercase_is_dealer,
        lambda r: r.data is not None,
    ),
    "пользователи: available bool, date null": (
        "users",
        "get_users.success.json",
        "get_users",
        user_field_types,
        lambda r: first(r).date is None,
    ),
    "пользователи: у договора нет cards_count": (
        "users",
        "get_users.success.json",
        "get_users",
        users_without_contract_cards_count,
        lambda r: all(
            contract.cards_count is None for user in r.data.result for contract in user.contracts
        ),
    ),
    "пользователи: у карты product и status = null": (
        "users",
        "get_users.success.json",
        "get_users",
        user_card_without_product_and_status,
        lambda r: next(u for u in r.data.result if u.cards).cards[0].product is None,
    ),
    "приглашения: у карты product и status = null": (
        "invites",
        "get_invites.success.json",
        "get_invites",
        invite_card_without_product_and_status,
        lambda r: next(i for i in r.data.result if i.cards).cards[0].status is None,
    ),
    "группы карт: status = null, пока группа синхронизируется": (
        "card_groups",
        "get_card_groups.success.json",
        "get_card_groups",
        card_group_status_null,
        lambda r: first(r).status is None,
    ),
    "водители по карте: role строкой": (
        "cards",
        "get_card_drivers.success.json",
        "get_card_drivers",
        driver_role_as_string,
        lambda r: first(r).role == "Driver",
    ),
    "отчёты: parameters[].label = null": (
        "reports",
        "get_reports.success.json",
        "get_reports",
        report_parameter_without_label,
        lambda r: first(r).parameters[0].label is None,
    ),
    "карты v1: нет can_work_offline, card_auth_type, date_expired": (
        "cards",
        "get_cards_v1.success.json",
        "get_cards_v1",
        cards_v1_without_offline_auth_type_and_expiry,
        lambda r: first(r).can_work_offline is None and first(r).date_expired is None,
    ),
    "детали карты: card_auth_type = null": (
        "cards",
        "get_card_detail.success.json",
        "get_card_detail",
        detail_card_auth_type_null,
        lambda r: first(r).card_auth_type is None,
    ),
    "детали карты: transaction_timeout.type = null": (
        "cards",
        "get_card_detail.success.json",
        "get_card_detail",
        detail_timeout_type_null,
        lambda r: first(r).transaction_timeout.type is None,
    ),
    "детали карты: transaction_timeout.type буквой": (
        "cards",
        "get_card_detail.success.json",
        "get_card_detail",
        detail_timeout_type_letter,
        lambda r: first(r).transaction_timeout.type == "H",
    ),
}


@pytest.mark.parametrize(
    ("domain", "name", "operation", "mutate", "check"),
    FIXTURE_CASES.values(),
    ids=FIXTURE_CASES.keys(),
)
def test_live_response_shape_is_accepted(
    domain: str,
    name: str,
    operation: str,
    mutate: Callable[[Payload], Payload],
    check: Callable[[Any], bool],
) -> None:
    response = decode(operation, mutate(fixture(domain, name)))

    assert check(response)


INLINE_CASES: dict[str, tuple[str, Payload, Any]] = {
    "справочник: числовой id становится строкой": (
        "get_dictionary",
        {
            "status": {"code": 200},
            "data": {"total_count": 2, "result": [{"id": 84, "name": "Мойка"}, {"id": "LIT"}]},
            "timestamp": 1,
        },
        ["84", "LIT"],
    ),
    "товарный ограничитель: числовой ID становится строкой": (
        "set_restriction",
        {"status": {"code": 200}, "data": [449000001, "449000002"], "timestamp": 1},
        ["449000001", "449000002"],
    ),
}


@pytest.mark.parametrize(
    ("operation", "payload", "expected"), INLINE_CASES.values(), ids=INLINE_CASES.keys()
)
def test_numeric_identifiers_become_strings(
    operation: str, payload: Payload, expected: Any
) -> None:
    data = decode(operation, payload).data
    values = [item.id for item in data.result] if hasattr(data, "result") else data

    assert values == expected


AZS_V2_STATION: Payload = {
    "id": "123456",
    "siebel_id": "1-3XYZ123",
    "status": "257",
    "own_type_name": "Собственная",
    "own_type_code": "1",
    "utc_timezone": None,
    "country_name": None,
    "country_code": None,
    "search_txt": None,
    "accept_cards": None,
}

AZS_V2_CASES: dict[str, Payload] = {
    "utc_timezone = null": {},
    "пустые группы услуг — []": {
        "electric_charging_station": [],
        "adblue": [],
        "services_with_card": [],
        "services_without_card": [],
    },
    "коды услуг строками": {
        "adblue": {"name": "AdBlue", "items": [{"code": "123", "name": "AdBlue", "sort": 1}]},
    },
}


@pytest.mark.parametrize("changes", AZS_V2_CASES.values(), ids=AZS_V2_CASES.keys())
def test_azs_v2_station_shape_is_accepted(changes: Payload) -> None:
    station = AzsItemV2.model_validate({**AZS_V2_STATION, **changes})

    assert station.id == "123456"
    assert station.utc_timezone is None
