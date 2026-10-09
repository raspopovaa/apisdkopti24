"""Таблицы параметров методов и моделей запросов и ответов для страниц примеров.

Модуль генератора scripts/generate_method_examples.py; отдельно не запускается.
"""

import inspect
import re
import sys
from pathlib import Path
from typing import Any, Union, get_args, get_origin, get_type_hints

from documentation_generator import (
    clean_docstring,
    format_type,
    parse_param_docs,
)
from method_examples_common import DOC_METADATA, ENVELOPE_MODELS, api_parameter_name
from method_examples_contracts import spec_request_parameters, spec_response_fields
from method_examples_format import clean_text, data_type_link
from pydantic import BaseModel
from pydantic_docs import (
    _constraints,
    _model_types,
    _unwrap_annotated,
    code_cell,
)

from apisdkopti24.operations import OperationSpec
from apisdkopti24.service_groups import ServiceContainer


def display_type(annotation: Any) -> str:
    """Тип для таблицы: без Annotated и служебных ограничений, они в отдельной колонке."""
    annotation = _unwrap_annotated(annotation)
    origin = get_origin(annotation)
    arguments = get_args(annotation)
    if origin in {Union, type(int | None)}:
        return " | ".join(display_type(argument) for argument in arguments)
    if origin in {list, dict, tuple} and arguments:
        return f"{origin.__name__}[{', '.join(display_type(argument) for argument in arguments)}]"
    return format_type(annotation)


def service_function(domain: str, name: str) -> Any:
    return getattr(get_type_hints(ServiceContainer)[domain], name)


def _contains_list(annotation: Any) -> bool:
    annotation = _unwrap_annotated(annotation)
    if get_origin(annotation) is list:
        return True
    if get_origin(annotation) in {Union, type(int | None)}:
        return any(_contains_list(argument) for argument in get_args(annotation))
    return False


def parameter_rows(domain: str, name: str) -> list[str]:
    function = service_function(domain, name)
    signature = inspect.signature(function, eval_str=True)
    doc_params = parse_param_docs(clean_docstring(function))
    operation_meta = DOC_METADATA["operations"].get(name, {})
    spec_parameters = spec_request_parameters(domain, name)
    rows = [
        "| Параметр | Python-тип | Обязательный | По умолчанию | Описание |",
        "|---|---|:---:|---|---|",
    ]
    for parameter in signature.parameters.values():
        if parameter.name == "self":
            continue
        spec_parameter = spec_parameters.get(api_parameter_name(name, parameter.name))
        description = (
            operation_meta.get("parameters", {}).get(parameter.name)
            or doc_params.get(parameter.name)
            or (spec_parameter or {}).get("description")
            or DOC_METADATA["parameters"].get(parameter.name)
            or (
                "Версия API. Обычно SDK выбирает её сам."
                if parameter.name == "api_version"
                else "—"
            )
        )
        required = parameter.default is inspect.Parameter.empty
        default = "—" if required else f"`{parameter.default!r}`"
        rows.append(
            f"| `{parameter.name}` | {code_cell(display_type(parameter.annotation))} | "
            f"{'Да' if required else 'Нет'} | {default} | {clean_text(description)} |"
        )
    return rows


def request_models(domain: str, name: str) -> list[type[BaseModel]]:
    """Модели, которыми метод SDK проверяет параметры перед отправкой."""
    function = service_function(domain, name)
    module = sys.modules[function.__module__]
    found: list[type[BaseModel]] = []
    for identifier in re.findall(r"\b[A-Z]\w+\b", inspect.getsource(function)):
        candidate = getattr(module, identifier, None)
        if (
            isinstance(candidate, type)
            and issubclass(candidate, BaseModel)
            and not candidate.__name__.endswith("Response")
            and candidate not in found
        ):
            found.append(candidate)
    for model in list(found):
        for field in model.model_fields.values():
            for nested in _model_types(field.annotation):
                if nested not in found:
                    found.append(nested)
    return found


def response_model_sections(model: type[BaseModel]) -> list[tuple[type[BaseModel], str]]:
    """Модель ответа и вложенные модели с путём к ним в JSON."""
    sections = [(model, "")]
    seen = {model}
    queue = [(model, "")]
    while queue:
        current, prefix = queue.pop(0)
        for field_name, field in current.model_fields.items():
            path = f"{prefix}{field.alias or field_name}"
            for nested in _model_types(field.annotation):
                if nested.__name__ in ENVELOPE_MODELS or nested in seen:
                    continue
                seen.add(nested)
                child_prefix = f"{path}{'[]' if _contains_list(field.annotation) else ''}."
                sections.append((nested, child_prefix))
                queue.append((nested, child_prefix))
    return sections


def model_heading(model: type[BaseModel], page_dir: Path, suffix: str = "") -> str:
    link = data_type_link(model.__name__, page_dir)
    title = f"[`{model.__name__}`]({link})" if link else f"`{model.__name__}`"
    return f"#### {title}{suffix}"


