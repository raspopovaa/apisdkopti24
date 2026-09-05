from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from api_client_opti24.registry import MethodRegistry, build_default_registry

EXPECTED_METHOD_FIELDS = {
    "external_code",
    "operation",
    "route_name",
    "http_method",
    "api_version",
    "endpoint",
    "demo_available",
    "billable",
}
OPTIONAL_METHOD_FIELDS = {"source_http_method", "known_discrepancy"}


@dataclass(frozen=True, slots=True)
class ExternalMethodContract:
    external_code: str
    operation: str
    route_name: str
    http_method: str
    api_version: str
    endpoint: str
    demo_available: bool
    billable: bool
    source_http_method: str | None = None
    known_discrepancy: str | None = None


class ContractMismatchError(AssertionError):
    pass


def _required_string(item: dict[str, Any], field: str, index: int) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ContractMismatchError(f"Method #{index}: {field} must be a non-empty string")
    return value.strip()


def _required_bool(item: dict[str, Any], field: str, index: int) -> bool:
    value = item.get(field)
    if not isinstance(value, bool):
        raise ContractMismatchError(f"Method #{index}: {field} must be a boolean")
    return value


def _parse_method(item: object, index: int) -> ExternalMethodContract:
    if not isinstance(item, dict):
        raise ContractMismatchError(f"Method #{index} must be a mapping")
    fields = set(item)
    missing = EXPECTED_METHOD_FIELDS - fields
    unexpected = fields - EXPECTED_METHOD_FIELDS - OPTIONAL_METHOD_FIELDS
    if missing or unexpected:
        raise ContractMismatchError(
            f"Method #{index} has invalid fields; "
            f"missing={sorted(missing)}, unexpected={sorted(unexpected)}"
        )

    source_http_method = item.get("source_http_method")
    known_discrepancy = item.get("known_discrepancy")
    if (source_http_method is None) != (known_discrepancy is None):
        raise ContractMismatchError(
            f"Method #{index}: source_http_method and known_discrepancy must be set together"
        )
    if source_http_method is not None and (
        not isinstance(source_http_method, str) or not source_http_method.strip()
    ):
        raise ContractMismatchError(
            f"Method #{index}: source_http_method must be a non-empty string"
        )
    if known_discrepancy is not None and (
        not isinstance(known_discrepancy, str) or not known_discrepancy.strip()
    ):
        raise ContractMismatchError(
            f"Method #{index}: known_discrepancy must be a non-empty string"
        )

    return ExternalMethodContract(
        external_code=_required_string(item, "external_code", index),
        operation=_required_string(item, "operation", index),
        route_name=_required_string(item, "route_name", index),
        http_method=_required_string(item, "http_method", index).upper(),
        api_version=_required_string(item, "api_version", index),
        endpoint=_required_string(item, "endpoint", index),
        demo_available=_required_bool(item, "demo_available", index),
        billable=_required_bool(item, "billable", index),
        source_http_method=(
            source_http_method.strip().upper() if isinstance(source_http_method, str) else None
        ),
        known_discrepancy=(
            known_discrepancy.strip() if isinstance(known_discrepancy, str) else None
        ),
    )


def load_external_contract(path: Path) -> tuple[ExternalMethodContract, ...]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ContractMismatchError("Contract root must be a mapping")
    if document.get("schema_version") != 1:
        raise ContractMismatchError("Unsupported or missing contract schema_version")
    methods = document.get("methods")
    if not isinstance(methods, list):
        raise ContractMismatchError("Contract methods must be a list")

    contracts = tuple(_parse_method(item, index) for index, item in enumerate(methods, 1))
    codes = [contract.external_code for contract in contracts]
    duplicate_codes = sorted(code for code, count in Counter(codes).items() if count > 1)
    route_keys = [(contract.operation, contract.route_name) for contract in contracts]
    duplicate_routes = sorted(key for key, count in Counter(route_keys).items() if count > 1)
    if duplicate_codes:
        raise ContractMismatchError("Duplicate external_code values: " + ", ".join(duplicate_codes))
    if duplicate_routes:
        raise ContractMismatchError(
            "Duplicate operation/route_name bindings: "
            + ", ".join(f"{operation}/{route}" for operation, route in duplicate_routes)
        )
    return contracts


def _registry_contracts(registry: MethodRegistry) -> dict[str, ExternalMethodContract]:
    contracts: dict[str, ExternalMethodContract] = {}
    for spec in registry.list_all():
        for route in spec.iter_routes():
            if route.external_code is None:
                continue
            if route.billable is None:
                raise ContractMismatchError(
                    f"Registry route {spec.name}/{route.name} has external_code without billable"
                )
            if route.external_code in contracts:
                raise ContractMismatchError(
                    f"Registry contains duplicate external_code {route.external_code!r}"
                )
            contracts[route.external_code] = ExternalMethodContract(
                external_code=route.external_code,
                operation=spec.name,
                route_name=route.name,
                http_method=route.http_method,
                api_version=route.api_version,
                endpoint=route.endpoint,
                demo_available=route.demo_available,
                billable=route.billable,
            )
    return contracts


def verify_registry_against_external_contract(
    path: Path,
    *,
    registry: MethodRegistry | None = None,
) -> tuple[ExternalMethodContract, ...]:
    external_contracts = load_external_contract(path)
    expected_by_code = {contract.external_code: contract for contract in external_contracts}
    registry_by_code = _registry_contracts(registry or build_default_registry())

    missing_codes = sorted(set(expected_by_code) - set(registry_by_code))
    unexpected_codes = sorted(set(registry_by_code) - set(expected_by_code))
    if missing_codes or unexpected_codes:
        raise ContractMismatchError(
            f"External code mismatch; missing={missing_codes}, unexpected={unexpected_codes}"
        )

    mismatches: list[str] = []
    for external_code, expected in expected_by_code.items():
        actual = registry_by_code[external_code]
        comparable_expected = ExternalMethodContract(
            external_code=expected.external_code,
            operation=expected.operation,
            route_name=expected.route_name,
            http_method=expected.http_method,
            api_version=expected.api_version,
            endpoint=expected.endpoint,
            demo_available=expected.demo_available,
            billable=expected.billable,
        )
        if actual != comparable_expected:
            mismatches.append(f"{external_code}: expected={comparable_expected}, actual={actual}")
    if mismatches:
        raise ContractMismatchError("Registry contract mismatches:\n" + "\n".join(mismatches))
    return external_contracts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify EndpointSpec metadata against the independent YAML contract"
    )
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    methods = verify_registry_against_external_contract(args.contract)
    discrepancies = sum(method.known_discrepancy is not None for method in methods)
    print(
        f"Verified {len(methods)} external API methods against the registry "
        f"({discrepancies} documented discrepancies)"
    )


if __name__ == "__main__":
    main()
