from __future__ import annotations

import inspect
from enum import Enum
from types import UnionType
from typing import Annotated, Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel

from api_client_opti24.modeling import StrictRequestModel

CONSTRAINT_LABELS = {
    "minLength": "минимальная длина",
    "maxLength": "максимальная длина",
    "pattern": "шаблон",
    "minimum": "минимум",
    "maximum": "максимум",
    "exclusiveMinimum": "строго больше",
    "exclusiveMaximum": "строго меньше",
    "multipleOf": "кратно",
    "minItems": "минимум элементов",
    "maxItems": "максимум элементов",
    "uniqueItems": "уникальные элементы",
    "format": "формат",
    "enum": "допустимые значения",
    "const": "фиксированное значение",
}


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _code(value: Any) -> str:
    return f"`{_escape(value)}`"


def _unwrap_annotated(annotation: Any) -> Any:
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        return args[0] if args else Any
    return annotation


def _allows_none(annotation: Any) -> bool:
    annotation = _unwrap_annotated(annotation)
    if annotation is type(None):
        return True
    origin = get_origin(annotation)
    return origin in {Union, UnionType} and any(_allows_none(arg) for arg in get_args(annotation))


def _model_types(annotation: Any) -> list[type[BaseModel]]:
    annotation = _unwrap_annotated(annotation)
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return [annotation]

    result: list[type[BaseModel]] = []
    for argument in get_args(annotation):
        for model in _model_types(argument):
            if model not in result:
                result.append(model)
    return result


def _json_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return f"object ({schema['$ref'].rsplit('/', 1)[-1]})"
    if "anyOf" in schema:
        values = [_json_type(item) for item in schema["anyOf"]]
        return " | ".join(dict.fromkeys(values))
    if "oneOf" in schema:
        values = [_json_type(item) for item in schema["oneOf"]]
        return " | ".join(dict.fromkeys(values))

    schema_type = schema.get("type")
    if schema_type == "array":
        return f"array[{_json_type(schema.get('items', {}))}]"
    if schema_type == "object":
        additional = schema.get("additionalProperties")
        if isinstance(additional, dict):
            return f"object[string, {_json_type(additional)}]"
        return "object"
    if isinstance(schema_type, list):
        return " | ".join(str(item) for item in schema_type)
    return str(schema_type or "any")


def _constraints(schema: dict[str, Any]) -> str:
    values: list[str] = []
    for key, label in CONSTRAINT_LABELS.items():
        if key not in schema:
            continue
        value = schema[key]
        if isinstance(value, list):
            rendered = ", ".join(repr(item) for item in value)
        else:
            rendered = repr(value)
        values.append(f"{label}: {rendered}")

    for branch_key in ("anyOf", "oneOf", "allOf"):
        for branch in schema.get(branch_key, []):
            branch_value = _constraints(branch)
            if branch_value and branch_value not in values:
                values.append(branch_value)
    return "; ".join(values) or "—"


def _field_default(field: Any) -> str:
    if field.is_required():
        return "—"
    if field.default_factory is not None:
        factory_name = getattr(field.default_factory, "__name__", repr(field.default_factory))
        return f"factory: {factory_name}()"
    return repr(field.default)


def _validation_description(annotation: Any, format_type: Any) -> str:
    annotation = _unwrap_annotated(annotation)
    origin = get_origin(annotation)
    args = get_args(annotation)

    if annotation is Any:
        return "Тип не ограничен: принимается любое значение."
    if origin in {Union, UnionType}:
        return "Значение должно соответствовать одному из типов: " + ", ".join(
            format_type(item) for item in args
        )
    if origin is list:
        item_type = format_type(args[0]) if args else "Any"
        return f"Проверяется как список; каждый элемент проверяется как {item_type}."
    if origin is dict:
        key_type = format_type(args[0]) if args else "Any"
        value_type = format_type(args[1]) if len(args) > 1 else "Any"
        return f"Проверяется как объект: ключи {key_type}, значения {value_type}."
    if origin is tuple:
        return f"Проверяется как кортеж {format_type(annotation)}."
    if origin is Literal:
        return "Допускаются только значения: " + ", ".join(repr(item) for item in args)
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return f"Вложенный объект рекурсивно проверяется моделью {annotation.__name__}."
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        return f"Проверяется как перечисление {annotation.__name__}."
    return f"Значение преобразуется и проверяется как {format_type(annotation)}."


