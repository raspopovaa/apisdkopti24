from __future__ import annotations

import json
from pathlib import Path
from string import Formatter

from apisdkopti24.registry import build_default_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "specifications" / "request-matrix-v1.1.60.json"

QR_OPERATIONS = frozenset(
    {
        "confirm_mpc",
        "delete_mpc",
        "generate_payment_qr",
        "get_card_drivers",
        "get_card_transactions_v2",
        "get_mpc_qr_list",
        "get_transaction_detail",
        "get_transactions_v2",
        "init_mpc",
        "reset_mpc",
        "reset_pin",
        "update_mpc",
        "verify_pin",
    }
)


def _path_values(endpoint: str) -> dict[str, str]:
    return {
        field_name: f"value-{field_name}"
        for _, field_name, _, _ in Formatter().parse(endpoint)
        if field_name is not None
    }


def export_request_matrix() -> list[dict[str, object]]:
    matrix: list[dict[str, object]] = []
    for operation in sorted(build_default_registry().list_all(), key=lambda item: item.name):
        route = operation.resolve_route()
        path_values = _path_values(route.endpoint)
        contract_locations = sorted(operation.request.contract_locations)
        query: dict[str, object] = {"probe": "value"} if operation.request.has_query else {}
        form: dict[str, object] | None = (
            {"probe": "value"} if operation.request.body_kind == "form" else None
        )
        json_body: dict[str, object] | None = (
            {"probe": "value"} if operation.request.body_kind == "json" else None
        )
        if "query" in contract_locations:
            query["contract_id"] = "contract-1"
        if "form" in contract_locations and form is not None:
            form["contract_id"] = "contract-1"
        if "json" in contract_locations and json_body is not None:
            json_body["contract_id"] = "contract-1"
        matrix.append(
            {
                "operation": operation.name,
                "source_contract": (
                    "api-qr-contract-v1.0.4.yaml"
                    if operation.name in QR_OPERATIONS
                    else "api-contract-v1.1.60.yaml"
                ),
                "method": route.http_method,
                "api_version": route.api_version,
                "endpoint": route.render(path_values),
                "path_params": path_values,
                "query": query,
                "form": form,
                "json_body": json_body,
                "contract_locations": contract_locations,
                "request_models": list(operation.request.request_models),
                "contract_header": "contract-1" if "header" in contract_locations else None,
                "content_type": (
                    "application/json"
                    if json_body is not None
                    else "application/x-www-form-urlencoded" if form is not None else None
                ),
            }
        )
    return matrix


def main() -> None:
    OUTPUT.write_text(
        json.dumps(export_request_matrix(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Exported request matrix for {len(export_request_matrix())} operations to {OUTPUT}")


if __name__ == "__main__":
    main()
