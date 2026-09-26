"""Сгенерировать в tools/live_check по одному файлу проверки на каждый метод SDK.

Источники: реестр операций SDK, сигнатуры сервисов, Pydantic-модели, контракты
спецификации 1.1.60 (specifications/contracts), описания параметров
(specifications/*.yaml) и краткие описания проверок (tools/live_check/descriptions.yaml).

Запуск из корня репозитория:

    python tools/live_check/_generate.py            # создать недостающие файлы
    python tools/live_check/_generate.py --force    # перезаписать все файлы методов
    python tools/live_check/_generate.py --check    # проверить, что файлы актуальны
"""

from __future__ import annotations

import argparse
import inspect
import re
import sys
import textwrap
import typing
from pathlib import Path
from typing import Any

import black
import yaml

LIVE_CHECK_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = LIVE_CHECK_DIR.parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pydantic import BaseModel  # noqa: E402

from apisdkopti24.registry import build_default_registry  # noqa: E402
from apisdkopti24.service_groups import ServiceContainer  # noqa: E402

SPEC_DIR = PROJECT_ROOT / "specifications"
CHECK_DESCRIPTIONS = LIVE_CHECK_DIR / "descriptions.yaml"
BLACK_MODE = black.Mode(line_length=100, string_normalization=False)

# POST-запросы, которые только читают данные, и GET-запросы, которые их меняют.
READ_ONLY_POST = {"auth_user", "check_purchase", "get_final_prices"}
MUTATING_GET = {"order_report_v1", "resend_invite"}

# Параметры, которые берутся из общего списка test_data.json -> common.
COMMON_KEYS = {
    "contract_id",
    "card_id",
    "user_id",
    "group_id",
    "template_id",
    "transaction_id",
    "invite_id",
    "job_id",
    "report_id",
    "poi_id",
    "office_id",
    "limit_id",
    "regionlimit_id",
    "restriction_id",
    "date_from",
    "date_to",
    "period",
    "email",
}
MPC_OPERATIONS = {
    "confirm_mpc",
    "delete_mpc",
    "generate_payment_qr",
    "init_mpc",
    "reset_mpc",
    "update_mpc",
}
TEMPLATE_IDS = {
    "limit_id": "template_limit_id",
    "restriction_id": "template_restriction_id",
    "georestriction_id": "template_georestriction_id",
}
# Необязательные параметры, для которых полезно подставить общее значение.
OPTIONAL_FROM_COMMON = {
    ("get_limits", "card_id"),
    ("get_region_limits", "card_id"),
    ("get_restrictions", "card_id"),
    ("create_virtual_card", "user_id"),
}
MODEL_LISTS = {
    ("set_limit", "limits"): "LimitRequestItem",
    ("set_region_limit", "region_limits"): "RegionLimitRequestItem",
    ("set_restriction", "restrictions"): "RestrictionRequestItem",
}
SKIPPED_PARAMS = {"api_version", "filter_fn", "sort_by", "reverse"}

API_ERRORS = """\
    Ответ API (HTTP-код или status.code; текст сервера — в «Сообщение сервера: …»):
      400 ValidationError — неверные параметры или структура запроса;
      401 NotAuthenticatedError — сессия недействительна (SDK один раз авторизуется
          заново и повторяет запрос);
      403 AccessDeniedError — нет прав на объект, роль, IP, api_key или тариф;
      404 NotFoundError — объект или маршрут не найден;
      409 DuplicateConflictError — повтор однотипного запроса;
      429/509 RateLimitError — превышен лимит запросов;
      5xx ServerError — ошибка сервера API.
    Проверка ответа моделью SDK: pydantic.ValidationError — ответ с HTTP 200 не совпал
      с моделью (поле отсутствует, null вместо значения, другой тип); список полей
      выводится при запуске, известные расхождения — в docs/spec-compatibility.md.
    Сеть: APIConnectionError (сервер недоступен, в т. ч. IP вне разрешённых стран),
      OperationTimeoutError (исчерпан общий лимит времени), RetryBudgetExceededError."""


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_contracts() -> dict[str, dict[str, Any]]:
    operations: dict[str, dict[str, Any]] = {}
    for path in sorted((SPEC_DIR / "contracts" / "1.1.60").glob("*.yaml")):
        operations.update(load_yaml(path).get("operations") or {})
    return operations


