from __future__ import annotations

import json
import sys
from pathlib import Path
from string import Formatter

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for path in (PROJECT_ROOT, SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from apisdkopti24.registry import build_default_registry  # noqa: E402
from tools.spec_contract import load_catalog  # noqa: E402

OUTPUT = PROJECT_ROOT / "specifications" / "model-matrix-v1.1.60.json"
MARKDOWN_OUTPUT = PROJECT_ROOT / "docs" / "reference" / "model-matrix.md"
CONTRACT_ROOT = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"
QR_CONTRACT = PROJECT_ROOT / "specifications" / "api-qr-contract-v1.0.4.yaml"


def _field(
    path: str, api_type: str, required: bool | None, description: str, location: str
) -> dict[str, object]:
    field: dict[str, object] = {
        "path": path,
        "type": api_type,
        "required": required if required is not None else "conditional",
        "description": description,
        "location": location,
    }
    if required is None:
        field["required_condition"] = description
    return field


def _request_location(operation: object, route: object, path: str) -> str:
    name = path.split(".", 1)[0].removesuffix("[]")
    placeholders = {
        field for _, field, _, _ in Formatter().parse(route.endpoint) if field is not None
    }
    if name in placeholders:
        return "path"
    if name == "contract_id":
        locations = operation.request.contract_locations
        for candidate in ("query", "form", "json", "header"):
            if candidate in locations:
                return candidate
    if route.http_method == "GET" or operation.request.has_query:
        return "query"
    return operation.request.body_kind


def export_model_matrix() -> dict[str, object]:
    registry = {item.name: item for item in build_default_registry().list_all()}
    catalog = load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)
    operations: list[dict[str, object]] = []
    common = [
        _field(field.path, field.api_type, field.required, field.description, "response")
        for field in catalog.manifest.common_response_fields
    ]
    for contract in catalog.iter_operations():
        operation = registry[contract.name]
        variants: list[dict[str, object]] = []
        for variant in contract.variants:
            route = operation.resolve_route(route_name=variant.route_name)
            variants.append(
                {
                    "route_name": variant.route_name,
                    "method": route.http_method,
                    "version": route.api_version,
                    "path": route.endpoint,
                    "request": [
                        _field(
                            field.path,
                            field.api_type,
                            field.required,
                            field.description,
                            _request_location(operation, route, field.path),
                        )
                        for field in variant.request_parameters
                    ],
                    "response": common
                    + [
                        _field(
                            field.path,
                            field.api_type,
                            field.required,
                            field.description,
                            "response",
                        )
                        for field in variant.response_fields
                    ],
                }
            )
        operations.append(
            {
                "operation": contract.name,
                "source": "api-corporate-client-1.1.60.sanitized.docx",
                "verification": contract.verification,
                "response_model": getattr(operation.response_type, "__name__", None)
                or operation.response_kind,
                "variants": variants,
            }
        )

    qr = yaml.safe_load(QR_CONTRACT.read_text(encoding="utf-8"))
    for method in qr["methods"]:
        operation = registry[method["operation"]]
        route = operation.resolve_route()
        request = []
        for name, value in method.get("request", {}).items():
            request.append(
                _field(
                    name,
                    value["type"],
                    value["required"],
                    value.get("description", ""),
                    value.get("location") or _request_location(operation, route, name),
                )
            )
        response = common.copy()
        for name, value in method.get("response", {}).get("fields", {}).items():
            path = name if name.startswith(("status", "data", "timestamp")) else f"data.{name}"
            response.append(
                _field(path, value["type"], value["required"], value["description"], "response")
            )
        operations.append(
            {
                "operation": operation.name,
                "source": "api-qr-corporate-clients-1.0.4.sanitized.docx",
                "verification": "verified",
                "response_model": getattr(operation.response_type, "__name__", None)
                or operation.response_kind,
                "variants": [
                    {
                        "route_name": "default",
                        "method": route.http_method,
                        "version": route.api_version,
                        "path": route.endpoint,
                        "request": request,
                        "response": response,
                    }
                ],
            }
        )

    operations.sort(key=lambda item: str(item["operation"]))
    return {
        "schema_version": 1,
        "corporate_contract": "1.1.60",
        "qr_contract": "1.0.4",
        "operation_count": len(operations),
        "operations": operations,
    }


def main() -> None:
    matrix = export_model_matrix()
    OUTPUT.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Матрица моделей API",
        "",
        "Матрица сформирована из спецификаций корпоративного API 1.1.60 и QR API 1.0.4. "
        "Значение `conditional` означает условную обязательность, описанную в соседней колонке.",
        "",
    ]
    for operation in matrix["operations"]:
        lines.extend([f"## `{operation['operation']}`", ""])
        for variant in operation["variants"]:
            lines.extend(
                [
                    f"`{variant['method']} /{variant['version']}/{variant['path']}`",
                    "",
                    "### Запрос",
                    "",
                    "| Путь | Расположение | Тип | Обяз. | Описание |",
                    "|---|---|---|---|---|",
                ]
            )
            for field in variant["request"]:
                description = str(field["description"]).replace("|", "\\|")
                lines.append(
                    f"| `{field['path']}` | {field['location']} | `{field['type']}` | "
                    f"{field['required']} | {description} |"
                )
            if not variant["request"]:
                lines.append("| — | — | — | — | Параметры метода отсутствуют |")
            lines.extend(
                [
                    "",
                    "### Ответ",
                    "",
                    "| Путь | Тип | Обяз. | Описание |",
                    "|---|---|---|---|",
                ]
            )
            for field in variant["response"]:
                description = str(field["description"]).replace("|", "\\|")
                lines.append(
                    f"| `{field['path']}` | `{field['type']}` | {field['required']} | {description} |"
                )
            lines.append("")
    MARKDOWN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Exported model matrix for {matrix['operation_count']} operations to {OUTPUT}")


if __name__ == "__main__":
    main()