def _validator_rows(model: type[BaseModel]) -> list[dict[str, str]]:
    decorators = getattr(model, "__pydantic_decorators__", None)
    if decorators is None:
        return []

    rows: list[dict[str, str]] = []
    for name, decorator in getattr(decorators, "field_validators", {}).items():
        info = decorator.info
        function = decorator.func
        rows.append(
            {
                "kind": "field_validator",
                "name": name,
                "targets": ", ".join(info.fields),
                "mode": str(info.mode),
                "description": inspect.cleandoc(inspect.getdoc(function) or "")
                or f"Пользовательская проверка `{name}`.",
            }
        )
    for name, decorator in getattr(decorators, "model_validators", {}).items():
        info = decorator.info
        function = decorator.func
        rows.append(
            {
                "kind": "model_validator",
                "name": name,
                "targets": "вся модель",
                "mode": str(info.mode),
                "description": inspect.cleandoc(inspect.getdoc(function) or "")
                or f"Пользовательская проверка `{name}`.",
            }
        )
    return rows


def _model_link(model: type[BaseModel], prefix: str) -> str:
    module = model.__module__.rsplit(".", 1)[-1]
    return f"{prefix}/{module}/{model.__name__}.md"


def _field_rows(model: type[BaseModel], format_type: Any) -> list[str]:
    schema = model.model_json_schema(by_alias=False)
    properties = schema.get("properties", {})
    validator_rows = _validator_rows(model)
    validators_by_field: dict[str, list[str]] = {}
    for validator in validator_rows:
        if validator["kind"] != "field_validator":
            continue
        for field_name in validator["targets"].split(", "):
            validators_by_field.setdefault(field_name, []).append(
                f"{validator['name']} ({validator['mode']})"
            )

    rows: list[str] = []
    for field_name, field in model.model_fields.items():
        field_schema = properties.get(field_name, {})
        validation = _validation_description(field.annotation, format_type)
        field_validators = validators_by_field.get(field_name, [])
        if field_validators:
            validation += " Дополнительно: " + ", ".join(field_validators) + "."
        alias = field.alias or "—"
        rows.append(
            f"| `{field_name}` | `{_escape(format_type(field.annotation))}` | "
            f"`{_escape(_json_type(field_schema))}` | "
            f"{'Да' if field.is_required() else 'Нет'} | "
            f"{'Да' if _allows_none(field.annotation) else 'Нет'} | "
            f"`{_escape(_field_default(field))}` | `{_escape(alias)}` | "
            f"{_escape(_constraints(field_schema))} | {_escape(validation)} | "
            f"{_escape(field.description or '—')} |"
        )
    return rows


def render_return_details(annotation: Any, format_type: Any) -> list[str]:
    type_text = format_type(annotation)
    models = _model_types(annotation)
    lines = [f"**Тип после валидации:** `{type_text}`", ""]

    if not models:
        lines.extend(
            [
                "**Pydantic-модель:** нет.",
                "",
                "SDK возвращает значение указанного Python-типа; отдельная модель ответа не применяется.",
                "",
            ]
        )
        return lines

    primary = models[0]
    model_links = ", ".join(
        f"[`{model.__name__}`]({_model_link(model, '../data-types')})" for model in models
    )
    lines.extend(
        [
            f"**Pydantic-модель:** {model_links}",
            "",
            f"Ответ передаётся в `{primary.__name__}.model_validate(payload)`. "
            "Pydantic проверяет обязательные поля, преобразует значения по аннотациям "
            "и рекурсивно валидирует вложенные модели.",
            "",
            "#### Поля возвращаемой модели",
            "",
            "| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |",
            "|---|---|---|:---:|:---:|---|",
        ]
    )
    schema = primary.model_json_schema(by_alias=False)
    properties = schema.get("properties", {})
    for field_name, field in primary.model_fields.items():
        field_schema = properties.get(field_name, {})
        lines.append(
            f"| `{field_name}` | `{_escape(format_type(field.annotation))}` | "
            f"`{_escape(_json_type(field_schema))}` | "
            f"{'Да' if field.is_required() else 'Нет'} | "
            f"{'Да' if _allows_none(field.annotation) else 'Нет'} | "
            f"{_escape(field.description or '—')} |"
        )

    nested: list[type[BaseModel]] = []
    for field in primary.model_fields.values():
        for nested_model in _model_types(field.annotation):
            if nested_model is not primary and nested_model not in nested:
                nested.append(nested_model)
    if nested:
        lines.extend(["", "**Вложенные модели:**"])
        for model in nested:
            lines.append(f"- [`{model.__name__}`]({_model_link(model, '../data-types')})")
    lines.append("")
    return lines


