"""Монолитный контракт и модульный каталог 1.1.60 описывают один документ одинаково.

Обе копии сверяются между собой: одинаковый набор маршрутов, раздел документа и
построчно, в порядке документа, имена, типы и обязательность параметров запроса и полей
ответа. Построчное сравнение не даёт двум одноимённым полям разных объектов обменяться
типами незаметно. Расхождение означает, что одна из копий записана с ошибкой.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tools.spec_contract.loader import load_catalog
from tools.spec_contract.models import ContractCatalog, FieldContract, VariantContract

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MONOLITHIC_CONTRACT = PROJECT_ROOT / "specifications" / "api-contract-v1.1.60.yaml"
CONTRACT_ROOT = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"
IDENTIFIER = re.compile(r"[A-Za-z_]\w*")

# Монолитный контракт хранит имена маршрутов реестра SDK (их проверяет
# verify_api_contract.py), модульный каталог — единственный вариант документа под именем
# default. Других расхождений в именах маршрутов нет.
ROUTE_ALIASES = {
    ("update_template", "put"): "default",
    ("update_template_limit", "put"): "default",
    ("update_template_restriction", "put_plural_id"): "default",
    ("delete_template_restriction", "plural_id"): "default",
    ("update_template_georestriction", "put_plural_id"): "default",
    ("delete_template_georestriction", "plural_id"): "default",
}

# Строка таблицы документа, которая не является полем ответа: в «Статистике» ключи
# объекта methods — коды методов, а `name` — заглушка «Метод – количество вызовов».
DOCUMENT_PLACEHOLDERS = {("get_info", "response", "name")}

Row = tuple[str, str, bool]
RouteKey = tuple[str, str]


@pytest.fixture(scope="module")
def contract_catalog() -> ContractCatalog:
    return load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)


def _documented_methods(catalog: ContractCatalog) -> list[dict[str, Any]]:
    methods = yaml.safe_load(MONOLITHIC_CONTRACT.read_text(encoding="utf-8"))["methods"]
    excluded = catalog.manifest.excluded_operations
    return [
        method
        for method in methods
        if (method.get("api") or {}).get("section") and method["operation"] not in excluded
    ]


def _catalog_key(method: dict[str, Any]) -> RouteKey:
    key = (method["operation"], method["route_name"])
    return (key[0], ROUTE_ALIASES.get(key, key[1]))


def _catalog_variants(catalog: ContractCatalog) -> dict[RouteKey, VariantContract]:
    return {
        (operation.name, variant.route_name): variant
        for operation in catalog.iter_operations()
        for variant in operation.variants
    }


def _monolithic_rows(operation: str, kind: str, items: list[dict[str, Any]] | None) -> list[Row]:
    return [
        (name, str(item.get("type", "")).lower(), bool(item.get("required")))
        for item in items or []
        if IDENTIFIER.fullmatch(name := str(item.get("name", "")))
        and (operation, kind, name) not in DOCUMENT_PLACEHOLDERS
    ]


def _modular_rows(items: tuple[FieldContract, ...], *, response: bool) -> list[Row]:
    rows: list[Row] = []
    for item in items:
        path = item.path.removeprefix("data.") if response else item.path
        name = path.replace("[]", "").split(".")[-1]
        if IDENTIFIER.fullmatch(name):
            rows.append((name, item.api_type.lower(), bool(item.required)))
    return rows


def test_route_aliases_are_all_used(contract_catalog):
    keys = {
        (method["operation"], method["route_name"])
        for method in _documented_methods(contract_catalog)
    }
    assert set(ROUTE_ALIASES) <= keys


def test_both_contract_copies_cover_the_same_routes(contract_catalog):
    monolithic = {_catalog_key(method) for method in _documented_methods(contract_catalog)}
    modular = set(_catalog_variants(contract_catalog))

    assert sorted(monolithic - modular) == [], "нет в модульном каталоге"
    assert sorted(modular - monolithic) == [], "нет в монолитном контракте"


def test_monolithic_contract_matches_modular_catalog(contract_catalog):
    variants = _catalog_variants(contract_catalog)
    problems: list[str] = []
    for method in _documented_methods(contract_catalog):
        operation = method["operation"]
        label = f"{operation}[{method['route_name']}]"
        variant = variants.get(_catalog_key(method))
        if variant is None:
            problems.append(f"{label}: в модульном каталоге нет этого маршрута")
            continue
        api = method["api"]
        if api["section"] != variant.source_section:
            problems.append(f"{label}: раздел {api['section']!r} != {variant.source_section!r}")
        for kind, monolithic_key, modular_items, response in (
            ("request", "request_parameters", variant.request_parameters, False),
            ("response", "response_fields", variant.response_fields, True),
        ):
            monolithic = _monolithic_rows(operation, kind, api.get(monolithic_key))
            modular = _modular_rows(modular_items, response=response)
            if response and not any(name == "data" for name, _, _ in monolithic):
                # Ответ «При успехе передается true» монолитный файл хранит текстом строки,
                # а модульный — полем `data`.
                modular = [row for row in modular if row[0] != "data"]
            if monolithic != modular:
                position = next(
                    index
                    for index in range(max(len(monolithic), len(modular)))
                    if index >= min(len(monolithic), len(modular))
                    or monolithic[index] != modular[index]
                )
                problems.append(
                    f"{label} {kind}: первое отличие в строке {position + 1}: "
                    f"монолитный {monolithic[position:position + 2]}, "
                    f"модульный {modular[position:position + 2]}"
                )

    assert not problems, "\n".join(problems)
