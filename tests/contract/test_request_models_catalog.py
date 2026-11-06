"""Каталог операций перечисляет модели, которыми метод SDK проверяет вход."""

from __future__ import annotations

import importlib
import inspect
import json
import pkgutil
import re
from pathlib import Path
from types import FunctionType

import apisdkopti24.services as services_package
from apisdkopti24.modeling import StrictRequestModel

CATALOG = Path(__file__).resolve().parents[2] / "specifications" / "operation-catalog.json"


def _service_methods() -> dict[str, tuple[object, FunctionType]]:
    methods: dict[str, tuple[object, FunctionType]] = {}
    for module_info in pkgutil.iter_modules(services_package.__path__):
        module = importlib.import_module(f"{services_package.__name__}.{module_info.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__:
                continue
            for name, function in vars(cls).items():
                if isinstance(function, FunctionType) and not name.startswith("_"):
                    methods.setdefault(name, (module, function))
    return methods


def _strict_models_used(module: object, function: FunctionType) -> set[str]:
    names = set(re.findall(r"\b[A-Z]\w+\b", inspect.getsource(function)))
    return {
        name
        for name in names
        if isinstance(candidate := getattr(module, name, None), type)
        and issubclass(candidate, StrictRequestModel)
    }


def test_catalog_lists_request_models_used_by_service_methods() -> None:
    operations = json.loads(CATALOG.read_text(encoding="utf-8"))["operations"]
    methods = _service_methods()
    mismatches = {}
    for operation in operations:
        module, function = methods[operation["name"]]
        expected = _strict_models_used(module, function)
        declared = set(operation["request"].get("request_models", ()))
        if declared != expected:
            mismatches[operation["name"]] = {"catalog": sorted(declared), "code": sorted(expected)}
    assert mismatches == {}
