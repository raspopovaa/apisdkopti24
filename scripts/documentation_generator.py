from __future__ import annotations

import importlib
import inspect
import pkgutil
import re
import sys
from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

import yaml
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
DOCS_PATH = PROJECT_ROOT / "docs"
METHODS_PATH = DOCS_PATH / "methods"
DATA_TYPES_PATH = DOCS_PATH / "data-types"
METADATA_PATH = PROJECT_ROOT / "specifications" / "documentation.yaml"
PARAMETER_METADATA_PATH = PROJECT_ROOT / "specifications" / "parameter-descriptions-1.1.60.yaml"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from pydantic_docs import render_model_page, render_return_details

from api_client_opti24.modeling import (
    APIEnvelope,
    ResponseModel,
    ResponseStatus,
    StrictRequestModel,
)
from api_client_opti24.modeling import BaseModel as SDKBaseModel
from api_client_opti24.registry import build_default_registry
from api_client_opti24.service_groups import ServiceContainer

PACKAGE_NAME = "api_client_opti24"
EXCLUDED_MODULES = {"api_client_opti24.logger"}

EXCLUDED_OPERATIONS: set[str] = set()

SERVICE_NAMES = {
    "auth": "auth",
    "card_group": "card_groups",
    "cards": "cards",
    "contract": "contracts",
    "dictionaries": "dictionaries",
    "ewallet": "ewallet",
    "final_prices": "final_prices",
    "invites": "invites",
    "limits": "limits",
    "region_limits": "region_limits",
    "reports": "reports",
    "restrictions": "restrictions",
    "templates": "templates",
    "transactions": "transactions",
    "users": "users",
    "virtual_cards": "virtual_cards",
}


def load_metadata() -> dict[str, Any]:
    if not METADATA_PATH.exists():
        return {"domains": {}, "operations": {}, "parameters": {}}

    value = yaml.safe_load(METADATA_PATH.read_text(encoding="utf-8")) or {}
    operations = value.get("operations", {})
    if PARAMETER_METADATA_PATH.exists():
        parameter_value = yaml.safe_load(PARAMETER_METADATA_PATH.read_text(encoding="utf-8")) or {}
        for operation, operation_meta in parameter_value.get("operations", {}).items():
            target = operations.setdefault(operation, {})
            target.setdefault("parameters", {}).update(operation_meta.get("parameters", {}))
    return {
        "domains": value.get("domains", {}),
        "operations": operations,
        "parameters": value.get("parameters", {}),
    }


def iter_package_modules(package_name: str) -> list[str]:
    package = importlib.import_module(package_name)
    modules = [package_name]
    if hasattr(package, "__path__"):
        modules.extend(
            info.name
            for info in pkgutil.walk_packages(package.__path__, prefix=f"{package_name}.")
            if info.name not in EXCLUDED_MODULES
        )
    return sorted(set(modules))


def clean_docstring(obj: object) -> str:
    return inspect.cleandoc(inspect.getdoc(obj) or "")


def first_paragraph(value: str) -> str:
    if not value:
        return "Описание отсутствует."
    return re.split(
        r"\n\s*\n|\n:param|\n:return|\n:raises",
        value,
        maxsplit=1,
    )[0].strip()