def load_parameter_descriptions() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    per_operation: dict[str, dict[str, str]] = {}
    shared: dict[str, str] = {}
    for name in ("parameter-descriptions-1.1.60.yaml", "documentation.yaml"):
        payload = load_yaml(SPEC_DIR / name)
        for key, text in (payload.get("parameters") or {}).items():
            shared.setdefault(str(key), " ".join(str(text).split()))
        for operation, entry in (payload.get("operations") or {}).items():
            for key, text in ((entry or {}).get("parameters") or {}).items():
                per_operation.setdefault(operation, {}).setdefault(
                    str(key), " ".join(str(text).split())
                )
    return per_operation, shared


def load_summaries() -> dict[str, str]:
    payload = load_yaml(SPEC_DIR / "documentation.yaml")
    return {
        name: " ".join(str(entry.get("summary", "")).split())
        for name, entry in (payload.get("operations") or {}).items()
        if isinstance(entry, dict)
    }


def load_check_descriptions() -> dict[str, str]:
    """Краткие описания проверок из descriptions.yaml."""
    loaded = load_yaml(CHECK_DESCRIPTIONS) or {}
    return {str(name): str(text) for name, text in loaded.items()}


def service_methods() -> dict[str, tuple[str, Any]]:
    methods: dict[str, tuple[str, Any]] = {}
    for attr, cls in typing.get_type_hints(ServiceContainer).items():
        for name, function in inspect.getmembers(cls, inspect.isfunction):
            methods.setdefault(name, (attr, function))
    return methods


def type_text(annotation: Any) -> str:
    if annotation is inspect.Parameter.empty:
        return "Any"
    text = annotation if isinstance(annotation, str) else repr(annotation)
    text = re.sub(r"<class '([\w.]+)'>", r"\1", text)
    text = re.sub(
        r"\b(?:apisdkopti24\.models\.\w+\.|apisdkopti24\.\w+\.|collections\.abc\.|typing\.|decimal\.)",
        "",
        text,
    )
    return text


def model_tree(model: Any, seen: set[type]) -> list[type[BaseModel]]:
    """Модель и все вложенные модели в порядке обхода."""
    result: list[type[BaseModel]] = []

    def walk(annotation: Any) -> None:
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            if annotation in seen:
                return
            seen.add(annotation)
            result.append(annotation)
            for field in annotation.model_fields.values():
                walk(field.annotation)
            return
        for arg in typing.get_args(annotation):
            walk(arg)

    walk(model)
    return result


def describe_models(models: list[type[BaseModel]], indent: str = "      ") -> list[str]:
    lines: list[str] = []
    for model in models:
        lines.append(f"{indent[:-2]}{model.__name__}:")
        for name, field in model.model_fields.items():
            alias = field.alias or name
            required = "обязательное" if field.is_required() else "необязательное"
            description = field.description or "описание не задано"
            lines.append(
                f"{indent}{alias}: {type_text(field.annotation)}, {required} — {description}"
            )
    return lines


def local_errors(function: Any) -> list[str]:
    """Проверки SDK до отправки запроса, найденные в коде метода сервиса."""
    source = inspect.getsource(function)
    found: list[str] = []
    for error, message in re.findall(r'raise (\w+)\(\s*f?"([^"]+)"', source):
        found.append(f"{error}: {message}")
    helpers = sorted(set(re.findall(r"\b(require_\w+|validate_\w+)\(", source)))
    for helper in helpers:
        found.append(f"{helper}() — RequestValidationError при недопустимом значении")
    return found


def is_mutating(spec: Any) -> bool:
    if spec.name in MUTATING_GET:
        return True
    if spec.name in READ_ONLY_POST:
        return False
    return spec.http_method.upper() != "GET"


def value_expression(operation: str, parameter: inspect.Parameter) -> str | None:
    """Выражение значения параметра в файле метода или None, если параметр не передаётся."""
    name = parameter.name
    required = parameter.default is inspect.Parameter.empty
    if (operation, name) in MODEL_LISTS:
        model = MODEL_LISTS[(operation, name)]
        return (
            f"[models.{model}.model_validate(item) "
            f"for item in method_value({operation!r}, {name!r})]"
        )
    if operation in MPC_OPERATIONS and name == "card_id":
        return 'common("mpc_card_id")'
    template_suffixes = ("_template_limit", "_template_restriction", "_template_georestriction")
    if operation.endswith(template_suffixes) and name in TEMPLATE_IDS:
        return f"common({TEMPLATE_IDS[name]!r})"
    if name in {"date_start", "start"}:
        return 'common("date_from")'
    if name in {"date_end", "end"}:
        return 'common("date_to")'
    if name == "card_ids":
        return '[common("card_id")]'
    if operation == "get_final_prices" and name == "goods":
        return '[common("goods_code")]'
    if name == "amount":
        return f"decimal(method_value({operation!r}, 'amount'))"
    if name == "contract_id" or (operation, name) in OPTIONAL_FROM_COMMON:
        return f"common({name!r})"
    if required:
        if name in COMMON_KEYS:
            return f"common({name!r})"
        return f"method_value({operation!r}, {name!r})"
    return repr(parameter.default)


