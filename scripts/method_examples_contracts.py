"""Чтение контрактов спецификации и таблиц совместимости для страниц примеров.

Модуль генератора scripts/generate_method_examples.py; отдельно не запускается.
"""

import functools
from typing import Any

import yaml
from method_examples_common import API_CONTRACT, COMPATIBILITY_DOC, CONTRACTS_DIR, QR_CONTRACT


@functools.cache
def contract_operations(domain: str) -> dict[str, Any]:
    path = CONTRACTS_DIR / f"{domain}.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8"))["operations"]


@functools.cache
def qr_contract_methods() -> dict[str, dict[str, Any]]:
    loaded = yaml.safe_load(QR_CONTRACT.read_text(encoding="utf-8"))
    return {item["operation"]: item for item in loaded["methods"]}


def _qr_operation(name: str) -> dict[str, Any] | None:
    """Операция из спецификации сервиса QR 1.0.4 в формате модульного контракта."""
    item = qr_contract_methods().get(name)
    if item is None:
        return None
    request = [
        {
            "path": key,
            "api_type": value.get("type", ""),
            "required": value.get("required", False),
            "description": value.get("description", ""),
        }
        for key, value in (item.get("request") or {}).items()
    ]
    response = [
        {
            "path": key if key == "data" or key.startswith("data.") else f"data.{key}",
            "api_type": value.get("type", ""),
            "required": value.get("required", False),
            "description": value.get("description", ""),
        }
        for key, value in ((item.get("response") or {}).get("fields") or {}).items()
    ]
    variant = {
        "route_name": "default",
        "source_section": "Спецификация сервиса API QR 1.0.4",
        "request_line": f"{item['http_method']} /{item['api_version']}/{item['endpoint']}",
        "request_parameters": request,
        "response_fields": response,
        "fixture_corrections": [],
    }
    return {"verification": "qr", "variants": [variant]}


def spec_operation(domain: str, name: str) -> dict[str, Any] | None:
    operation = contract_operations(domain).get(name)
    return operation if operation is not None else _qr_operation(name)


def spec_variant(domain: str, name: str) -> dict[str, Any] | None:
    operation = spec_operation(domain, name)
    if operation is None:
        return None
    variants = operation["variants"]
    return next(
        (variant for variant in variants if variant.get("route_name") == "default"),
        variants[0],
    )


def spec_request_parameters(domain: str, name: str) -> dict[str, dict[str, Any]]:
    variant = spec_variant(domain, name) or {}
    return {item["path"]: item for item in variant.get("request_parameters", [])}


def spec_response_fields(domain: str, name: str) -> dict[str, dict[str, Any]]:
    variant = spec_variant(domain, name) or {}
    return {item["path"]: item for item in variant.get("response_fields", [])}


@functools.cache
def api_contract_methods() -> tuple[dict[str, Any], ...]:
    return tuple(yaml.safe_load(API_CONTRACT.read_text(encoding="utf-8"))["methods"])


def _api_contract_index(name: str) -> int | None:
    for index, item in enumerate(api_contract_methods()):
        if item["operation"] == name and item.get("route_name", "default") == "default":
            return index
    return None


def _compatibility_tables() -> dict[str, list[list[str]]]:
    """Таблицы docs/spec-compatibility.md по заголовкам разделов."""
    tables: dict[str, list[list[str]]] = {}
    section = ""
    for line in COMPATIBILITY_DOC.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.startswith("| `"):
            continue
        cells = [cell.strip().replace("\\|", "|") for cell in line.strip().strip("|").split(" | ")]
        tables.setdefault(section, []).append(cells)
    return tables


def compatibility_rows(name: str) -> list[list[str]]:
    """Расхождения фактических ответов API со спецификацией для метода."""
    rows = _compatibility_tables().get("Расхождения фактических ответов со спецификацией", [])
    return [cells for cells in rows if len(cells) == 5 and f"`{name}`" in cells[0]]


def request_compatibility_rows(name: str) -> list[list[str]]:
    """Подтверждённые расхождения запросов со спецификацией для метода."""
    rows = _compatibility_tables().get("Расхождения фактических запросов со спецификацией", [])
    return [cells for cells in rows if len(cells) == 5 and cells[0] == f"`{name}`"]
