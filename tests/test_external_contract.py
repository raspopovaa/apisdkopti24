from dataclasses import replace
from pathlib import Path

import pytest

from api_client_opti24.registry import MethodRegistry, build_default_registry
from scripts.verify_external_contract import (
    ContractMismatchError,
    load_external_contract,
    verify_registry_against_external_contract,
)

EXTERNAL_CONTRACT_PATH = Path("specifications/api-methods.yaml")


def test_registry_matches_independent_external_contract() -> None:
    methods = verify_registry_against_external_contract(EXTERNAL_CONTRACT_PATH)

    assert len(methods) == 91
    assert len({method.external_code for method in methods}) == 91
    assert len({(method.operation, method.route_name) for method in methods}) == 91


def test_known_specification_discrepancies_are_explicit() -> None:
    methods = load_external_contract(EXTERNAL_CONTRACT_PATH)
    discrepancies = {
        method.external_code: method for method in methods if method.known_discrepancy is not None
    }

    assert set(discrepancies) == {"calculate_prices", "check_purchase"}
    assert all(method.source_http_method == "GET" for method in discrepancies.values())
    assert all(method.http_method == "POST" for method in discrepancies.values())


def test_external_code_prevents_ambiguous_same_route_matching() -> None:
    registry = build_default_registry()
    cards_v1 = registry.get("get_cards_v1")
    card_detail = registry.get("get_card_detail")
    modified = {
        spec.name: spec
        for spec in registry.list_all()
        if spec.name not in {cards_v1.name, card_detail.name}
    }
    modified[cards_v1.name] = replace(
        cards_v1,
        external_code=card_detail.external_code,
        billable=card_detail.billable,
    )
    modified[card_detail.name] = replace(
        card_detail,
        external_code=cards_v1.external_code,
        billable=cards_v1.billable,
    )

    with pytest.raises(ContractMismatchError, match="Registry contract mismatches"):
        verify_registry_against_external_contract(
            EXTERNAL_CONTRACT_PATH,
            registry=MethodRegistry(modified),
        )


def test_tariff_mismatch_fails_contract_verification() -> None:
    registry = build_default_registry()
    cards_v2 = registry.get("get_cards_v2")
    modified = {spec.name: spec for spec in registry.list_all()}
    modified[cards_v2.name] = replace(cards_v2, billable=not cards_v2.billable)

    with pytest.raises(ContractMismatchError, match="Registry contract mismatches"):
        verify_registry_against_external_contract(
            EXTERNAL_CONTRACT_PATH,
            registry=MethodRegistry(modified),
        )