def parameter_lines(
    signature: inspect.Signature,
    contract_params: dict[str, dict[str, Any]],
    descriptions: dict[str, str],
    shared: dict[str, str],
) -> list[str]:
    lines: list[str] = []
    for parameter in list(signature.parameters.values())[1:]:
        if parameter.name in SKIPPED_PARAMS:
            continue
        required = parameter.default is inspect.Parameter.empty
        state = (
            "обязательный" if required else f"необязательный, по умолчанию {parameter.default!r}"
        )
        contract = contract_params.get(parameter.name, {})
        description = (
            descriptions.get(parameter.name)
            or " ".join(str(contract.get("description", "")).split())
            or shared.get(parameter.name)
            or shared.get(parameter.name.replace("_", ""))
            or "описание в спецификации не найдено"
        )
        api_type = (
            f", тип в спецификации: {contract['api_type']}" if contract.get("api_type") else ""
        )
        lines.append(
            f"      {parameter.name}: {type_text(parameter.annotation)}, {state}{api_type} — {description}"
        )
    return lines


def route_lines(spec: Any) -> list[str]:
    lines: list[str] = []
    for route in spec.iter_routes():
        suffix = "" if route.name == "default" else f" (вариант {route.name})"
        lines.append(f"      {route.http_method} /{route.api_version}/{route.endpoint}{suffix}")
    request = spec.request
    places = []
    if request.has_path:
        places.append("путь URL")
    if request.has_query:
        places.append("строка запроса")
    if request.body_kind != "none":
        places.append(f"тело ({request.body_kind})")
    lines.append(f"    Параметры передаются: {', '.join(places) or 'без параметров'}.")
    if request.contract_locations:
        lines.append(
            "    contract_id передаётся: " + ", ".join(sorted(request.contract_locations)) + "."
        )
    lines.append(
        "    Заголовки: api_key, date_time"
        + (", session_id (после авторизации)" if spec.requires_session else "")
        + "."
    )
    return lines


def wrap(text: str, indent: str = "    ") -> list[str]:
    return textwrap.wrap(text, width=92, initial_indent=indent, subsequent_indent=indent) or [
        indent
    ]


def flag(value: bool | None) -> str:
    return "не указано" if value is None else ("да" if value else "нет")