def render_model_page(model: type[BaseModel], format_type: Any) -> str:
    description = inspect.cleandoc(vars(model).get("__doc__") or "") or "Модель данных SDK."
    config = model.model_config
    extra = str(config.get("extra", "ignore"))
    extra_description = {
        "allow": "Дополнительные поля разрешены и сохраняются в модели.",
        "forbid": "Дополнительные поля запрещены и вызывают ValidationError.",
        "ignore": "Дополнительные поля игнорируются.",
    }.get(extra, f"Режим дополнительных полей: {extra}.")
    is_request_model = issubclass(model, StrictRequestModel)
    model_kind = "request" if is_request_model else "response/data"
    if is_request_model:
        validation_notice = (
            f"    Тип модели: **{model_kind}**. Правила ниже применяются, когда вызывающий код "
            f"явно создаёт `{model.__name__}` или вызывает "
            f"`{model.__name__}.model_validate(payload)`. Наличие request-модели не означает, "
            "что каждый метод SDK автоматически создаёт её: фактический входной контракт "
            "определяется сигнатурой соответствующего сервисного метода."
        )
    else:
        validation_notice = (
            f"    Тип модели: **{model_kind}**. Ответ API проверяется этой моделью напрямую "
            "или рекурсивно как часть родительской response-модели. При несовпадении типов "
            "или отсутствии обязательного поля Pydantic формирует `ValidationError`."
        )

    lines = [
        f"# `{model.__name__}`",
        "",
        description,
        "",
        '!!! info "Назначение Pydantic"',
        validation_notice,
        "",
        "## Поведение модели",
        "",
        "| Настройка | Значение | Фактическое поведение |",
        "|---|---|---|",
        f"| Дополнительные поля (`extra`) | `{extra}` | {extra_description} |",
        f"| Проверка default | `{bool(config.get('validate_default', False))}` | "
        "Значения по умолчанию также проходят валидацию. |",
        f"| Заполнение по имени поля | `{bool(config.get('populate_by_name', False))}` | "
        "Разрешено использовать имя поля наряду с alias. |",
        f"| Число → строка | `{bool(config.get('coerce_numbers_to_str', False))}` | "
        "Для строковых полей числовые значения могут быть преобразованы в строку. |",
        "",
        "## Поля и проверки",
        "",
        "| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |",
        "|---|---|---|:---:|:---:|---|---|---|---|---|",
        *_field_rows(model, format_type),
        "",
        "!!! note \"Граница проверки\"",
        "    Значения, упомянутые только в тексте описания, не считаются жёстким "
        "ограничением. Например, фраза «Y или N» проверяется только тогда, когда "
        "в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.",
        "",
    ]

    validators = _validator_rows(model)
    if validators:
        lines.extend(
            [
                "## Пользовательские валидаторы",
                "",
                "| Тип | Имя | Поля/область | Режим | Описание |",
                "|---|---|---|---|---|",
            ]
        )
        for item in validators:
            lines.append(
                f"| `{item['kind']}` | `{item['name']}` | `{_escape(item['targets'])}` | "
                f"`{_escape(item['mode'])}` | {_escape(item['description'])} |"
            )
        lines.append("")

    nested: list[type[BaseModel]] = []
    for field in model.model_fields.values():
        for nested_model in _model_types(field.annotation):
            if nested_model is not model and nested_model not in nested:
                nested.append(nested_model)
    if nested:
        lines.extend(["## Вложенные модели", ""])
        current_module = model.__module__.rsplit(".", 1)[-1]
        for nested_model in nested:
            nested_module = nested_model.__module__.rsplit(".", 1)[-1]
            link = (
                f"{nested_model.__name__}.md"
                if nested_module == current_module
                else f"../{nested_module}/{nested_model.__name__}.md"
            )
            lines.append(f"- [`{nested_model.__name__}`]({link})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
