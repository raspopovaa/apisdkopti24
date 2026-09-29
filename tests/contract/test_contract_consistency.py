"""Монолитный контракт и модульный каталог 1.1.60 описывают один документ одинаково.

Обе копии сверяются между собой: раздел документа, имена полей, типы и обязательность
параметров запроса и полей ответа. Расхождение означает, что одна из копий записана с
ошибкой — такую ошибку ранее не ловила ни одна проверка.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest
import yaml

from tools.spec_contract.loader import load_catalog
from tools.spec_contract.models import FieldContract

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MONOLITHIC_CONTRACT = PROJECT_ROOT / "specifications" / "api-contract-v1.1.60.yaml"
CONTRACT_ROOT = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"
IDENTIFIER = re.compile(r"[A-Za-z_]\w*")

# Строка таблицы документа, которая не является полем ответа: в «Статистике» ключи
# объекта methods — коды методов, а `name` — заглушка «Метод – количество вызовов».
DOCUMENT_PLACEHOLDERS = {("get_info", "response", "name")}

FieldMap = dict[str, set[tuple[str, bool]]]


@pytest.fixture(scope="module")
def contract_catalog():
    return load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)


def _monolithic_fields(items: list[dict[str, Any]] | None) -> FieldMap:
    fields: FieldMap = defaultdict(set)
    for item in items or []:
        name = str(item.get("name", ""))
        if IDENTIFIER.fullmatch(name):
            fields[name].add((str(item.get("type", "")).lower(), bool(item.get("required"))))
    return dict(fields)


def _modular_fields(items: tuple[FieldContract, ...], *, response: bool) -> FieldMap:
    fields: FieldMap = defaultdict(set)
    for item in items:
        path = item.path
        if response:
            path = path.removeprefix("data.")
        name = path.replace("[]", "").split(".")[-1]
        if IDENTIFIER.fullmatch(name):
            fields[name].add((item.api_type.lower(), bool(item.required)))
    return dict(fields)


def _without_placeholders(operation: str, kind: str, fields: FieldMap) -> FieldMap:
    return {
        name: types
        for name, types in fields.items()
        if (operation, kind, name) not in DOCUMENT_PLACEHOLDERS
    }


def test_monolithic_contract_matches_modular_catalog(contract_catalog):
    methods = yaml.safe_load(MONOLITHIC_CONTRACT.read_text(encoding="utf-8"))["methods"]
    problems: list[str] = []
    checked = 0
    for method in methods:
        api = method.get("api") or {}
        operation = contract_catalog.operations.get(method["operation"])
        if api.get("section") is None or operation is None:
            continue
        variant = next(
            (item for item in operation.variants if item.route_name == method["route_name"]),
            operation.variants[0] if len(operation.variants) == 1 else None,
        )
        key = f"{method['operation']}[{method['route_name']}]"
        if variant is None:
            problems.append(f"{key}: в модульном каталоге нет варианта маршрута")
            continue
        checked += 1
        if api["section"] != variant.source_section:
            problems.append(f"{key}: раздел {api['section']!r} != {variant.source_section!r}")
        for kind, monolithic_key, modular_items, response in (
            ("request", "request_parameters", variant.request_parameters, False),
            ("response", "response_fields", variant.response_fields, True),
        ):
            monolithic = _without_placeholders(
                method["operation"], kind, _monolithic_fields(api.get(monolithic_key))
            )
            modular = _without_placeholders(
                method["operation"], kind, _modular_fields(modular_items, response=response)
            )
            if response and "data" not in monolithic:
                # Ответ «При успехе передается true» монолитный файл хранит текстом строки,
                # а модульный — полем `data`.
                modular.pop("data", None)
            for name in sorted(set(monolithic) | set(modular)):
                if monolithic.get(name) != modular.get(name):
                    problems.append(
                        f"{key} {kind} {name}: монолитный {sorted(monolithic.get(name, ()))}, "
                        f"модульный {sorted(modular.get(name, ()))}"
                    )

    assert checked >= 80
    assert not problems, "\n".join(problems)