def build_file(
    spec: Any,
    service: str,
    function: Any,
    contract: dict[str, Any],
    check_description: str,
    summary: str,
    descriptions: dict[str, dict[str, str]],
    shared: dict[str, str],
) -> str:
    operation = spec.name
    signature = inspect.signature(function)
    variants = contract.get("variants") or [{}]
    contract_params = {
        str(item.get("path")): item for item in variants[0].get("request_parameters") or []
    }
    title = summary or contract.get("summary") or function.__doc__ or operation
    mutating = is_mutating(spec)
    doc: list[str] = [f"{operation} — {' '.join(str(title).split())}", ""]
    doc.append("Что делает")
    doc += wrap(check_description or (function.__doc__ or "").strip() or "Описание не найдено.")
    doc.append(
        f"    Изменяет данные: {'да' if mutating else 'нет'}. Тарификация: {flag(spec.billable)}. "
        f"Демо-стенд: {flag(spec.demo_available)}."
    )
    doc.append(f"    Вызов SDK: client.{service}.{operation}(...)")
    if contract.get("summary"):
        doc.append(f"    Раздел спецификации 1.1.60: {contract['summary']}")
    doc += ["", "HTTP-запрос"] + route_lines(spec)
    doc += ["", "Параметры метода SDK"]
    params = parameter_lines(signature, contract_params, descriptions.get(operation, {}), shared)
    doc += params or ["      нет параметров"]

    request_models: list[type[BaseModel]] = []
    seen: set[type] = set()
    import apisdkopti24.models as sdk_models

    for name in spec.request.request_models:
        request_models += model_tree(getattr(sdk_models, name, None), seen)
    for parameter in list(signature.parameters.values())[1:]:
        request_models += model_tree(parameter.annotation, seen)
    doc += ["", "Модели проверки входящих данных (запрос)"]
    doc += (
        describe_models(request_models)
        if request_models
        else ["      отдельной модели нет: параметры проверяются сигнатурой и проверками метода"]
    )
    doc += ["", "Модели проверки исходящих данных (ответ API)"]
    if spec.response_kind != "json" or spec.response_type is None:
        doc.append("      ответ — файл (bytes); модель не применяется")
    else:
        doc += describe_models(model_tree(spec.response_type, set()))

    doc += ["", "Возможные ошибки", "    До отправки запроса (локальные проверки SDK):"]
    checks = local_errors(function)
    doc += [f"      {item}" for item in checks] or ["      специальных проверок нет"]
    doc.append("      pydantic.ValidationError / RequestValidationError — неверный тип или формат")
    doc.append("      параметра по модели запроса.")
    if operation == "auth_user":
        doc.append("      ContractSelectionError — несколько договоров, а contract_id не указан.")
    doc.append(API_ERRORS)
    doc.append(
        f"    Повтор при сетевой ошибке: {'только безопасные читающие' if spec.retry_class == 'safe' else spec.retry_class}; "
        f"идемпотентность: {flag(spec.idempotent)}."
    )

    body_lines = []
    imports = {"common", "method_value", "run"}
    for parameter in list(signature.parameters.values())[1:]:
        if parameter.name in SKIPPED_PARAMS:
            continue
        expression = value_expression(operation, parameter)
        if "decimal(" in (expression or ""):
            imports.add("decimal")
        body_lines.append(f"    {parameter.name!r}: {expression},")
    if any(op == operation for op, _ in MODEL_LISTS):
        imports.add("models")

    docstring = "\n".join(line.rstrip() for line in doc)
    params_block = (
        "PARAMS = {\n" + "\n".join(body_lines) + "\n}\n" if body_lines else "PARAMS: dict = {}\n"
    )
    return (
        f'"""{docstring}\n"""\n\n'
        f"from _common import {', '.join(sorted(imports))}  # noqa: F401\n"
        "\n"
        "# Значения берутся из test_data.json: common — общие данные, methods — данные метода,\n"
        "# overrides — замена любого параметра ниже. Файл создаётся генератором\n"
        "# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.\n"
        f"{params_block}\n"
        f"DESCRIPTION = {check_description or title!r}\n\n"
        'if __name__ == "__main__":\n'
        f"    run({operation!r}, PARAMS, mutating={mutating}, description=DESCRIPTION)\n"
    )


def build_all() -> dict[Path, str]:
    registry = {spec.name: spec for spec in build_default_registry().list_all()}
    methods = service_methods()
    contracts = load_contracts()
    descriptions, shared = load_parameter_descriptions()
    summaries = load_summaries()
    check_descriptions = load_check_descriptions()
    outputs: dict[Path, str] = {}
    for operation, spec in sorted(registry.items()):
        service, function = methods[operation]
        source = build_file(
            spec,
            service,
            function,
            contracts.get(operation, {}),
            check_descriptions.get(operation, ""),
            summaries.get(operation, ""),
            descriptions,
            shared,
        )
        # Форматирование как в репозитории: файлы проходят black --check в CI.
        outputs[LIVE_CHECK_DIR / f"{operation}.py"] = black.format_str(source, mode=BLACK_MODE)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--force", action="store_true", help="Перезаписать существующие файлы")
    mode.add_argument("--check", action="store_true", help="Проверить актуальность файлов")
    args = parser.parse_args()

    outputs = build_all()
    if args.check:
        stale = sorted(
            path.name
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        )
        if stale:
            raise SystemExit(
                "Файлы tools/live_check устарели; выполните "
                "python tools/live_check/_generate.py --force:\n" + "\n".join(stale)
            )
        print(f"Файлы tools/live_check актуальны: {len(outputs)}")
        return
    written = 0
    for path, content in outputs.items():
        if path.exists() and not args.force:
            continue
        path.write_text(content, encoding="utf-8")
        written += 1
    print(f"Файлов методов: {len(outputs)}, записано: {written}")


if __name__ == "__main__":
    main()