def parse_param_docs(docstring: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, description in re.findall(
        r"^\s*:param\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.+?)(?=\n\s*:[a-z]+|\Z)",
        docstring,
        flags=re.MULTILINE | re.DOTALL,
    ):
        result[name] = " ".join(description.split())
    return result


def format_type(annotation: Any) -> str:
    if annotation is inspect.Signature.empty:
        return "Any"
    if annotation is None or annotation is type(None):
        return "None"
    if isinstance(annotation, str):
        return annotation

    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in {Union, UnionType}:
        return " | ".join(format_type(arg) for arg in args)
    if origin is list:
        return f"list[{', '.join(format_type(arg) for arg in args)}]"
    if origin is dict:
        return f"dict[{', '.join(format_type(arg) for arg in args)}]"
    if origin is tuple:
        return f"tuple[{', '.join(format_type(arg) for arg in args)}]"
    if origin is not None:
        name = getattr(origin, "__name__", str(origin).replace("typing.", ""))
        return f"{name}[{', '.join(format_type(arg) for arg in args)}]"

    return getattr(annotation, "__name__", str(annotation).replace("typing.", ""))


def example_value(name: str, annotation: Any, default: Any) -> str:
    if default is not inspect.Signature.empty and default is not None:
        return repr(default)

    type_text = format_type(annotation)
    if name == "contract_id":
        return '"contract-id"'
    if name.endswith("_id"):
        return f'"{name.replace("_", "-")}"'
    if "list[str]" in type_text:
        return '["item-id"]'
    if type_text.startswith("bool"):
        return "True"
    if type_text.startswith("int"):
        return "1"
    if type_text.startswith("float"):
        return "1.0"
    if "dict" in type_text:
        return "{}"
    return f'"{name.replace("_", "-")}"'


def service_classes() -> dict[str, type]:
    hints = get_type_hints(ServiceContainer)
    return {name: cls for name, cls in hints.items() if inspect.isclass(cls)}


def public_service_methods(cls: type) -> dict[str, object]:
    return {
        name: member
        for name, member in inspect.getmembers(cls, inspect.isfunction)
        if not name.startswith("_") and getattr(member, "__module__", "") == cls.__module__
    }


def documented_specs() -> list[Any]:
    return [
        spec for spec in build_default_registry().list_all() if spec.name not in EXCLUDED_OPERATIONS
    ]


def grouped_specs() -> dict[str, list[Any]]:
    grouped: dict[str, list[Any]] = {}
    for spec in documented_specs():
        service_name = SERVICE_NAMES[spec.domain]
        grouped.setdefault(service_name, []).append(spec)
    return grouped


def model_types() -> list[type[BaseModel]]:
    models: dict[str, type[BaseModel]] = {
        f"{ResponseStatus.__module__}.{ResponseStatus.__qualname__}": ResponseStatus
    }
    framework_models = {APIEnvelope, SDKBaseModel, ResponseModel, StrictRequestModel}
    for module_name in iter_package_modules(f"{PACKAGE_NAME}.models"):
        module = importlib.import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is BaseModel or obj in framework_models or not issubclass(obj, BaseModel):
                continue
            if obj.__module__ != module.__name__:
                continue
            models[f"{obj.__module__}.{obj.__qualname__}"] = obj
    return sorted(models.values(), key=lambda item: (item.__module__, item.__name__))


def parameter_description(
    name: str,
    doc_params: dict[str, str],
    metadata: dict[str, Any],
    operation_meta: dict[str, Any] | None = None,
) -> str:
    operation_parameters = (operation_meta or {}).get("parameters", {})
    common = metadata.get("parameters", {})
    description = operation_parameters.get(name) or doc_params.get(name) or common.get(name)
    if description:
        return str(description)
    if name == "api_version":
        return "Версия API. Обычно определяется SDK автоматически."
    return "Параметр публичного метода SDK."


def render_parameters(
    method: object,
    metadata: dict[str, Any],
    operation_meta: dict[str, Any] | None = None,
) -> list[str]:
    signature = inspect.signature(method)
    hints = get_type_hints(method)
    doc_params = parse_param_docs(clean_docstring(method))
    lines = [
        "| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |",
        "|---|---|:---:|---|---|",
    ]

    for name, parameter in signature.parameters.items():
        if name == "self":
            continue
        annotation = hints.get(name, parameter.annotation)
        required = parameter.default is inspect.Signature.empty
        default = "—" if required else f"`{parameter.default!r}`"
        description = parameter_description(name, doc_params, metadata, operation_meta)
        lines.append(
            f"| `{name}` | `{format_type(annotation)}` | "
            f"{'Да' if required else 'Нет'} | {default} | {description} |"
        )
    return lines


def render_example(service_name: str, method_name: str, method: object) -> list[str]:
    signature = inspect.signature(method)
    hints = get_type_hints(method)
    arguments: list[str] = []

    for name, parameter in signature.parameters.items():
        if name in {"self", "api_version"}:
            continue
        if parameter.default is not inspect.Signature.empty and parameter.default is None:
            continue
        value = example_value(name, hints.get(name, parameter.annotation), parameter.default)
        arguments.append(f"    {name}={value},")

    return [
        "```python",
        f"result = await client.{service_name}.{method_name}(",
        *arguments,
        ")",
        "print(result)",
        "```",
    ]


def render_method_page(
    service_name: str,
    service_cls: type,
    specs: list[Any],
    metadata: dict[str, Any],
) -> str:
    methods = public_service_methods(service_cls)
    operations_meta = metadata.get("operations", {})
    domain_meta = metadata.get("domains", {}).get(service_name, {})
    lines = [
        f"# `client.{service_name}`",
        "",
        domain_meta.get("description") or clean_docstring(service_cls) or "Методы сервиса SDK.",
        "",
    ]

    for spec in sorted(specs, key=lambda item: item.name):
        method = methods[spec.name]
        op_meta = operations_meta.get(spec.name, {})
        docstring = clean_docstring(method)
        return_type = get_type_hints(method).get("return", inspect.Signature.empty)
        lines.extend(
            [
                f"## `client.{service_name}.{spec.name}()`",
                "",
                op_meta.get("summary") or first_paragraph(docstring),
                "",
                "### Маршрут",
                "",
                "| HTTP | API | Route | DEMO | Тарифицируется |",
                "|---:|---:|---|:---:|:---:|",
                f"| {spec.http_method} | {spec.default_version} | `{spec.endpoint}` | "
                f"{'Да' if spec.demo_available else 'Нет'} | "
                f"{'Да' if bool(spec.billable) else 'Нет'} |",
                "",
                "### Параметры",
                "",
                *render_parameters(method, metadata, op_meta),
                "",
                "### Возвращаемое значение",
                "",
                *render_return_details(return_type, format_type),
            ]
        )
        response_description = op_meta.get("response")
        if response_description:
            lines.extend([str(response_description), ""])
        lines.extend(
            [
                "### Пример",
                "",
                *render_example(service_name, spec.name, method),
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_catalog(grouped: dict[str, list[Any]], metadata: dict[str, Any]) -> str:
    registry_count = len(build_default_registry().list_all())
    documented_count = sum(len(specs) for specs in grouped.values())
    lines = [
        "# Методы API",
        "",
        "Документация генерируется из runtime registry, публичных сигнатур, type hints, "
        "моделей SDK и метаданных спецификации.",
        "",
        '!!! info "Покрытие"',
        f"    Опубликовано **{documented_count} операций** из {registry_count}, "
        "зарегистрированных в SDK.",
        "    Методы МПК/QR временно исключены до отдельного решения по QR-спецификации.",
        "",
        "| Сервис | Операций | Назначение |",
        "|---|---:|---|",
    ]
    domains = metadata.get("domains", {})
    for service_name in sorted(grouped):
        description = domains.get(service_name, {}).get("summary", "Методы сервиса SDK")
        lines.append(
            f"| [`client.{service_name}`](methods/{service_name}.md) | "
            f"{len(grouped[service_name])} | {description} |"
        )

    lines.extend(
        [
            "",
            "## Общий формат ответа",
            "",
            "Большинство методов возвращают типизированную модель SDK. Ответ проходит "
            "проверку Pydantic: обязательные поля, типы, вложенные модели, ограничения "
            "схемы и пользовательские валидаторы.",
            "",
            "Подробные структуры и фактические правила проверки приведены в разделе "
            "[Типы данных](data-types/index.md).",
            "",
        ]
    )
    return "\n".join(lines)


def render_model(model: type[BaseModel]) -> str:
    return render_model_page(model, format_type)


def render_model_index(models: list[type[BaseModel]]) -> str:
    lines = [
        "# Типы данных",
        "",
        "Типизированные Pydantic-модели запросов и ответов SDK. Для каждой модели "
        "показаны типы после валидации, JSON-типы, обязательность, nullable, значения "
        "по умолчанию, ограничения схемы и пользовательские валидаторы.",
        "",
    ]
    by_module: dict[str, list[type[BaseModel]]] = {}
    for model in models:
        module = model.__module__.rsplit(".", 1)[-1]
        by_module.setdefault(module, []).append(model)

    for module, values in sorted(by_module.items()):
        lines.extend([f"## `{module}`", ""])
        for model in values:
            lines.append(f"- [`{model.__name__}`]({module}/{model.__name__}.md)")
        lines.append("")
    return "\n".join(lines)


def render_api_reference() -> str:
    return "\n".join(
        [
            "# API Reference",
            "",
            "Автоматически сформированная справка разделена на два раздела:",
            "",
            "- [Методы API](methods.md) — вызовы SDK, параметры, раскрытые модели ответов и примеры.",
            "- [Типы данных](data-types/index.md) — фактические проверки Pydantic для полей моделей.",
            "",
        ]
    )


def validate(
    grouped: dict[str, list[Any]],
    models: list[type[BaseModel]],
    metadata: dict[str, Any],
) -> None:
    services = service_classes()
    operations_meta = metadata.get("operations", {})
    errors: list[str] = []

    for service_name, specs in grouped.items():
        cls = services.get(service_name)
        if cls is None:
            errors.append(f"missing service class: {service_name}")
            continue
        methods = public_service_methods(cls)
        for spec in specs:
            method = methods.get(spec.name)
            if method is None:
                errors.append(f"{service_name}.{spec.name}: method not found")
                continue
            hints = get_type_hints(method)
            if "return" not in hints:
                errors.append(f"{service_name}.{spec.name}: missing return annotation")
            if not clean_docstring(method):
                errors.append(f"{service_name}.{spec.name}: missing docstring")
            declared_parameters = operations_meta.get(spec.name, {}).get("parameters", {})
            unknown_parameters = set(declared_parameters) - set(
                inspect.signature(method).parameters
            )
            if unknown_parameters:
                errors.append(
                    f"{service_name}.{spec.name}: metadata contains unknown parameters "
                    f"{sorted(unknown_parameters)}"
                )

    if not models:
        errors.append("no public models found")
    if errors:
        raise RuntimeError("Documentation validation failed:\n- " + "\n- ".join(errors))


def build_all() -> dict[Path, str]:
    metadata = load_metadata()
    grouped = grouped_specs()
    models = model_types()
    validate(grouped, models, metadata)
    services = service_classes()
    output: dict[Path, str] = {
        DOCS_PATH / "methods.md": render_catalog(grouped, metadata),
        DOCS_PATH / "api-reference.md": render_api_reference(),
        DATA_TYPES_PATH / "index.md": render_model_index(models),
    }

    for service_name, specs in grouped.items():
        output[METHODS_PATH / f"{service_name}.md"] = render_method_page(
            service_name,
            services[service_name],
            specs,
            metadata,
        )
    for model in models:
        module = model.__module__.rsplit(".", 1)[-1]
        output[DATA_TYPES_PATH / module / f"{model.__name__}.md"] = render_model(model)
    return output


def main() -> None:
    output = build_all()
    for path, content in output.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Generated {path.relative_to(PROJECT_ROOT)}")
