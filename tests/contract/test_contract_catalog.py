from __future__ import annotations

from pathlib import Path

import pytest

from tools.spec_contract.loader import load_catalog

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"


@pytest.fixture(scope="session")
def contract_catalog():
    return load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)


def test_contract_catalog_covers_public_non_qr_operations(contract_catalog):
    assert contract_catalog.manifest.source["version"] == "1.1.60"
    assert len(contract_catalog.operations) == 82
    assert contract_catalog.manifest.expected_operation_count == 82
    assert set(contract_catalog.operations).isdisjoint(
        contract_catalog.manifest.excluded_operations
    )


def test_qr_mpc_operations_are_explicitly_excluded(contract_catalog):
    assert contract_catalog.manifest.excluded_operations == {
        "get_mpc_qr_list",
        "delete_mpc",
        "reset_mpc",
        "generate_payment_qr",
        "init_mpc",
        "confirm_mpc",
        "update_mpc",
    }
    normalization = contract_catalog.manifest.source["normalization"]
    assert normalization["qr_specification_used"] is False


def test_source_normalization_records_1160_patch(contract_catalog):
    normalization = contract_catalog.manifest.source["normalization"]
    assert normalization["base_snapshot"]["version"] == "1.1.59"
    changes = [item["change"] for item in normalization["applied_patches"]]
    assert any("is_manual_corrention" in change for change in changes)

    for operation_name in (
        "get_transactions_v2",
        "get_card_transactions_v2",
        "get_transaction_detail",
    ):
        decisions = contract_catalog.operations[operation_name].source_decisions
        assert any("is_manual_corrention" in decision.path for decision in decisions)


def test_every_operation_has_a_service_and_at_least_one_variant(contract_catalog):
    for operation in contract_catalog.iter_operations():
        assert operation.service
        assert operation.variants
        route_names = [variant.route_name for variant in operation.variants]
        assert len(route_names) == len(set(route_names))