def request_model_blocks(domain: str, name: str, page_dir: Path) -> list[str]:
    models = request_models(domain, name)
    if not models:
        return [
            "Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой "
            "метода и общими правилами идентификаторов.",
            "",
        ]
    spec_parameters = spec_request_parameters(domain, name)
    lines = [
        "Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы "
        "и ограничения; при ошибке запрос не отправляется.",
        "",
    ]
    for model in models:
        properties = model.model_json_schema(by_alias=False).get("properties", {})
        lines.extend(
            [
                model_heading(model, page_dir),
                "",
                "| Поле | Python-тип | Обязательное | Ограничения | Описание |",
                "|---|---|:---:|---|---|",
            ]
        )
        for field_name, field in model.model_fields.items():
            spec_parameter = spec_parameters.get(field.alias or field_name, {})
            description = field.description or spec_parameter.get("description") or "—"
            lines.append(
                f"| `{field.alias or field_name}` | {code_cell(display_type(field.annotation))} | "
                f"{'Да' if field.is_required() else 'Нет'} | "
                f"{clean_text(_constraints(properties.get(field_name, {})))} | "
                f"{clean_text(description)} |"
            )
        lines.append("")
    return lines


def response_model_blocks(domain: str, name: str, spec: OperationSpec, page_dir: Path) -> list[str]:
    if spec.response_type is None or not issubclass(spec.response_type, BaseModel):
        return []
    spec_fields = spec_response_fields(domain, name)
    lines = [
        "Модели ответа и путь к их полям в JSON.",
        "",
    ]
    occurrences = model_occurrences(spec.response_type)
    for model, prefix in response_model_sections(spec.response_type):
        suffix = f" · `{prefix.rstrip('.')}`" if prefix else ""
        other_paths = [path for path in occurrences.get(model, []) if f"{path}." != prefix]
        lines.extend(
            [
                model_heading(model, page_dir, suffix),
                "",
            ]
        )
        if other_paths:
            also = ", ".join(f"`{path}`" for path in other_paths)
            lines.extend([f"Та же модель описывает и {also}.", ""])
        lines.extend(
            [
                "| Поле | Путь в JSON | Python-тип | Обязательное | Описание |",
                "|---|---|---|:---:|---|",
            ]
        )
        for field_name, field in model.model_fields.items():
            key = field.alias or field_name
            path = f"{prefix}{key}"
            spec_field = spec_fields.get(path) or {}
            description = field.description or spec_field.get("description") or "—"
            lines.append(
                f"| `{key}` | `{path}` | {code_cell(display_type(field.annotation))} | "
                f"{'Да' if field.is_required() else 'Нет'} | {clean_text(description)} |"
            )
        lines.append("")
    return lines


def model_paths(model: type[BaseModel], prefix: str = "", depth: int = 0) -> set[str]:
    """Все пути полей модели в JSON, в том числе для моделей, повторяющихся в разных полях."""
    paths: set[str] = set()
    if depth > 8:
        return paths
    for field_name, field in model.model_fields.items():
        keys = field_keys(field_name, field)
        for key in keys:
            paths.add(f"{prefix}{key}")
        for nested in _model_types(field.annotation):
            if nested.__name__ in ENVELOPE_MODELS:
                continue
            for key in keys:
                suffix = "[]" if _contains_list(field.annotation) else ""
                paths |= model_paths(nested, f"{prefix}{key}{suffix}.", depth + 1)
    return paths


def field_keys(field_name: str, field: Any) -> set[str]:
    """Все имена поля в JSON: имя, alias и варианты AliasChoices."""
    keys = {field_name}
    for alias in (field.alias, field.serialization_alias):
        if isinstance(alias, str):
            keys.add(alias)
    choices = getattr(field.validation_alias, "choices", None)
    if choices:
        keys.update(choice for choice in choices if isinstance(choice, str))
    elif isinstance(field.validation_alias, str):
        keys.add(field.validation_alias)
    return keys


def model_occurrences(model: type[BaseModel]) -> dict[type[BaseModel], list[str]]:
    """Для каждой вложенной модели — все пути в JSON, где она встречается."""
    found: dict[type[BaseModel], list[str]] = {}

    def walk(current: type[BaseModel], prefix: str, depth: int) -> None:
        if depth > 8:
            return
        for field_name, field in current.model_fields.items():
            path = f"{prefix}{field.alias or field_name}"
            for nested in _model_types(field.annotation):
                if nested.__name__ in ENVELOPE_MODELS:
                    continue
                child = f"{path}{'[]' if _contains_list(field.annotation) else ''}"
                found.setdefault(nested, []).append(child)
                walk(nested, f"{child}.", depth + 1)

    walk(model, "", 0)
    return found
