from __future__ import annotations

# ruff: noqa: E402, I001 -- src-layout bootstrap выполняется до импортов SDK.

import asyncio
import argparse
import inspect
import json
import random
import re
import sys
from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, get_args, get_origin

import httpx

# При прямом запуске файла из checkout пакет находится в каталоге src/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if SRC_ROOT.is_dir():
    sys.path.insert(0, str(SRC_ROOT))

import apisdkopti24.models as sdk_models
from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    ContractSelectionError,
    EnvironmentCredentialsProvider,
    __version__,
)
from apisdkopti24.models.limits import LimitRequestItem
from apisdkopti24.models.region_limits import RegionLimitRequestItem
from apisdkopti24.models.restrictions import RestrictionRequestItem
from apisdkopti24.operations import OperationSpec
from apisdkopti24.registry import build_default_registry
from apisdkopti24.transport import AsyncTransport
from apisdkopti24.utils import sanitize_for_logging

Check = Callable[[APIClient, dict[str, Any]], Awaitable[Any]]

DEFAULT_ENV_CANDIDATES = (
    Path.cwd() / ".env",
    PROJECT_ROOT / ".env",
    Path(__file__).with_name(".env"),
)
CURRENT_CLIENT: APIClient | None = None
CURRENT_STATE: dict[str, Any] = {}
FIELD_HELP: dict[str, list[str]] = {}
METHOD_DESCRIPTIONS: dict[str, str] = {}
OPERATION_MODELS: dict[str, type[Any] | None] = {}
OPERATIONS: dict[str, OperationSpec[Any]] = {}
CURRENT_METHOD_NAME: str | None = None
MODEL_MATRIX_PATH = PROJECT_ROOT / "specifications" / "model-matrix-v1.1.60.json"
MODEL_MATRIX: dict[str, dict[str, Any]] = {}
REFERENCE_DICTIONARIES = (
    "Goods",
    "ProductType",
    "ProductGroup",
    "Country",
    "Region",
    "Office",
    "Services",
)


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


class SkipMethod(Exception):
    pass


class RetryMethod(Exception):
    pass


def resolve_env_file() -> Path:
    parser = argparse.ArgumentParser(description="Интерактивная проверка 89 методов SDK")
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Путь к .env с API_BASE_URL, API_KEY, API_LOGIN и API_PASSWORD",
    )
    args = parser.parse_args()
    if args.env_file is not None:
        env_file = args.env_file.expanduser().resolve()
        if not env_file.is_file():
            parser.error(f"файл не найден: {env_file}")
        return env_file
    for candidate in DEFAULT_ENV_CANDIDATES:
        if candidate.is_file():
            return candidate.resolve()
    searched = "\n".join(f"- {candidate}" for candidate in DEFAULT_ENV_CANDIDATES)
    parser.error(
        "не найден .env. Передайте --env-file /полный/путь/.env "
        f"или создайте файл в одном из мест:\n{searched}"
    )


EXAMPLE_HINTS: tuple[tuple[str, str], ...] = (
    ("period", "2026-07 или 2026-07-01:2026-07-31, если API поддерживает период"),
    ("date_from", "2026-07-01"),
    ("date_to", "2026-07-31"),
    ("date_start", "2026-07-01"),
    ("date_end", "2026-07-31"),
    ("start yyyy", "2026-07-01"),
    ("end yyyy", "2026-07-31"),
    ("page_limit", "100"),
    ("page_offset", "0"),
    ("on_page", "10"),
    ("onpage", "10"),
    ("page", "1"),
    ("count", "1"),
    ("amount", "100.00"),
    ("email", "user@example.com"),
    ("emails", "user@example.com,manager@example.com"),
    ("fmt", "pdf или xlsx"),
    ("report_format", "xlsx"),
    ("format", "xlsx"),
    ("product wallet", "wallet или limit"),
    ("type_ (limit", "Limit или Wallet"),
    ("type_, enter", "Limit или Wallet"),
    ("type_", "Limit"),
    ("mobile", "+79991234567"),
    ("uuid", "550e8400-e29b-41d4-a716-446655440000"),
    ("card_ids", "56745380,56745381"),
    ("card_id", "56745380"),
    ("group_id", "1-ABCDEF"),
    ("user_id", "1-USERID"),
    ("template_id", "1-TEMPLATE"),
    ("limit_id", "1-LIMIT"),
    ("regionlimit_id", "1-REGIONLIMIT"),
    ("restriction_id", "1-RESTRICTION"),
    ("georestriction_id", "1-GEORESTRICTION"),
    ("invite_id", "1-INVITE"),
    ("job_id", "1-REPORTJOB"),
    ("transaction_id", "123456789"),
    ("document ids", "1-DOC1,1-DOC2"),
    ("contract ids", "1-13ZVGRYV,1-18UUFGT5"),
    ("contracts json list", '[{"sid":"1-13ZVGRYV","use_mpc":false}]'),
    ("goods json list", '[{"code":"1-276PF01","quantity":"10","price":"55.50"}]'),
    ("goods codes", "1-276PF01,1-276PF02"),
    ("payload json object", '{"request_id":"test-001"}'),
    (
        "invite data json object",
        '{"role":"Driver","mobile":"+79991234567","contracts":[{"sid":"1-13ZVGRYV"}]}',
    ),
    (
        "templatelimitcreaterequest json object",
        '{"product_type":"1-276PF01","amount":{"unit":"LIT","value":10},'
        '"time":{"type":3,"number":1}}',
    ),
    (
        "templaterestrictioncreaterequest json object",
        '{"product_type":"1-276PF01","restriction_type":2}',
    ),
    (
        "templategeorestrictioncreaterequest json object",
        '{"country":"RUS","region":"54","restriction_type":1}',
    ),
    (
        "limits json list",
        '[{"card_id":"56745380","productType":"1-276PF01",'
        '"amount":{"unit":"LIT","value":10},"time":{"type":3,"number":1}}]',
    ),
    (
        "region_limits json list",
        '[{"card_id":"56745380","country":"RUS","region":"54","limit_type":1}]',
    ),
    (
        "restrictions json list",
        '[{"card_id":"56745380","productType":"1-276PF01","restriction_type":2}]',
    ),
    ("cards_list json list", '[{"card_id":"56745380"}]'),
    ("filter json object", '{"status":"Active"}'),
    (
        "params json object",
        '{"contract_id":"1-13ZVGRYV","date_from":"2026-07-01","date_to":"2026-07-31"}',
    ),
    ("dictionary name", "ProductType"),
    ("poi_id", "1-POI"),
    ("office_id", "1-OFFICE"),
    ("code", "1234"),
    ("comment", "Тестовый комментарий SDK"),
    ("name", "SDK test"),
)


def color(text: str, value: str) -> str:
    return f"{value}{text}{Color.RESET}"


def sanitize_http_value(value: Any) -> Any:
    return sanitize_for_logging(value)


def body_preview(kwargs: dict[str, Any]) -> Any:
    if "json" in kwargs:
        return sanitize_http_value(kwargs["json"])
    if "data" in kwargs:
        return sanitize_http_value(kwargs["data"])
    if "content" in kwargs:
        content = kwargs["content"]
        if isinstance(content, bytes):
            return f"<bytes {len(content)}>"
        return sanitize_http_value(content)
    return None


def final_url(url: str, params: Any) -> str:
    if not params:
        return url
    try:
        return str(httpx.URL(url, params=params))
    except Exception:
        return f"{url} params={params!r}"


class TracingHTTPClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient()

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        print_http_request(method, url, kwargs)
        response = await self._client.request(method, url, **kwargs)
        print_http_response(response)
        return response

    def stream(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> AbstractAsyncContextManager[httpx.Response]:
        print_http_request(method, url, kwargs)
        return self._client.stream(method, url, **kwargs)

    async def aclose(self) -> None:
        await self._client.aclose()


def print_http_request(method: str, url: str, kwargs: dict[str, Any]) -> None:
    headers = sanitize_http_value(dict(kwargs.get("headers") or {}))
    params = sanitize_http_value(kwargs.get("params"))
    body = body_preview(kwargs)
    print(color("\nHTTP-запрос, отправленный SDK:", Color.BOLD + Color.MAGENTA))
    print(f"operation: {CURRENT_METHOD_NAME or 'unknown'}")
    print(f"method: {method.upper()}")
    print(f"url: {final_url(url, kwargs.get('params'))}")
    print("headers:")
    print(color(json.dumps(headers, ensure_ascii=False, indent=2, default=str), Color.DIM))
    if params:
        print("query params:")
        print(color(json.dumps(params, ensure_ascii=False, indent=2, default=str), Color.YELLOW))
    if body is None:
        print("body: <empty>")
    else:
        print("body:")
        print(color(json.dumps(body, ensure_ascii=False, indent=2, default=str), Color.YELLOW))


def print_http_response(response: httpx.Response) -> None:
    """Показать фактический ответ до преобразования в Pydantic-модель."""
    print(color("\nHTTP-ответ, полученный SDK:", Color.BOLD + Color.MAGENTA))
    print(f"status: {response.status_code}")
    print(f"content-type: {response.headers.get('content-type', '<not set>')}")
    try:
        payload: Any = response.json()
    except (ValueError, UnicodeDecodeError):
        preview = response.content[:1000]
        payload = f"<bytes {len(response.content)}: {preview!r}>"
    print(
        color(
            json.dumps(sanitize_http_value(payload), ensure_ascii=False, indent=2, default=str),
            Color.DIM,
        )
    )


def normalize_help_key(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum() or char == "_")


def format_annotation(annotation: Any) -> str:
    if annotation is None:
        return "None"
    if annotation is Any:
        return "Any"
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is None:
        return getattr(annotation, "__name__", str(annotation).replace("typing.", ""))
    if origin in {list, tuple, dict}:
        inner = ", ".join(format_annotation(arg) for arg in args)
        return f"{getattr(origin, '__name__', str(origin))}[{inner}]"
    if args:
        return " | ".join(format_annotation(arg) for arg in args)
    return str(annotation).replace("typing.", "")


def field_aliases(field: Any) -> list[str]:
    aliases: list[str] = []
    for attr_name in ("alias", "serialization_alias"):
        value = getattr(field, attr_name, None)
        if isinstance(value, str):
            aliases.append(value)
    validation_alias = getattr(field, "validation_alias", None)
    if isinstance(validation_alias, str):
        aliases.append(validation_alias)
    choices = getattr(validation_alias, "choices", None)
    if isinstance(choices, list | tuple):
        aliases.extend(str(choice) for choice in choices)
    return aliases


def register_field_help(key: str, text: str) -> None:
    normalized = normalize_help_key(key)
    if not normalized:
        return
    values = FIELD_HELP.setdefault(normalized, [])
    if text not in values:
        values.append(text)


def build_field_help() -> None:
    if FIELD_HELP:
        return
    for model_name in getattr(sdk_models, "__all__", []):
        model = getattr(sdk_models, model_name, None)
        fields = getattr(model, "model_fields", None)
        if not fields:
            continue
        for field_name, field in fields.items():
            field_type = format_annotation(getattr(field, "annotation", Any))
            required = "обязательный" if field.is_required() else "необязательный"
            description = getattr(field, "description", None) or "описание в модели не задано"
            text = f"{model_name}.{field_name}: {field_type}, {required}. {description}"
            register_field_help(field_name, text)
            for alias in field_aliases(field):
                register_field_help(alias, text)


def build_operation_models() -> dict[str, type[Any] | None]:
    if OPERATION_MODELS:
        return OPERATION_MODELS
    for operation in build_default_registry().list_all():
        OPERATION_MODELS[operation.name] = operation.response_type
        OPERATIONS[operation.name] = operation
    return OPERATION_MODELS


def build_model_matrix() -> dict[str, dict[str, Any]]:
    if MODEL_MATRIX or not MODEL_MATRIX_PATH.exists():
        return MODEL_MATRIX
    payload = json.loads(MODEL_MATRIX_PATH.read_text(encoding="utf-8"))
    for operation in payload.get("operations", []):
        if isinstance(operation, dict) and isinstance(operation.get("operation"), str):
            MODEL_MATRIX[operation["operation"]] = operation
    return MODEL_MATRIX


def print_operation_request_contract(method_name: str) -> None:
    """Показать wire-контракт запроса из OperationSpec и полной матрицы."""
    build_operation_models()
    operation = OPERATIONS.get(method_name)
    if operation is not None:
        request = operation.request
        print(color("OperationSpec:", Color.BOLD))
        print(
            f"- {operation.http_method} /{operation.default_version}/{operation.endpoint}; "
            f"response={operation.response_kind}; retry={operation.retry_class}; "
            f"idempotent={operation.idempotent}"
        )
        print(
            "- request metadata: "
            f"path={request.has_path}, query={request.has_query}, "
            f"body={request.body_kind}, contract={sorted(request.contract_locations)}"
        )

    matrix_entry = build_model_matrix().get(method_name)
    if matrix_entry is None:
        print(color("Матрица параметров недоступна вне checkout репозитория.", Color.DIM))
        return
    variants = matrix_entry.get("variants") or []
    if not variants:
        return
    print(color("Параметры запроса по спецификации:", Color.BOLD))
    for variant in variants:
        route_name = variant.get("route_name", "default")
        fields = variant.get("request") or []
        if len(variants) > 1:
            print(f"  route={route_name}")
        if not fields:
            print("- параметры отсутствуют")
        for field in fields:
            print(
                f"- {field['path']}: {field['type']}, location={field['location']}, "
                f"обяз.={field['required']}. {field['description']}"
            )


def nested_model_types(annotation: Any) -> list[type[Any]]:
    result: list[type[Any]] = []
    if isinstance(annotation, type) and hasattr(annotation, "model_fields"):
        result.append(annotation)
    for arg in get_args(annotation):
        result.extend(nested_model_types(arg))
    return result


def print_model_schema(
    model: type[Any],
    *,
    indent: int = 0,
    seen: set[type[Any]] | None = None,
) -> None:
    seen = seen or set()
    prefix = " " * indent
    if model in seen:
        print(color(f"{prefix}{model.__name__}: уже описана выше", Color.DIM))
        return
    seen.add(model)
    fields = getattr(model, "model_fields", None)
    if not fields:
        print(color(f"{prefix}{model.__name__}: Pydantic-поля не найдены", Color.YELLOW))
        return
    print(color(f"{prefix}{model.__name__}", Color.BOLD))
    for field_name, field in fields.items():
        annotation = getattr(field, "annotation", Any)
        field_type = format_annotation(annotation)
        required = "обязательное" if field.is_required() else "необязательное"
        alias_values = field_aliases(field)
        alias_text = f", alias={alias_values}" if alias_values else ""
        description = getattr(field, "description", None) or "описание отсутствует"
        print(f"{prefix}- {field_name}: {field_type}, {required}{alias_text}. {description}")
        for nested_model in nested_model_types(annotation):
            if nested_model is not model:
                print_model_schema(nested_model, indent=indent + 4, seen=seen)


def print_operation_model(method_name: str) -> None:
    model = build_operation_models().get(method_name)
    print(color("Pydantic-модель ответа:", Color.BOLD))
    if model is None:
        print(
            color("модель ответа не найдена или метод возвращает bytes/raw payload", Color.YELLOW)
        )
        return
    print_model_schema(model)


def extract_input_key(name: str) -> str:
    return name.split(",", 1)[0].split(" ", 1)[0].strip()


def field_help_for(name: str) -> list[str]:
    build_field_help()
    key = normalize_help_key(extract_input_key(name))
    if not key:
        return []
    return FIELD_HELP.get(key, [])[:3]


def print_input_help(name: str, explicit_example: str | None = None) -> None:
    hint = example_for(name, explicit_example)
    if hint:
        print(color(f"пример для {name}: {hint}", Color.DIM))
    descriptions = field_help_for(name)
    for description in descriptions:
        print(color(f"описание {name}: {description}", Color.DIM))


def build_method_descriptions() -> dict[str, str]:
    if METHOD_DESCRIPTIONS:
        return METHOD_DESCRIPTIONS

    lines = Path(__file__).read_text(encoding="utf-8").splitlines()
    pending_comments: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            pending_comments.append(stripped[2:])
            continue
        if stripped.startswith("async def check_"):
            method = stripped.split("async def check_", 1)[1].split("(", 1)[0]
            comments = [item for item in pending_comments if item and not item.startswith("Метод ")]
            METHOD_DESCRIPTIONS[method] = " ".join(comments[-3:])
        pending_comments = []
    return METHOD_DESCRIPTIONS


def print_method_intro(method_name: str) -> None:
    description = build_method_descriptions().get(method_name, "Описание метода не найдено.")
    print_header(f"Следующий метод: {method_name}")
    print(color("Что делает:", Color.BOLD), description)
    print(color("Путь клиента:", Color.BOLD), color(find_service_path(method_name), Color.MAGENTA))
    print(color("Автоданные:", Color.BOLD), color(known_values_text(), Color.DIM))
    print_operation_request_contract(method_name)
    print_operation_model(method_name)
    print(color("Дальше скрипт запросит входные переменные.", Color.DIM))


def example_for(name: str, explicit: str | None = None) -> str | None:
    if explicit:
        return explicit
    normalized = name.lower()
    for marker, example in EXAMPLE_HINTS:
        if marker in normalized:
            return example
    return None


def print_header(title: str) -> None:
    print("\n" + color("=" * 100, Color.BLUE))
    print(color(title, Color.BOLD + Color.CYAN))
    print(color("=" * 100, Color.BLUE))


def find_service_path(method_name: str) -> str:
    if CURRENT_CLIENT is None:
        return f"client.<service>.{method_name}(...)"
    for service_field in CURRENT_CLIENT.services.__dataclass_fields__:
        service = getattr(CURRENT_CLIENT.services, service_field)
        if callable(getattr(service, method_name, None)):
            return f"client.{service_field}.{method_name}(...)"
    return f"client.<service>.{method_name}(...)"


def known_values_text() -> str:
    keys = [
        "contract_id",
        "card_id",
        "user_id",
        "group_id",
        "template_id",
        "limit_id",
        "regionlimit_id",
        "restriction_id",
        "georestriction_id",
        "invite_id",
        "job_id",
        "transaction_id",
        "document_id",
    ]
    values = [f"{key}={CURRENT_STATE[key]}" for key in keys if CURRENT_STATE.get(key)]
    return ", ".join(values) if values else "пока нет"


def print_request(method_name: str, description: str, payload: dict[str, Any]) -> None:
    del description
    print(color(f"\n{method_name}: входные данные готовы", Color.BOLD + Color.BLUE))
    print(color("Будет передано в API:", Color.BOLD))
    print(color(json.dumps(payload, ensure_ascii=False, indent=2, default=str), Color.YELLOW))


def close_if_pending(awaitable: Awaitable[Any]) -> None:
    if inspect.iscoroutine(awaitable):
        awaitable.close()


def prompt_before_call(*, mutating: bool, awaitable: Awaitable[Any] | None = None) -> None:
    if mutating:
        print(
            color("Внимание:", Color.BOLD + Color.RED),
            "метод может создать, изменить, удалить данные или быть тарифицируемым.",
        )
        prompt = "Enter/yes — выполнить, e — изменить входные данные, s/no — пропустить: "
        allowed_run = {"", "yes", "y", "да", "д"}
    else:
        prompt = "Enter — выполнить, e — изменить входные данные, s — пропустить: "
        allowed_run = {""}

    answer = input(color(prompt, Color.CYAN)).strip().lower()
    if answer in {"e", "edit", "и", "изменить"}:
        if awaitable is not None:
            close_if_pending(awaitable)
        raise RetryMethod("Повтор ввода параметров")
    if answer in {"s", "skip", "n", "no", "нет"}:
        if awaitable is not None:
            close_if_pending(awaitable)
        raise SkipMethod("Пользователь пропустил метод")
    if answer not in allowed_run:
        if awaitable is not None:
            close_if_pending(awaitable)
        raise SkipMethod("Нет явного разрешения на запуск")


def print_result(method_name: str, result: Any) -> None:
    remember_result(method_name, result)
    print(color(f"\n{method_name}: OK", Color.BOLD + Color.GREEN))
    if isinstance(result, bytes):
        print(f"Ответ: bytes, размер {len(result)} байт")
        return
    if hasattr(result, "model_dump_json"):
        print(result.model_dump_json(indent=2, by_alias=True))
        return
    print(result)


def result_payload(result: Any) -> Any:
    if hasattr(result, "model_dump"):
        return result.model_dump(by_alias=True)
    return result


def as_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0


def print_tariff_usage_summary(result: Any, *, default_quota: int = 500) -> None:
    payload = result_payload(result)
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        print(color("Не удалось посчитать тариф: неожиданный формат data.", Color.YELLOW))
        return

    methods = data.get("methods")
    methods_info = data.get("methods_info")
    client_info = data.get("client_info")
    if not isinstance(methods, dict) or not isinstance(methods_info, dict):
        print(color("Не удалось посчитать тариф: нет methods или methods_info.", Color.YELLOW))
        return

    billable_catalog = methods_info.get("actions_bill") or {}
    free_catalog = methods_info.get("actions_not_bill") or {}
    if not isinstance(billable_catalog, dict) or not isinstance(free_catalog, dict):
        print(
            color(
                "Не удалось посчитать тариф: неверный формат actions_bill/actions_not_bill.",
                Color.YELLOW,
            )
        )
        return

    billable_used: dict[str, int] = {}
    free_used: dict[str, int] = {}
    unknown_used: dict[str, int] = {}
    for method_code, raw_count in methods.items():
        if method_code == "all":
            continue
        count = as_int(raw_count)
        if count <= 0:
            continue
        if method_code in billable_catalog:
            billable_used[method_code] = count
        elif method_code in free_catalog:
            free_used[method_code] = count
        else:
            unknown_used[method_code] = count

    quota = default_quota
    if isinstance(client_info, dict):
        quota = as_int(client_info.get("Queries")) or default_quota
    used = sum(billable_used.values())
    remaining = max(quota - used, 0)

    print(color("\nПрактический расчёт тарификации", Color.BOLD + Color.MAGENTA))
    print(f"Период: {data.get('from')} — {data.get('to')}")
    print(f"Лимит тарифицируемых запросов: {quota}")
    print(f"Тарифицируемых запросов использовано: {used}")
    print(color(f"Остаток тарифицируемых запросов: {remaining}", Color.BOLD + Color.GREEN))

    if billable_used:
        print(color("Тарифицируемые методы с вызовами:", Color.BOLD))
        for method_code, count in sorted(billable_used.items()):
            print(f"- {method_code}: {count} — {billable_catalog.get(method_code)}")
    if free_used:
        print(color("Нетарифицируемые методы с вызовами:", Color.BOLD))
        for method_code, count in sorted(free_used.items()):
            print(f"- {method_code}: {count} — {free_catalog.get(method_code)}")
    if unknown_used:
        print(color("Методы с неизвестной тарификацией:", Color.BOLD + Color.YELLOW))
        for method_code, count in sorted(unknown_used.items()):
            print(f"- {method_code}: {count}")


def compact_error(exc: Exception, *, max_length: int = 700) -> str:
    message = str(exc)
    if "<html" in message.lower():
        error_id = re.search(r'ERROR_ID"?\s+content="([^"]+)"|ID-запроса:\s*([^<\s]+)', message)
        error_id_value = next(
            (item for item in (error_id.groups() if error_id else ()) if item), None
        )
        waf_message = "сервер вернул HTML/WAF-страницу вместо JSON"
        if error_id_value:
            waf_message = f"{waf_message}, ERROR_ID={error_id_value}"
        return f"{type(exc).__name__}: {waf_message}"
    if len(message) > max_length:
        return f"{type(exc).__name__}: {message[:max_length]}..."
    return f"{type(exc).__name__}: {message}"


def first_result_item(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if isinstance(data, dict):
        result = data.get("result")
        if isinstance(result, list) and result and isinstance(result[0], dict):
            return result[0]
    return None


def remember_value(key: str, value: Any) -> None:
    if value is not None and value != "":
        CURRENT_STATE.setdefault(key, str(value))


def remember_result(method_name: str, result: Any) -> None:
    payload = result_payload(result)
    item = first_result_item(payload)
    data = payload.get("data") if isinstance(payload, dict) else None

    if method_name in {"get_cards_v1", "get_cards_v2", "get_cards_by_group"} and item:
        remember_value("card_id", item.get("id") or item.get("sid") or item.get("card_id"))
    if method_name == "get_users" and item:
        remember_value("user_id", item.get("id") or item.get("sid") or item.get("user_id"))
    if method_name in {"get_templates", "create_template", "update_template"}:
        remember_value("template_id", data if isinstance(data, str) else (item or {}).get("id"))
    if method_name in {"get_card_groups", "set_card_group"} and item:
        remember_value("group_id", item.get("id") or item.get("sid") or item.get("group_id"))
    if method_name in {"get_invites", "create_invite", "resend_invite"} and item:
        remember_value("invite_id", item.get("id") or item.get("invite_id"))
    if method_name in {
        "get_report_jobs",
        "get_report_job_list_v1",
        "order_report",
        "order_report_v1",
    }:
        remember_value("job_id", data if isinstance(data, str) else (item or {}).get("id"))
    if method_name in {"get_limits", "set_limit"}:
        remember_value(
            "limit_id", data[0] if isinstance(data, list) and data else (item or {}).get("id")
        )
    if method_name in {"get_region_limits", "set_region_limit"}:
        remember_value(
            "regionlimit_id",
            data[0] if isinstance(data, list) and data else (item or {}).get("id"),
        )
    if method_name in {"get_restrictions", "set_restriction"}:
        remember_value(
            "restriction_id",
            data[0] if isinstance(data, list) and data else (item or {}).get("id"),
        )
    if method_name == "get_template_limits" and item:
        remember_value("limit_id", item.get("id") or item.get("limit_id"))
    if method_name == "get_template_restrictions" and item:
        remember_value("restriction_id", item.get("id") or item.get("restriction_id"))
    if method_name == "get_template_georestrictions" and item:
        remember_value("georestriction_id", item.get("id") or item.get("georestriction_id"))
    if (
        method_name in {"get_transactions_v1", "get_transactions_v2", "get_card_transactions_v2"}
        and item
    ):
        remember_value("transaction_id", item.get("id") or item.get("transaction_id"))
    if method_name == "get_documents" and item:
        remember_value("document_id", item.get("id") or item.get("document_id"))


def ask_value(
    name: str,
    *,
    default: str | None = None,
    required: bool = True,
    example: str | None = None,
) -> str | None:
    suffix = f" [{default}]" if default else ""
    print_input_help(name, example)
    value = input(color(f"{name}{suffix}: ", Color.CYAN)).strip()
    if not value and default is not None:
        return default
    if not value and required:
        raise SkipMethod(f"Не указан обязательный параметр {name}")
    return value or None


def ask_bool(name: str, *, default: bool, example: str | None = None) -> bool:
    default_text = "yes" if default else "no"
    print_input_help(name, example or "yes или no")
    value = input(color(f"{name} [yes/no, default={default_text}]: ", Color.CYAN)).strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "д", "да", "1", "true"}


def ask_decimal(name: str, *, example: str | None = None) -> Decimal:
    return Decimal(ask_value(name, example=example or "100.00") or "0")


def ask_csv(name: str, *, required: bool = True, example: str | None = None) -> list[str]:
    raw = ask_value(name, required=required, example=example)
    if raw is None:
        return []
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if required and not values:
        raise SkipMethod(f"Не указан список {name}")
    return values


def ask_json(name: str, *, example: str | None = None) -> Any:
    raw = ask_value(name, example=example)
    try:
        return json.loads(raw or "")
    except json.JSONDecodeError as exc:
        raise SkipMethod(f"Некорректный JSON для {name}: {exc}") from exc


def ask_target() -> dict[str, str]:
    card_id = ask_value(
        "card_id, если проверяем карту",
        default=saved(CURRENT_STATE, "card_id"),
        required=False,
    )
    group_id = ask_value(
        "group_id, если проверяем группу",
        default=saved(CURRENT_STATE, "group_id"),
        required=False,
    )
    payload: dict[str, str] = {}
    if card_id:
        payload["card_id"] = card_id
    if group_id:
        payload["group_id"] = group_id
    return payload


async def confirm_mutation(method_name: str, description: str, payload: dict[str, Any]) -> None:
    print_request(method_name, description, payload)
    prompt_before_call(mutating=True)


async def run_read(
    method_name: str, description: str, payload: dict[str, Any], call: Awaitable[Any]
) -> Any:
    print_request(method_name, description, payload)
    prompt_before_call(mutating=False, awaitable=call)
    return await call


async def run_mutation(
    method_name: str,
    description: str,
    payload: dict[str, Any],
    call_factory: Callable[[], Awaitable[Any]],
) -> Any:
    await confirm_mutation(method_name, description, payload)
    return await call_factory()


def contract_id(state: dict[str, Any]) -> str:
    value = state.get("contract_id")
    if not value:
        raise SkipMethod("Договор ещё не выбран")
    return str(value)


def first_card_id(state: dict[str, Any]) -> str | None:
    return state.get("card_id")


def first_user_id(state: dict[str, Any]) -> str | None:
    return state.get("user_id")


def saved(state: dict[str, Any], key: str) -> str | None:
    return state.get(key)


def as_payload(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True)
    return value


def response_result_items(response: Any) -> list[dict[str, Any]]:
    payload = as_payload(response)
    data = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(data, dict):
        result = data.get("result")
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def pick_value(items: list[dict[str, Any]], *keys: str) -> str | None:
    candidates: list[str] = []
    for item in items:
        for key in keys:
            value = item.get(key)
            if value not in (None, "", []):
                candidates.append(str(value))
    return random.choice(candidates) if candidates else None


def price_value(price: dict[str, Any]) -> float:
    raw_price = price.get("Price") or price.get("price") or price.get("value") or 1
    try:
        return float(str(raw_price).replace(",", "."))
    except ValueError:
        return 1.0


def active_station_with_price(
    stations: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for station in stations:
        if station.get("accept_cards") is False:
            continue
        if str(station.get("status") or "") == "258":
            continue
        prices = station.get("prices")
        if not isinstance(prices, list):
            continue
        for price in prices:
            if isinstance(price, dict) and pick_value([price], "GoodsCode", "code", "ID"):
                candidates.append((station, price))
    return random.choice(candidates) if candidates else None


def store_reference_if_found(refs: dict[str, Any], key: str, value: Any) -> None:
    if value not in (None, "", []):
        refs[key] = value


def reference_store(state: dict[str, Any]) -> dict[str, Any]:
    return state.setdefault("reference_data", {})


def reference_value(state: dict[str, Any], key: str) -> str | None:
    value = reference_store(state).get(key)
    if value not in (None, "", []):
        return str(value)
    return None


async def fetch_dictionary_items(
    client: APIClient,
    state: dict[str, Any],
    name: str,
) -> list[dict[str, Any]]:
    refs = reference_store(state)
    cache_key = f"dictionary:{name}"
    if cache_key not in refs:
        try:
            response = await client.dictionaries.get_dictionary(name=name)
            refs[cache_key] = response_result_items(response)
            print(color(f"Справочник {name}: загружено {len(refs[cache_key])} записей", Color.DIM))
        except Exception as exc:
            refs[cache_key] = []
            print(
                color(
                    f"Справочник {name}: не удалось загрузить ({type(exc).__name__}: {exc})",
                    Color.YELLOW,
                )
            )
    return refs[cache_key]


async def ensure_reference_data(
    client: APIClient,
    state: dict[str, Any],
    *,
    dictionaries: tuple[str, ...] = (),
    need_azs: bool = False,
) -> None:
    refs = reference_store(state)
    if need_azs and not refs.get("poi_id"):
        try:
            response = await client.dictionaries.get_azs_list_v2()
            stations = response_result_items(response)
            station_with_price = active_station_with_price(stations)
            if not station_with_price:
                response = await client.dictionaries.get_azs_list_v1(page=1, onpage=50)
                stations = response_result_items(response)
                station_with_price = active_station_with_price(stations)
            if station_with_price:
                station, price = station_with_price
                store_reference_if_found(refs, "poi_id", pick_value([station], "id", "siebel_id"))
                store_reference_if_found(
                    refs, "goods_code", pick_value([price], "GoodsCode", "code", "ID")
                )
                store_reference_if_found(refs, "goods_price", price_value(price))
                refs["country"] = refs.get("country") or pick_value(
                    [station], "country_code", "countryCode"
                )
                refs["region"] = refs.get("region") or pick_value(
                    [station], "region_code", "regionCode"
                )
                print(
                    color(
                        "АЗС: подобраны "
                        f"poi_id={refs.get('poi_id')}, "
                        f"goods_code={refs.get('goods_code')}, "
                        f"goods_price={refs.get('goods_price')}",
                        Color.DIM,
                    )
                )
            else:
                print(
                    color(
                        "АЗС: не найдено точки с ценами, poi_id нужно ввести вручную",
                        Color.YELLOW,
                    )
                )
        except Exception as exc:
            print(
                color(
                    f"АЗС: не удалось подобрать значения ({type(exc).__name__}: {exc})",
                    Color.YELLOW,
                )
            )

    for dictionary_name in dictionaries:
        items = await fetch_dictionary_items(client, state, dictionary_name)
        if dictionary_name == "Goods":
            refs["goods_code"] = refs.get("goods_code") or pick_value(items, "code", "id", "value")
        elif dictionary_name == "ProductType":
            refs["product_type"] = refs.get("product_type") or pick_value(
                items, "id", "code", "value"
            )
        elif dictionary_name == "ProductGroup":
            refs["product_group"] = refs.get("product_group") or pick_value(
                items, "id", "code", "value"
            )
        elif dictionary_name == "Country":
            refs["country"] = refs.get("country") or pick_value(items, "code", "id", "value")
        elif dictionary_name == "Region":
            refs["region"] = refs.get("region") or pick_value(items, "code", "id", "value")
        elif dictionary_name == "Office":
            refs["office_id"] = refs.get("office_id") or pick_value(items, "id", "code", "value")


def limit_item_example(state: dict[str, Any]) -> str:
    product_type = reference_value(state, "product_type") or "1-276PF01"
    card_id = first_card_id(state) or "56745380"
    return json.dumps(
        [
            {
                "card_id": card_id,
                "productType": product_type,
                "amount": {"unit": "LIT", "value": 10},
                "time": {"type": 3, "number": 1},
            }
        ],
        ensure_ascii=False,
    )


def region_limit_item_example(state: dict[str, Any]) -> str:
    card_id = first_card_id(state) or "56745380"
    country = reference_value(state, "country") or "RUS"
    region = reference_value(state, "region")
    payload = {"card_id": card_id, "country": country, "limit_type": 1}
    if region:
        payload["region"] = region
    return json.dumps([payload], ensure_ascii=False)


def restriction_item_example(state: dict[str, Any]) -> str:
    product_type = reference_value(state, "product_type") or "1-276PF01"
    card_id = first_card_id(state) or "56745380"
    return json.dumps(
        [{"card_id": card_id, "productType": product_type, "restriction_type": 2}],
        ensure_ascii=False,
    )


# Метод auth_user.
# Авторизует пользователя, получает session_id и список доступных договоров.
# Выводит полный envelope авторизации и сохраняет выбранный contract_id для следующих методов.
async def check_auth_user(client: APIClient, state: dict[str, Any]) -> None:
    try:
        result = await client.auth.auth_user()
    except ContractSelectionError as error:
        print("Доступно несколько договоров:")
        for item_contract_id, item_number in error.available_contracts:
            print(f"- ID: {item_contract_id} | Номер: {item_number}")
        selected = ask_value("Введите ID договора", default=saved(CURRENT_STATE, "contract_id"))
        result = await client.auth.auth_user(contract_id=selected)
    state["auth"] = result
    state["contract_id"] = client.contract_id
    print_result("auth_user", result)


# Метод attach_card.
# Прикрепляет карту к пользователю.
# Передаёт user_id и card_id, выводит bool-envelope результата.
async def check_attach_card(client: APIClient, state: dict[str, Any]) -> None:
    user_id = ask_value("user_id", default=first_user_id(state))
    card_id = ask_value("card_id", default=first_card_id(state))
    payload = {"user_id": user_id, "card_id": card_id}
    result = await run_mutation(
        "attach_card",
        "Прикрепить карту к пользователю.",
        payload,
        lambda: client.users.attach_card(user_id=user_id, card_id=card_id),
    )
    print_result("attach_card", result)


# Метод attach_contracts.
# Прикрепляет договоры к пользователю.
# Передаёт user_id и JSON-список contracts, выводит bool-envelope результата.
async def check_attach_contracts(client: APIClient, state: dict[str, Any]) -> None:
    user_id = ask_value("user_id", default=first_user_id(state))
    contracts = ask_json("contracts JSON list")
    payload = {"user_id": user_id, "contracts": contracts}
    result = await run_mutation(
        "attach_contracts",
        "Прикрепить один или несколько договоров к пользователю.",
        payload,
        lambda: client.users.attach_contracts(user_id=user_id, contracts=contracts),
    )
    print_result("attach_contracts", result)


# Метод block_card.
# Блокирует или разблокирует карты.
# Передаёт список card_ids и флаг block, выводит envelope со списком ID.
async def check_block_card(client: APIClient, state: dict[str, Any]) -> None:
    card_ids = ask_csv("card_ids через запятую", required=True)
    block = ask_bool("block=True заблокировать, block=False разблокировать", default=True)
    payload = {"contract_id": contract_id(state), "card_ids": card_ids, "block": block}
    result = await run_mutation(
        "block_card",
        "Изменить статус блокировки карт.",
        payload,
        lambda: client.cards.block_card(
            contract_id=contract_id(state),
            card_ids=card_ids,
            block=block,
        ),
    )
    print_result("block_card", result)


# Метод check_purchase.
# Проверяет возможность покупки по карте в точке продаж.
# Передаёт card_id, poi_id и goods JSON, выводит envelope проверки покупки.
async def check_check_purchase(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("Goods",), need_azs=True)
    card_id = ask_value("card_id", default=first_card_id(state))
    poi_id = ask_value("poi_id", default=reference_value(state, "poi_id"))
    goods_code = reference_value(state, "goods_code") or "1-276PF01"
    goods_price = float(reference_value(state, "goods_price") or "55.50")
    goods = ask_json(
        "goods JSON list",
        example=json.dumps(
            [{"code": goods_code, "quantity": 1, "price": goods_price}],
            ensure_ascii=False,
        ),
    )
    payload = {"card_id": card_id, "poi_id": poi_id, "goods": goods}
    result = await run_read(
        "check_purchase",
        "Проверить возможность покупки по карте.",
        payload,
        client.final_prices.check_purchase(card_id=card_id, poi_id=poi_id, goods=goods),
    )
    print_result("check_purchase", result)


# Метод confirm_mpc.
# Подтверждает MPC/QR-операцию по карте.
# Передаёт card_id и SMS-код, выводит результат подтверждения.
async def check_confirm_mpc(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    code = ask_value("SMS code")
    payload = {"card_id": card_id, "code": code}
    result = await run_mutation(
        "confirm_mpc",
        "Подтвердить MPC/QR-операцию.",
        payload,
        lambda: client.virtual_cards.confirm_mpc(card_id=card_id, code=code),
    )
    print_result("confirm_mpc", result)


# Метод create_invite.
# Создаёт приглашение пользователя.
# Передаёт invite JSON и with_send, выводит envelope созданного приглашения.
async def check_create_invite(client: APIClient, _state: dict[str, Any]) -> None:
    data = ask_json("invite data JSON object")
    with_send = ask_bool("with_send", default=True)
    payload = {"data": data, "with_send": with_send}
    result = await run_mutation(
        "create_invite",
        "Создать приглашение пользователя.",
        payload,
        lambda: client.invites.create_invite(data=data, with_send=with_send),
    )
    print_result("create_invite", result)


# Метод create_template.
# Создаёт шаблон виртуальной карты.
# Передаёт type_ и name, выводит envelope с ID шаблона.
async def check_create_template(client: APIClient, state: dict[str, Any]) -> None:
    type_ = ask_value("type_ (Limit или Wallet)")
    name = ask_value("name")
    payload = {"contract_id": contract_id(state), "type_": type_, "name": name}
    result = await run_mutation(
        "create_template",
        "Создать шаблон виртуальной карты.",
        payload,
        lambda: client.templates.create_template(
            contract_id=contract_id(state),
            type_=type_,
            name=name,
        ),
    )
    print_result("create_template", result)


# Метод create_template_georestriction.
# Создаёт геоограничение в шаблоне.
# Передаёт template_id и payload JSON, выводит envelope с ID геоограничения.
async def check_create_template_georestriction(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("Country", "Region"), need_azs=True)
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    country = reference_value(state, "country") or "RUS"
    region = reference_value(state, "region") or "54"
    payload_data = ask_json(
        "TemplateGeoRestrictionCreateRequest JSON object",
        example=json.dumps(
            {"country": country, "region": region, "restriction_type": 1},
            ensure_ascii=False,
        ),
    )
    payload = {"template_id": template_id, "payload": payload_data}
    result = await run_mutation(
        "create_template_georestriction",
        "Создать геоограничение шаблона.",
        payload,
        lambda: client.templates.create_template_georestriction(
            template_id=template_id,
            payload=payload_data,
            contract_id=contract_id(state),
        ),
    )
    print_result("create_template_georestriction", result)


# Метод create_template_limit.
# Создаёт лимит в шаблоне.
# Передаёт template_id и payload JSON, выводит envelope с ID лимита.
async def check_create_template_limit(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("ProductType", "Goods"))
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    product_type = (
        reference_value(state, "product_type")
        or reference_value(state, "goods_code")
        or "1-276PF01"
    )
    payload_data = ask_json(
        "TemplateLimitCreateRequest JSON object",
        example=json.dumps(
            {
                "product_type": product_type,
                "amount": {"unit": "LIT", "value": 10},
                "time": {"type": 3, "number": 1},
            },
            ensure_ascii=False,
        ),
    )
    payload = {"template_id": template_id, "payload": payload_data}
    result = await run_mutation(
        "create_template_limit",
        "Создать лимит шаблона.",
        payload,
        lambda: client.templates.create_template_limit(
            template_id=template_id,
            payload=payload_data,
            contract_id=contract_id(state),
        ),
    )
    print_result("create_template_limit", result)


# Метод create_template_restriction.
# Создаёт товарное ограничение в шаблоне.
# Передаёт template_id и payload JSON, выводит envelope с ID ограничения.
async def check_create_template_restriction(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("ProductType", "Goods"))
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    product_type = (
        reference_value(state, "product_type")
        or reference_value(state, "goods_code")
        or "1-276PF01"
    )
    payload_data = ask_json(
        "TemplateRestrictionCreateRequest JSON object",
        example=json.dumps(
            {"product_type": product_type, "restriction_type": 2},
            ensure_ascii=False,
        ),
    )
    payload = {"template_id": template_id, "payload": payload_data}
    result = await run_mutation(
        "create_template_restriction",
        "Создать товарное ограничение шаблона.",
        payload,
        lambda: client.templates.create_template_restriction(
            template_id=template_id,
            payload=payload_data,
            contract_id=contract_id(state),
        ),
    )
    print_result("create_template_restriction", result)


# Метод create_user.
# Создаёт пользователя.
# Передаёт uuid и mobile, выводит envelope с ID/результатом создания.
async def check_create_user(client: APIClient, _state: dict[str, Any]) -> None:
    uuid = ask_value("uuid")
    mobile = ask_value("mobile")
    payload = {"uuid": uuid, "mobile": mobile}
    result = await run_mutation(
        "create_user",
        "Создать пользователя.",
        payload,
        lambda: client.users.create_user(uuid=uuid, mobile=mobile),
    )
    print_result("create_user", result)


# Метод create_virtual_card.
# Выпускает виртуальную карту для пользователя.
# Передаёт user_id, выводит envelope созданной виртуальной карты.
async def check_create_virtual_card(client: APIClient, state: dict[str, Any]) -> None:
    user_id = ask_value("user_id", default=first_user_id(state))
    payload = {"user_id": user_id}
    result = await run_mutation(
        "create_virtual_card",
        "Выпустить виртуальную карту.",
        payload,
        lambda: client.virtual_cards.create_virtual_card(user_id=user_id),
    )
    print_result("create_virtual_card", result)


# Метод delete_invite.
# Удаляет приглашение.
# Передаёт invite_id, выводит bool-envelope результата.
async def check_delete_invite(client: APIClient, _state: dict[str, Any]) -> None:
    invite_id = ask_value("invite_id", default=saved(CURRENT_STATE, "invite_id"))
    use_post = ask_bool("use_post method override", default=False)
    payload = {"invite_id": invite_id, "use_post": use_post}
    result = await run_mutation(
        "delete_invite",
        "Удалить приглашение.",
        payload,
        lambda: client.invites.delete_invite(invite_id=invite_id, use_post=use_post),
    )
    print_result("delete_invite", result)


# Метод delete_mpc.
# Удаляет MPC/QR-привязку карты.
# Передаёт card_id, выводит envelope результата.
async def check_delete_mpc(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    payload = {"card_id": card_id}
    result = await run_mutation(
        "delete_mpc",
        "Удалить MPC/QR-привязку карты.",
        payload,
        lambda: client.virtual_cards.delete_mpc(card_id),
    )
    print_result("delete_mpc", result)


# Метод delete_template.
# Удаляет шаблон виртуальной карты.
# Передаёт template_id, выводит bool-envelope результата.
async def check_delete_template(client: APIClient, _state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    use_post = ask_bool("use_post method override", default=False)
    payload = {"template_id": template_id, "use_post": use_post}
    result = await run_mutation(
        "delete_template",
        "Удалить шаблон виртуальной карты.",
        payload,
        lambda: client.templates.delete_template(template_id=template_id, use_post=use_post),
    )
    print_result("delete_template", result)


# Метод delete_template_georestriction.
# Удаляет геоограничение шаблона.
# Передаёт template_id и georestriction_id, выводит bool-envelope результата.
async def check_delete_template_georestriction(client: APIClient, _state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    georestriction_id = ask_value(
        "georestriction_id", default=saved(CURRENT_STATE, "georestriction_id")
    )
    use_post = ask_bool("use_post method override", default=False)
    payload = {
        "template_id": template_id,
        "georestriction_id": georestriction_id,
        "use_post": use_post,
    }
    result = await run_mutation(
        "delete_template_georestriction",
        "Удалить геоограничение шаблона.",
        payload,
        lambda: client.templates.delete_template_georestriction(
            template_id=template_id,
            georestriction_id=georestriction_id,
            use_post=use_post,
        ),
    )
    print_result("delete_template_georestriction", result)


# Метод delete_template_limit.
# Удаляет лимит шаблона.
# Передаёт template_id и limit_id, выводит bool-envelope результата.
async def check_delete_template_limit(client: APIClient, _state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    limit_id = ask_value("limit_id", default=saved(CURRENT_STATE, "limit_id"))
    use_post = ask_bool("use_post method override", default=False)
    payload = {"template_id": template_id, "limit_id": limit_id, "use_post": use_post}
    result = await run_mutation(
        "delete_template_limit",
        "Удалить лимит шаблона.",
        payload,
        lambda: client.templates.delete_template_limit(
            template_id=template_id,
            limit_id=limit_id,
            use_post=use_post,
        ),
    )
    print_result("delete_template_limit", result)


# Метод delete_template_restriction.
# Удаляет товарное ограничение шаблона.
# Передаёт template_id и restriction_id, выводит bool-envelope результата.
async def check_delete_template_restriction(client: APIClient, _state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    restriction_id = ask_value("restriction_id", default=saved(CURRENT_STATE, "restriction_id"))
    use_post = ask_bool("use_post method override", default=False)
    payload = {"template_id": template_id, "restriction_id": restriction_id, "use_post": use_post}
    result = await run_mutation(
        "delete_template_restriction",
        "Удалить товарное ограничение шаблона.",
        payload,
        lambda: client.templates.delete_template_restriction(
            template_id=template_id,
            restriction_id=restriction_id,
            use_post=use_post,
        ),
    )
    print_result("delete_template_restriction", result)


# Метод delete_user.
# Удаляет пользователя.
# Передаёт user_id, выводит bool-envelope результата.
async def check_delete_user(client: APIClient, state: dict[str, Any]) -> None:
    user_id = ask_value("user_id", default=first_user_id(state))
    use_post = ask_bool("use_post method override", default=False)
    payload = {"user_id": user_id, "use_post": use_post}
    result = await run_mutation(
        "delete_user",
        "Удалить пользователя.",
        payload,
        lambda: client.users.delete_user(user_id=user_id, use_post=use_post),
    )
    print_result("delete_user", result)


# Метод detach_card.
# Открепляет карту от пользователя.
# Передаёт user_id и card_id, выводит bool-envelope результата.
async def check_detach_card(client: APIClient, state: dict[str, Any]) -> None:
    user_id = ask_value("user_id", default=first_user_id(state))
    card_id = ask_value("card_id", default=first_card_id(state))
    payload = {"user_id": user_id, "card_id": card_id}
    result = await run_mutation(
        "detach_card",
        "Открепить карту от пользователя.",
        payload,
        lambda: client.users.detach_card(user_id=user_id, card_id=card_id),
    )
    print_result("detach_card", result)


# Метод detach_contracts.
# Открепляет договоры от пользователя.
# Передаёт user_id и список contracts, выводит bool-envelope результата.
async def check_detach_contracts(client: APIClient, state: dict[str, Any]) -> None:
    user_id = ask_value("user_id", default=first_user_id(state))
    contracts = ask_csv("contract IDs через запятую", required=True)
    payload = {"user_id": user_id, "contracts": contracts}
    result = await run_mutation(
        "detach_contracts",
        "Открепить договоры от пользователя.",
        payload,
        lambda: client.users.detach_contracts(user_id=user_id, contracts=contracts),
    )
    print_result("detach_contracts", result)


# Метод download_report_file.
# Скачивает файл отчёта v2.
# Передаёт job_id, выводит размер bytes-ответа.
async def check_download_report_file(client: APIClient, _state: dict[str, Any]) -> None:
    job_id = ask_value("job_id", default=saved(CURRENT_STATE, "job_id"))
    payload = {"job_id": job_id}
    result = await run_read(
        "download_report_file",
        "Скачать файл отчёта v2.",
        payload,
        client.reports.download_report_file(job_id=job_id),
    )
    print_result("download_report_file", result)


# Метод download_report_file_v1.
# Скачивает файл отчёта v1.
# Передаёт job_id и archive, выводит размер bytes-ответа.
async def check_download_report_file_v1(client: APIClient, _state: dict[str, Any]) -> None:
    job_id = ask_value("job_id", default=saved(CURRENT_STATE, "job_id"))
    archive = ask_bool("archive", default=False)
    payload = {"job_id": job_id, "archive": archive}
    result = await run_read(
        "download_report_file_v1",
        "Скачать файл отчёта v1.",
        payload,
        client.reports.download_report_file_v1(job_id=job_id, archive=archive),
    )
    print_result("download_report_file_v1", result)


# Метод generate_payment_qr.
# Генерирует платёжный QR/MPC payload.
# Передаёт card_id и PIN МПК, выводит платёжную BER-TLV строку.
async def check_generate_payment_qr(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    pin = ask_value("MPC PIN")
    payload = {"card_id": card_id, "pin": "<redacted>"}
    result = await run_mutation(
        "generate_payment_qr",
        "Сгенерировать платёжный QR/MPC payload.",
        payload,
        lambda: client.virtual_cards.generate_payment_qr(card_id=card_id, pin=pin),
    )
    print_result("generate_payment_qr", result)


# Метод get_azs_filters.
# Получает фильтры АЗС.
# Передаёт только session/api context, выводит справочник фильтров.
async def check_get_azs_filters(client: APIClient, _state: dict[str, Any]) -> None:
    payload: dict[str, Any] = {}
    result = await run_read(
        "get_azs_filters",
        "Получить фильтры АЗС.",
        payload,
        client.dictionaries.get_azs_filters(),
    )
    print_result("get_azs_filters", result)


# Метод get_azs_list_v1.
# Получает список АЗС v1.
# Передаёт пагинацию и опциональный filter/id, выводит список АЗС.
async def check_get_azs_list_v1(client: APIClient, _state: dict[str, Any]) -> None:
    page = int(ask_value("page", default="1") or "1")
    onpage = int(ask_value("onpage", default="10") or "10")
    filter_data = ask_value("filter JSON object, Enter чтобы пропустить", required=False)
    azs_id = ask_value("id, Enter чтобы пропустить", required=False)
    filter_obj = json.loads(filter_data) if filter_data else None
    payload = {"page": page, "onpage": onpage, "filter": filter_obj, "id": azs_id}
    result = await run_read(
        "get_azs_list_v1",
        "Получить список АЗС v1.",
        payload,
        client.dictionaries.get_azs_list_v1(
            page=page,
            onpage=onpage,
            filter=filter_obj,
            id=azs_id,
        ),
    )
    print_result("get_azs_list_v1", result)


# Метод get_azs_list_v2.
# Получает список АЗС v2.
# Передаёт filter/q, выводит список АЗС.
async def check_get_azs_list_v2(client: APIClient, _state: dict[str, Any]) -> None:
    filter_data = ask_value("filter JSON object, Enter чтобы пропустить", required=False)
    q = ask_value("q, Enter чтобы пропустить", required=False)
    filter_obj = json.loads(filter_data) if filter_data else None
    payload = {"filter": filter_obj, "q": q}
    result = await run_read(
        "get_azs_list_v2",
        "Получить список АЗС v2.",
        payload,
        client.dictionaries.get_azs_list_v2(filter=filter_obj, q=q),
    )
    print_result("get_azs_list_v2", result)


# Метод get_card_detail.
# Получает детальную информацию по карте.
# Передаёт card_id и contract_id, выводит card detail envelope.
async def check_get_card_detail(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    payload = {"contract_id": contract_id(state), "card_id": card_id}
    result = await run_read(
        "get_card_detail",
        "Получить детальную информацию по карте.",
        payload,
        client.cards.get_card_detail(contract_id=contract_id(state), card_id=card_id),
    )
    print_result("get_card_detail", result)


# Метод get_card_drivers.
# Получает водителей карты.
# Передаёт card_id и contract_id, выводит список водителей.
async def check_get_card_drivers(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    payload = {"contract_id": contract_id(state), "card_id": card_id}
    result = await run_read(
        "get_card_drivers",
        "Получить список водителей карты.",
        payload,
        client.cards.get_card_drivers(contract_id=contract_id(state), card_id=card_id),
    )
    print_result("get_card_drivers", result)


# Метод get_card_groups.
# Получает группы карт договора.
# Передаёт contract_id, выводит список групп карт.
async def check_get_card_groups(client: APIClient, state: dict[str, Any]) -> None:
    payload = {"contract_id": contract_id(state)}
    result = await run_read(
        "get_card_groups",
        "Получить группы карт договора.",
        payload,
        client.card_groups.get_card_groups(contract_id=contract_id(state)),
    )
    print_result("get_card_groups", result)


# Метод get_card_transactions_v2.
# Получает транзакции конкретной карты.
# Передаёт card_id, contract_id, период и пагинацию, выводит страницу транзакций.
async def check_get_card_transactions_v2(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    date_from = ask_value("date_from YYYY-MM-DD")
    date_to = ask_value("date_to YYYY-MM-DD")
    page_limit = int(ask_value("page_limit", default="100") or "100")
    page_offset = int(ask_value("page_offset", default="0") or "0")
    payload = {
        "card_id": card_id,
        "contract_id": contract_id(state),
        "date_from": date_from,
        "date_to": date_to,
        "page_limit": page_limit,
        "page_offset": page_offset,
    }
    result = await run_read(
        "get_card_transactions_v2",
        "Получить транзакции карты v2.",
        payload,
        client.transactions.get_card_transactions_v2(**payload),
    )
    print_result("get_card_transactions_v2", result)


# Метод get_cards_by_group.
# Получает карты группы.
# Передаёт group_id и contract_id, выводит список карт группы.
async def check_get_cards_by_group(client: APIClient, state: dict[str, Any]) -> None:
    group_id = ask_value("group_id", default=saved(CURRENT_STATE, "group_id"))
    payload = {"contract_id": contract_id(state), "group_id": group_id}
    result = await run_read(
        "get_cards_by_group",
        "Получить карты группы.",
        payload,
        client.cards.get_cards_by_group(contract_id=contract_id(state), group_id=group_id),
    )
    print_result("get_cards_by_group", result)


# Метод get_cards_v1.
# Получает список карт v1.
# Передаёт contract_id и cache, выводит список карт.
async def check_get_cards_v1(client: APIClient, state: dict[str, Any]) -> None:
    cache = ask_bool("cache", default=True)
    payload = {"contract_id": contract_id(state), "cache": cache}
    result = await run_read(
        "get_cards_v1",
        "Получить список карт v1.",
        payload,
        client.cards.get_cards_v1(contract_id=contract_id(state), cache=cache),
    )
    print_result("get_cards_v1", result)


# Метод get_cards_v2.
# Получает список карт v2.
# Передаёт contract_id, фильтры и пагинацию, выводит страницу карт.
async def check_get_cards_v2(client: APIClient, state: dict[str, Any]) -> None:
    page = int(ask_value("page", default="1") or "1")
    onpage = int(ask_value("onpage", default="5") or "5")
    payload = {"contract_id": contract_id(state), "page": page, "onpage": onpage}
    result = await run_read(
        "get_cards_v2",
        "Получить список карт v2.",
        payload,
        client.cards.get_cards_v2(contract_id=contract_id(state), page=page, onpage=onpage),
    )
    if getattr(result.data, "result", None):
        state["card_id"] = result.data.result[0].id
    print_result("get_cards_v2", result)


# Метод get_contract_data.
# Получает данные договора.
# Передаёт contract_id, выводит баланс, параметры договора, менеджера и статистику карт.
async def check_get_contract_data(client: APIClient, state: dict[str, Any]) -> None:
    payload = {"contract_id": contract_id(state)}
    result = await run_read(
        "get_contract_data",
        "Получить данные договора.",
        payload,
        client.contracts.get_contract_data(contract_id=contract_id(state)),
    )
    print_result("get_contract_data", result)


# Метод get_dictionary.
# Получает справочник по имени.
# Передаёт name, выводит данные справочника.
async def check_get_dictionary(client: APIClient, _state: dict[str, Any]) -> None:
    name = ask_value(
        "dictionary name",
        default=random.choice(REFERENCE_DICTIONARIES),
        example=", ".join(REFERENCE_DICTIONARIES),
    )
    payload = {"name": name}
    result = await run_read(
        "get_dictionary",
        "Получить справочник по имени.",
        payload,
        client.dictionaries.get_dictionary(name=name),
    )
    print_result("get_dictionary", result)


# Метод get_documents.
# Получает список документов договора.
# Передаёт contract_id, date_start, date_end и пагинацию, выводит список документов.
async def check_get_documents(client: APIClient, state: dict[str, Any]) -> None:
    date_start = ask_value("date_start YYYY-MM-DD")
    date_end = ask_value("date_end YYYY-MM-DD")
    page = int(ask_value("page", default="1") or "1")
    on_page = int(ask_value("on_page", default="10") or "10")
    payload = {
        "contract_id": contract_id(state),
        "date_start": date_start,
        "date_end": date_end,
        "page": page,
        "on_page": on_page,
    }
    result = await run_read(
        "get_documents",
        "Получить документы договора.",
        payload,
        client.contracts.get_documents(**payload),
    )
    print_result("get_documents", result)


# Метод get_final_prices.
# Рассчитывает финальные цены для карты и точки продаж.
# Передаёт card_id, poi_id и список goods, выводит envelope цен.
async def check_get_final_prices(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("Goods",), need_azs=True)
    card_id = ask_value("card_id", default=first_card_id(state))
    poi_id = ask_value("poi_id", default=reference_value(state, "poi_id"))
    goods = ask_csv(
        "goods codes через запятую",
        example=reference_value(state, "goods_code") or "1-276PF01",
    )
    payload = {"card_id": card_id, "poi_id": poi_id, "goods": goods}
    result = await run_read(
        "get_final_prices",
        "Рассчитать финальные цены.",
        payload,
        client.final_prices.get_final_prices(card_id=card_id, poi_id=poi_id, goods=goods),
    )
    print_result("get_final_prices", result)


# Метод get_info.
# Получает информацию о клиенте и тарифных запросах.
# Передаёт period при необходимости, выводит envelope client_info.
async def check_get_info(client: APIClient, _state: dict[str, Any]) -> None:
    current_period = date.today().strftime("%Y-%m")
    period = ask_value("period", default=current_period, required=False)
    payload = {"period": period}
    result = await run_read(
        "get_info",
        "Получить информацию о клиенте и тарифе.",
        payload,
        client.auth.get_info(period=period),
    )
    print_result("get_info", result)
    print_tariff_usage_summary(result)


# Метод get_invites.
# Получает список приглашений.
# Передаёт фильтры и пагинацию, выводит страницу приглашений.
async def check_get_invites(client: APIClient, _state: dict[str, Any]) -> None:
    page = ask_value("page, Enter чтобы пропустить", required=False)
    on_page = ask_value("on_page, Enter чтобы пропустить", required=False)
    payload = {
        "role": ask_value("role, Enter чтобы пропустить", required=False),
        "user_id": ask_value("user_id, Enter чтобы пропустить", required=False),
        "sort": ask_value("sort, Enter чтобы пропустить", required=False),
        "status": ask_value("status, Enter чтобы пропустить", required=False),
        "q": ask_value("q, Enter чтобы пропустить", required=False),
        "page": int(page) if page else None,
        "on_page": int(on_page) if on_page else None,
    }
    result = await run_read(
        "get_invites",
        "Получить список приглашений.",
        payload,
        client.invites.get_invites(**payload),
    )
    print_result("get_invites", result)


# Метод get_invoices.
# Получает счета договора.
# Передаёт contract_id, выводит список счетов.
async def check_get_invoices(client: APIClient, state: dict[str, Any]) -> None:
    payload = {"contract_id": contract_id(state)}
    result = await run_read(
        "get_invoices",
        "Получить счета договора.",
        payload,
        client.contracts.get_invoices(contract_id=contract_id(state)),
    )
    print_result("get_invoices", result)


# Метод get_limits.
# Получает продуктовые лимиты договора, карты или группы.
# Передаёт contract_id и опциональный card_id/group_id, выводит список лимитов.
async def check_get_limits(client: APIClient, state: dict[str, Any]) -> None:
    target = ask_target()
    payload = {"contract_id": contract_id(state), **target}
    result = await run_read(
        "get_limits",
        "Получить продуктовые лимиты.",
        payload,
        client.limits.get_limits(contract_id=contract_id(state), **target),
    )
    print_result("get_limits", result)


# Метод get_mpc_qr_list.
# Получает список MPC/QR.
# Передаёт только session/api context, выводит список MPC.
async def check_get_mpc_qr_list(client: APIClient, _state: dict[str, Any]) -> None:
    payload: dict[str, Any] = {}
    result = await run_read(
        "get_mpc_qr_list",
        "Получить список MPC/QR.",
        payload,
        client.virtual_cards.get_mpc_qr_list(),
    )
    print_result("get_mpc_qr_list", result)


# Метод get_payments.
# Получает платежи договора.
# Передаёт contract_id, выводит список платежей.
async def check_get_payments(client: APIClient, state: dict[str, Any]) -> None:
    payload = {"contract_id": contract_id(state)}
    result = await run_read(
        "get_payments",
        "Получить платежи договора.",
        payload,
        client.contracts.get_payments(contract_id=contract_id(state)),
    )
    print_result("get_payments", result)


# Метод get_region_limits.
# Получает региональные лимиты договора, карты или группы.
# Передаёт contract_id и опциональный card_id/group_id, выводит список региональных лимитов.
async def check_get_region_limits(client: APIClient, state: dict[str, Any]) -> None:
    target = ask_target()
    payload = {"contract_id": contract_id(state), **target}
    result = await run_read(
        "get_region_limits",
        "Получить региональные лимиты.",
        payload,
        client.region_limits.get_region_limits(contract_id=contract_id(state), **target),
    )
    print_result("get_region_limits", result)


# Метод get_report_job_list_v1.
# Получает список задач отчётов v1.
# Передаёт только session/api context, выводит список задач.
async def check_get_report_job_list_v1(client: APIClient, _state: dict[str, Any]) -> None:
    payload: dict[str, Any] = {}
    result = await run_read(
        "get_report_job_list_v1",
        "Получить список задач отчётов v1.",
        payload,
        client.reports.get_report_job_list_v1(),
    )
    print_result("get_report_job_list_v1", result)


# Метод get_report_jobs.
# Получает список задач отчётов v2.
# Передаёт только session/api context, выводит список задач.
async def check_get_report_jobs(client: APIClient, _state: dict[str, Any]) -> None:
    payload: dict[str, Any] = {}
    result = await run_read(
        "get_report_jobs",
        "Получить список задач отчётов v2.",
        payload,
        client.reports.get_report_jobs(),
    )
    print_result("get_report_jobs", result)


# Метод get_reports.
# Получает список доступных отчётов v2.
# Передаёт только session/api context, выводит список отчётов.
async def check_get_reports(client: APIClient, _state: dict[str, Any]) -> None:
    payload: dict[str, Any] = {}
    result = await run_read(
        "get_reports", "Получить список доступных отчётов.", payload, client.reports.get_reports()
    )
    print_result("get_reports", result)


# Метод get_restrictions.
# Получает товарные ограничители договора, карты или группы.
# Передаёт contract_id и опциональный card_id/group_id, выводит список ограничителей.
async def check_get_restrictions(client: APIClient, state: dict[str, Any]) -> None:
    target = ask_target()
    payload = {"contract_id": contract_id(state), **target}
    result = await run_read(
        "get_restrictions",
        "Получить товарные ограничители.",
        payload,
        client.restrictions.get_restrictions(contract_id=contract_id(state), **target),
    )
    print_result("get_restrictions", result)


# Метод get_template_georestrictions.
# Получает геоограничения шаблона.
# Передаёт template_id, выводит список геоограничений.
async def check_get_template_georestrictions(client: APIClient, _state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    payload = {"template_id": template_id}
    result = await run_read(
        "get_template_georestrictions",
        "Получить геоограничения шаблона.",
        payload,
        client.templates.get_template_georestrictions(template_id=template_id),
    )
    print_result("get_template_georestrictions", result)


# Метод get_template_limits.
# Получает лимиты шаблона.
# Передаёт template_id, выводит список лимитов.
async def check_get_template_limits(client: APIClient, _state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    payload = {"template_id": template_id}
    result = await run_read(
        "get_template_limits",
        "Получить лимиты шаблона.",
        payload,
        client.templates.get_template_limits(template_id=template_id),
    )
    print_result("get_template_limits", result)


# Метод get_template_restrictions.
# Получает товарные ограничения шаблона.
# Передаёт template_id, выводит список ограничений.
async def check_get_template_restrictions(client: APIClient, _state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    payload = {"template_id": template_id}
    result = await run_read(
        "get_template_restrictions",
        "Получить товарные ограничения шаблона.",
        payload,
        client.templates.get_template_restrictions(template_id=template_id),
    )
    print_result("get_template_restrictions", result)


# Метод get_templates.
# Получает шаблоны виртуальных карт договора.
# Передаёт contract_id, выводит список шаблонов.
async def check_get_templates(client: APIClient, state: dict[str, Any]) -> None:
    payload = {"contract_id": contract_id(state)}
    result = await run_read(
        "get_templates",
        "Получить шаблоны виртуальных карт.",
        payload,
        client.templates.get_templates(contract_id=contract_id(state)),
    )
    print_result("get_templates", result)


# Метод get_transaction_detail.
# Получает детальную информацию по транзакции.
# Передаёт transaction_id и contract_id, выводит detail envelope.
async def check_get_transaction_detail(client: APIClient, state: dict[str, Any]) -> None:
    transaction_id = ask_value("transaction_id", default=saved(CURRENT_STATE, "transaction_id"))
    payload = {"contract_id": contract_id(state), "transaction_id": transaction_id}
    result = await run_read(
        "get_transaction_detail",
        "Получить детали транзакции.",
        payload,
        client.transactions.get_transaction_detail(
            contract_id=contract_id(state),
            transaction_id=transaction_id,
        ),
    )
    print_result("get_transaction_detail", result)


# Метод get_transactions_v1.
# Получает последние транзакции v1.
# Передаёт contract_id, count и опциональный card_id, выводит список транзакций.
async def check_get_transactions_v1(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value(
        "card_id, Enter чтобы пропустить", default=first_card_id(state), required=False
    )
    count = int(ask_value("count", default="20") or "20")
    payload = {"contract_id": contract_id(state), "card_id": card_id, "count": count}
    result = await run_read(
        "get_transactions_v1",
        "Получить транзакции v1.",
        payload,
        client.transactions.get_transactions_v1(
            contract_id=contract_id(state),
            card_id=card_id,
            count=count,
        ),
    )
    print_result("get_transactions_v1", result)


# Метод get_transactions_v2.
# Получает транзакции договора v2.
# Передаёт contract_id, период и пагинацию, выводит страницу транзакций.
async def check_get_transactions_v2(client: APIClient, state: dict[str, Any]) -> None:
    date_from = ask_value("date_from YYYY-MM-DD")
    date_to = ask_value("date_to YYYY-MM-DD")
    page_limit = int(ask_value("page_limit", default="100") or "100")
    page_offset = int(ask_value("page_offset", default="0") or "0")
    payload = {
        "contract_id": contract_id(state),
        "date_from": date_from,
        "date_to": date_to,
        "page_limit": page_limit,
        "page_offset": page_offset,
    }
    result = await run_read(
        "get_transactions_v2",
        "Получить транзакции договора v2.",
        payload,
        client.transactions.get_transactions_v2(**payload),
    )
    print_result("get_transactions_v2", result)


# Метод get_users.
# Получает список пользователей.
# Передаёт фильтры и пагинацию, выводит страницу пользователей.
async def check_get_users(client: APIClient, state: dict[str, Any]) -> None:
    page = ask_value("page, Enter чтобы пропустить", default="1", required=False)
    on_page = ask_value("on_page, Enter чтобы пропустить", default="5", required=False)
    filter_raw = ask_value("filter JSON object, Enter чтобы пропустить", required=False)
    payload = {
        "sort": ask_value("sort, Enter чтобы пропустить", required=False),
        "page": int(page) if page else None,
        "on_page": int(on_page) if on_page else None,
        "q": ask_value("q, Enter чтобы пропустить", required=False),
        "filter": json.loads(filter_raw) if filter_raw else None,
    }
    result = await run_read(
        "get_users", "Получить список пользователей.", payload, client.users.get_users(**payload)
    )
    if result.data and result.data.result:
        state["user_id"] = result.data.result[0].id
    print_result("get_users", result)


# Метод init_mpc.
# Инициализирует MPC/QR для карты.
# Передаёт карту, пользователя, PIN и данные устройства.
async def check_init_mpc(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    user_id = ask_value("user_id", default=saved(CURRENT_STATE, "user_id"))
    pin = ask_value("MPC PIN")
    device_id = ask_value("device_id")
    device_name = ask_value("device_name (11-17 chars)")
    payload = {
        "card_id": card_id,
        "user_id": user_id,
        "pin": "<redacted>",
        "device_id": device_id,
        "device_name": device_name,
    }
    result = await run_mutation(
        "init_mpc",
        "Инициализировать MPC/QR для карты.",
        payload,
        lambda: client.virtual_cards.init_mpc(
            card_id=card_id,
            user_id=user_id,
            pin=pin,
            device_id=device_id,
            device_name=device_name,
        ),
    )
    print_result("init_mpc", result)


# Метод logoff.
# Завершает серверную сессию.
# Передаёт session_id из клиента, выводит envelope выхода.
async def check_logoff(client: APIClient, state: dict[str, Any]) -> None:
    payload = {"session_id": "current session"}
    result = await run_read("logoff", "Завершить текущую сессию.", payload, client.auth.logoff())
    print_result("logoff", result)
    state["logged_off"] = True


# Метод move_to_card.
# Переводит средства на карту.
# Передаёт contract_id, card_id и amount, выводит envelope результата.
async def check_move_to_card(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    amount = ask_decimal("amount")
    payload = {"contract_id": contract_id(state), "card_id": card_id, "amount": amount}
    result = await run_mutation(
        "move_to_card",
        "Перевести средства на карту.",
        payload,
        lambda: client.ewallet.move_to_card(
            contract_id=contract_id(state),
            card_id=card_id,
            amount=amount,
        ),
    )
    print_result("move_to_card", result)


# Метод move_to_contract.
# Возвращает средства с карты на договор.
# Передаёт contract_id, card_id и amount, выводит envelope результата.
async def check_move_to_contract(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    amount = ask_decimal("amount")
    payload = {"contract_id": contract_id(state), "card_id": card_id, "amount": amount}
    result = await run_mutation(
        "move_to_contract",
        "Вернуть средства с карты на договор.",
        payload,
        lambda: client.ewallet.move_to_contract(
            contract_id=contract_id(state),
            card_id=card_id,
            amount=amount,
        ),
    )
    print_result("move_to_contract", result)


# Метод order_cards.
# Создаёт заявку на выпуск пластиковых карт.
# Передаёт contract_id, count и office_id, выводит envelope заявки.
async def check_order_cards(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("Office",))
    count = int(ask_value("count") or "0")
    office_id = ask_value("office_id", default=reference_value(state, "office_id"))
    payload = {"contract_id": contract_id(state), "count": count, "office_id": office_id}
    result = await run_mutation(
        "order_cards",
        "Создать заявку на выпуск карт.",
        payload,
        lambda: client.contracts.order_cards(
            contract_id=contract_id(state),
            count=count,
            office_id=office_id,
        ),
    )
    print_result("order_cards", result)


# Метод order_documents_email.
# Заказывает отправку документов на email.
# Передаёт ids, формат и emails, выводит envelope результата.
async def check_order_documents_email(client: APIClient, state: dict[str, Any]) -> None:
    ids = ask_csv("document ids через запятую")
    fmt = ask_value("fmt pdf/xlsx")
    emails = ask_csv("emails через запятую")
    payload = {"contract_id": contract_id(state), "ids": ids, "fmt": fmt, "emails": emails}
    result = await run_mutation(
        "order_documents_email",
        "Заказать отправку документов на email.",
        payload,
        lambda: client.contracts.order_documents_email(
            contract_id=contract_id(state),
            ids=ids,
            fmt=fmt,
            emails=emails,
        ),
    )
    print_result("order_documents_email", result)


# Метод order_invoice.
# Создаёт счёт на оплату.
# Передаёт contract_id, amount и email, выводит envelope заявки на счёт.
async def check_order_invoice(client: APIClient, state: dict[str, Any]) -> None:
    amount = ask_decimal("amount")
    email = ask_value("email")
    payload = {"contract_id": contract_id(state), "amount": amount, "email": email}
    result = await run_mutation(
        "order_invoice",
        "Создать счёт на оплату.",
        payload,
        lambda: client.contracts.order_invoice(
            contract_id=contract_id(state),
            amount=amount,
            email=email,
        ),
    )
    print_result("order_invoice", result)


# Метод order_report.
# Заказывает отчёт v2.
# Передаёт report_id, format, params и emails, выводит envelope задачи отчёта.
async def check_order_report(client: APIClient, _state: dict[str, Any]) -> None:
    report_id = ask_value("report_id")
    report_format = ask_value("format")
    params = ask_json("params JSON object")
    emails = ask_value("emails, Enter чтобы пропустить", required=False)
    payload = {"report_id": report_id, "format": report_format, "params": params, "emails": emails}
    result = await run_mutation(
        "order_report",
        "Заказать отчёт v2.",
        payload,
        lambda: client.reports.order_report(
            report_id=report_id,
            format=report_format,
            params=params,
            emails=emails,
        ),
    )
    print_result("order_report", result)


# Метод order_report_v1.
# Заказывает отчёт v1.
# Передаёт contract_id, период, формат и фильтры, выводит envelope задачи отчёта.
async def check_order_report_v1(client: APIClient, state: dict[str, Any]) -> None:
    start = ask_value("start YYYY-MM-DD")
    end = ask_value("end YYYY-MM-DD")
    report_format = ask_value("report_format")
    email = ask_value("email, Enter чтобы пропустить", required=False)
    cards_list = ask_csv("cards_list через запятую, Enter чтобы пропустить", required=False)
    group_id = ask_csv("group_id list через запятую, Enter чтобы пропустить", required=False)
    archive = ask_bool("archive", default=False)
    payload = {
        "contract_id": contract_id(state),
        "start": start,
        "end": end,
        "report_format": report_format,
        "email": email,
        "cards_list": cards_list or None,
        "group_id": group_id or None,
        "archive": archive,
    }
    result = await run_mutation(
        "order_report_v1",
        "Заказать отчёт v1.",
        payload,
        lambda: client.reports.order_report_v1(**payload),
    )
    print_result("order_report_v1", result)


# Метод prolong_invite.
# Продлевает приглашение.
# Передаёт invite_id и with_send, выводит bool-envelope результата.
async def check_prolong_invite(client: APIClient, _state: dict[str, Any]) -> None:
    invite_id = ask_value("invite_id", default=saved(CURRENT_STATE, "invite_id"))
    with_send = ask_bool("with_send", default=True)
    payload = {"invite_id": invite_id, "with_send": with_send}
    result = await run_mutation(
        "prolong_invite",
        "Продлить приглашение.",
        payload,
        lambda: client.invites.prolong_invite(invite_id=invite_id, with_send=with_send),
    )
    print_result("prolong_invite", result)


# Метод release_virtual_card.
# Выпускает виртуальную карту по типу/шаблону/пользователю.
# Передаёт type_, template_id и user_id, выводит envelope виртуальной карты.
async def check_release_virtual_card(client: APIClient, state: dict[str, Any]) -> None:
    type_ = ask_value("type_, Enter чтобы пропустить", required=False)
    template_id = None
    if type_ is None:
        template_id = ask_value(
            "template_id (обязателен, если type_ не указан)",
            default=saved(CURRENT_STATE, "template_id"),
            required=True,
        )
    user_id = ask_value(
        "user_id, Enter чтобы пропустить", default=first_user_id(state), required=False
    )
    payload = {"type_": type_, "template_id": template_id, "user_id": user_id}
    result = await run_mutation(
        "release_virtual_card",
        "Выпустить виртуальную карту.",
        payload,
        lambda: client.virtual_cards.release_virtual_card(**payload),
    )
    print_result("release_virtual_card", result)


# Метод remove_card_group.
# Удаляет группу карт.
# Передаёт group_id и contract_id, выводит envelope результата.
async def check_remove_card_group(client: APIClient, state: dict[str, Any]) -> None:
    group_id = ask_value("group_id", default=saved(CURRENT_STATE, "group_id"))
    payload = {"contract_id": contract_id(state), "group_id": group_id}
    result = await run_mutation(
        "remove_card_group",
        "Удалить группу карт.",
        payload,
        lambda: client.card_groups.remove_card_group(
            contract_id=contract_id(state),
            group_id=group_id,
        ),
    )
    print_result("remove_card_group", result)


# Метод remove_limit.
# Удаляет продуктовый лимит.
# Передаёт limit_id, contract_id и опциональный group_id, выводит bool-envelope результата.
async def check_remove_limit(client: APIClient, state: dict[str, Any]) -> None:
    limit_id = ask_value("limit_id", default=saved(CURRENT_STATE, "limit_id"))
    group_id = ask_value(
        "group_id, Enter чтобы пропустить",
        default=saved(CURRENT_STATE, "group_id"),
        required=False,
    )
    payload = {"contract_id": contract_id(state), "limit_id": limit_id, "group_id": group_id}
    result = await run_mutation(
        "remove_limit",
        "Удалить продуктовый лимит.",
        payload,
        lambda: client.limits.remove_limit(
            contract_id=contract_id(state),
            limit_id=limit_id,
            group_id=group_id,
        ),
    )
    print_result("remove_limit", result)


# Метод remove_region_limit.
# Удаляет региональный лимит.
# Передаёт regionlimit_id, contract_id и опциональный group_id, выводит bool-envelope результата.
async def check_remove_region_limit(client: APIClient, state: dict[str, Any]) -> None:
    regionlimit_id = ask_value("regionlimit_id", default=saved(CURRENT_STATE, "regionlimit_id"))
    group_id = ask_value(
        "group_id, Enter чтобы пропустить",
        default=saved(CURRENT_STATE, "group_id"),
        required=False,
    )
    payload = {
        "contract_id": contract_id(state),
        "regionlimit_id": regionlimit_id,
        "group_id": group_id,
    }
    result = await run_mutation(
        "remove_region_limit",
        "Удалить региональный лимит.",
        payload,
        lambda: client.region_limits.remove_region_limit(
            contract_id=contract_id(state),
            regionlimit_id=regionlimit_id,
            group_id=group_id,
        ),
    )
    print_result("remove_region_limit", result)


# Метод remove_restriction.
# Удаляет товарный ограничитель.
# Передаёт restriction_id, contract_id и опциональный group_id, выводит bool-envelope результата.
async def check_remove_restriction(client: APIClient, state: dict[str, Any]) -> None:
    restriction_id = ask_value("restriction_id", default=saved(CURRENT_STATE, "restriction_id"))
    group_id = ask_value(
        "group_id, Enter чтобы пропустить",
        default=saved(CURRENT_STATE, "group_id"),
        required=False,
    )
    payload = {
        "contract_id": contract_id(state),
        "restriction_id": restriction_id,
        "group_id": group_id,
    }
    result = await run_mutation(
        "remove_restriction",
        "Удалить товарный ограничитель.",
        payload,
        lambda: client.restrictions.remove_restriction(
            contract_id=contract_id(state),
            restriction_id=restriction_id,
            group_id=group_id,
        ),
    )
    print_result("remove_restriction", result)


# Метод resend_invite.
# Повторно отправляет приглашение.
# Передаёт invite_id, выводит envelope приглашения.
async def check_resend_invite(client: APIClient, _state: dict[str, Any]) -> None:
    invite_id = ask_value("invite_id", default=saved(CURRENT_STATE, "invite_id"))
    payload = {"invite_id": invite_id}
    result = await run_mutation(
        "resend_invite",
        "Повторно отправить приглашение.",
        payload,
        lambda: client.invites.resend_invite(invite_id=invite_id),
    )
    print_result("resend_invite", result)


# Метод reset_mpc.
# Сбрасывает MPC/QR состояние карты.
# Передаёт card_id и type_, выводит envelope результата.
async def check_reset_mpc(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    type_ = ask_value("type_")
    payload = {"card_id": card_id, "type_": type_}
    result = await run_mutation(
        "reset_mpc",
        "Сбросить MPC/QR состояние карты.",
        payload,
        lambda: client.virtual_cards.reset_mpc(card_id, type_),
    )
    print_result("reset_mpc", result)


# Метод reset_pin.
# Сбрасывает PIN карты.
# Передаёт card_id и code, выводит bool-envelope результата.
async def check_reset_pin(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    code = ask_value("code")
    payload = {"contract_id": contract_id(state), "card_id": card_id, "code": code}
    result = await run_mutation(
        "reset_pin",
        "Сбросить PIN карты.",
        payload,
        lambda: client.cards.reset_pin(
            contract_id=contract_id(state),
            card_id=card_id,
            code=code,
        ),
    )
    print_result("reset_pin", result)


# Метод set_card_comment.
# Устанавливает комментарий к карте.
# Передаёт card_id, contract_id и comment, выводит bool-envelope результата.
async def check_set_card_comment(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    comment = ask_value("comment")
    payload = {"contract_id": contract_id(state), "card_id": card_id, "comment": comment}
    result = await run_mutation(
        "set_card_comment",
        "Установить комментарий к карте.",
        payload,
        lambda: client.cards.set_card_comment(
            contract_id=contract_id(state),
            card_id=card_id,
            comment=comment,
        ),
    )
    print_result("set_card_comment", result)


# Метод set_card_group.
# Создаёт или изменяет группу карт.
# Передаёт name, contract_id и опциональный group_id, выводит envelope группы.
async def check_set_card_group(client: APIClient, state: dict[str, Any]) -> None:
    name = ask_value("name")
    group_id = ask_value(
        "group_id, Enter чтобы создать новую",
        default=saved(CURRENT_STATE, "group_id"),
        required=False,
    )
    payload = {"contract_id": contract_id(state), "name": name, "group_id": group_id}
    result = await run_mutation(
        "set_card_group",
        "Создать или изменить группу карт.",
        payload,
        lambda: client.card_groups.set_card_group(
            contract_id=contract_id(state),
            name=name,
            group_id=group_id,
        ),
    )
    print_result("set_card_group", result)


# Метод set_card_product.
# Меняет продукт карт: wallet или limit.
# Передаёт card_ids, product и contract_id, выводит envelope результата.
async def check_set_card_product(client: APIClient, state: dict[str, Any]) -> None:
    card_ids = ask_csv("card_ids через запятую")
    product = ask_value("product wallet/limit")
    payload = {"contract_id": contract_id(state), "card_ids": card_ids, "product": product}
    result = await run_mutation(
        "set_card_product",
        "Изменить продукт карт.",
        payload,
        lambda: client.ewallet.set_card_product(
            contract_id=contract_id(state),
            card_ids=card_ids,
            product=product,
        ),
    )
    print_result("set_card_product", result)


# Метод set_cards_to_group.
# Назначает карты в группу.
# Передаёт group_id, contract_id и cards_list JSON, выводит envelope результата.
async def check_set_cards_to_group(client: APIClient, state: dict[str, Any]) -> None:
    group_id = ask_value("group_id", default=saved(CURRENT_STATE, "group_id"))
    cards_list = ask_json("cards_list JSON list")
    payload = {"contract_id": contract_id(state), "group_id": group_id, "cards_list": cards_list}
    result = await run_mutation(
        "set_cards_to_group",
        "Назначить карты в группу.",
        payload,
        lambda: client.card_groups.set_cards_to_group(
            contract_id=contract_id(state),
            group_id=group_id,
            cards_list=cards_list,
        ),
    )
    print_result("set_cards_to_group", result)


# Метод set_limit.
# Создаёт или изменяет продуктовые лимиты.
# Передаёт список LimitRequestItem, выводит envelope с ID лимитов.
async def check_set_limit(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("ProductType", "Goods"))
    raw_items = ask_json("limits JSON list", example=limit_item_example(state))
    items = [LimitRequestItem.model_validate(item) for item in raw_items]
    payload = {"contract_id": contract_id(state), "limits": raw_items}
    result = await run_mutation(
        "set_limit",
        "Создать или изменить продуктовые лимиты.",
        payload,
        lambda: client.limits.set_limit(contract_id=contract_id(state), limits=items),
    )
    print_result("set_limit", result)


# Метод set_region_limit.
# Создаёт или изменяет региональные лимиты.
# Передаёт список RegionLimitRequestItem, выводит envelope с ID лимитов.
async def check_set_region_limit(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("Country", "Region"), need_azs=True)
    raw_items = ask_json("region_limits JSON list", example=region_limit_item_example(state))
    items = [RegionLimitRequestItem.model_validate(item) for item in raw_items]
    payload = {"contract_id": contract_id(state), "region_limits": raw_items}
    result = await run_mutation(
        "set_region_limit",
        "Создать или изменить региональные лимиты.",
        payload,
        lambda: client.region_limits.set_region_limit(
            contract_id=contract_id(state),
            region_limits=items,
        ),
    )
    print_result("set_region_limit", result)


# Метод set_restriction.
# Создаёт или изменяет товарные ограничители.
# Передаёт список RestrictionRequestItem, выводит envelope с ID ограничителей.
async def check_set_restriction(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("ProductType", "Goods"))
    raw_items = ask_json("restrictions JSON list", example=restriction_item_example(state))
    items = [RestrictionRequestItem.model_validate(item) for item in raw_items]
    payload = {"contract_id": contract_id(state), "restrictions": raw_items}
    result = await run_mutation(
        "set_restriction",
        "Создать или изменить товарные ограничители.",
        payload,
        lambda: client.restrictions.set_restriction(
            contract_id=contract_id(state),
            restrictions=items,
        ),
    )
    print_result("set_restriction", result)


# Метод update_mpc.
# Обновляет MPC/QR payload карты.
# Передаёт card_id, текущий PIN и необязательный новый PIN.
async def check_update_mpc(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    pin = ask_value("current MPC PIN")
    new_pin = ask_value("new MPC PIN (optional)", required=False)
    payload = {
        "card_id": card_id,
        "pin": "<redacted>",
        "new_pin": "<redacted>" if new_pin else None,
    }
    result = await run_mutation(
        "update_mpc",
        "Обновить MPC/QR payload карты.",
        payload,
        lambda: client.virtual_cards.update_mpc(card_id=card_id, pin=pin, new_pin=new_pin),
    )
    print_result("update_mpc", result)


# Метод update_template.
# Изменяет шаблон виртуальной карты.
# Передаёт template_id, type_, name и contract_id, выводит envelope результата.
async def check_update_template(client: APIClient, state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    type_ = ask_value("type_ (Limit или Wallet)")
    name = ask_value("name")
    payload = {
        "template_id": template_id,
        "contract_id": contract_id(state),
        "type_": type_,
        "name": name,
    }
    result = await run_mutation(
        "update_template",
        "Изменить шаблон виртуальной карты.",
        payload,
        lambda: client.templates.update_template(
            template_id=template_id,
            contract_id=contract_id(state),
            type_=type_,
            name=name,
        ),
    )
    print_result("update_template", result)


# Метод update_template_georestriction.
# Изменяет геоограничение шаблона.
# Передаёт template_id, georestriction_id и payload JSON, выводит envelope результата.
async def check_update_template_georestriction(client: APIClient, state: dict[str, Any]) -> None:
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    georestriction_id = ask_value(
        "georestriction_id", default=saved(CURRENT_STATE, "georestriction_id")
    )
    payload_data = ask_json("TemplateGeoRestrictionCreateRequest JSON object")
    use_post = ask_bool("use_post method override", default=True)
    payload = {
        "template_id": template_id,
        "georestriction_id": georestriction_id,
        "payload": payload_data,
        "use_post": use_post,
    }
    result = await run_mutation(
        "update_template_georestriction",
        "Изменить геоограничение шаблона.",
        payload,
        lambda: client.templates.update_template_georestriction(
            template_id=template_id,
            georestriction_id=georestriction_id,
            payload=payload_data,
            contract_id=contract_id(state),
            use_post=use_post,
        ),
    )
    print_result("update_template_georestriction", result)


# Метод update_template_limit.
# Изменяет лимит шаблона.
# Передаёт template_id, limit_id и limits JSON, выводит envelope результата.
async def check_update_template_limit(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("ProductType", "Goods"))
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    limit_id = ask_value("limit_id", default=saved(CURRENT_STATE, "limit_id"))
    limits = ask_json("limits JSON list", example=limit_item_example(state))
    use_post = ask_bool("use_post method override", default=True)
    payload = {
        "template_id": template_id,
        "limit_id": limit_id,
        "limits": limits,
        "use_post": use_post,
    }
    result = await run_mutation(
        "update_template_limit",
        "Изменить лимит шаблона.",
        payload,
        lambda: client.templates.update_template_limit(
            template_id=template_id,
            limit_id=limit_id,
            limits=limits,
            contract_id=contract_id(state),
            use_post=use_post,
        ),
    )
    print_result("update_template_limit", result)


# Метод update_template_restriction.
# Изменяет товарное ограничение шаблона.
# Передаёт template_id, restriction_id и payload JSON, выводит envelope результата.
async def check_update_template_restriction(client: APIClient, state: dict[str, Any]) -> None:
    await ensure_reference_data(client, state, dictionaries=("ProductType", "Goods"))
    template_id = ask_value("template_id", default=saved(CURRENT_STATE, "template_id"))
    restriction_id = ask_value("restriction_id", default=saved(CURRENT_STATE, "restriction_id"))
    product_type = (
        reference_value(state, "product_type")
        or reference_value(state, "goods_code")
        or "1-276PF01"
    )
    payload_data = ask_json(
        "TemplateRestrictionCreateRequest JSON object",
        example=json.dumps(
            {"product_type": product_type, "restriction_type": 2},
            ensure_ascii=False,
        ),
    )
    use_post = ask_bool("use_post method override", default=True)
    payload = {
        "template_id": template_id,
        "restriction_id": restriction_id,
        "payload": payload_data,
        "use_post": use_post,
    }
    result = await run_mutation(
        "update_template_restriction",
        "Изменить товарное ограничение шаблона.",
        payload,
        lambda: client.templates.update_template_restriction(
            template_id=template_id,
            restriction_id=restriction_id,
            payload=payload_data,
            contract_id=contract_id(state),
            use_post=use_post,
        ),
    )
    print_result("update_template_restriction", result)


# Метод verify_pin.
# Проверяет PIN карты.
# Передаёт card_id и contract_id, выводит bool-envelope результата.
async def check_verify_pin(client: APIClient, state: dict[str, Any]) -> None:
    card_id = ask_value("card_id", default=first_card_id(state))
    payload = {"contract_id": contract_id(state), "card_id": card_id}
    result = await run_read(
        "verify_pin",
        "Проверить PIN карты.",
        payload,
        client.cards.verify_pin(contract_id=contract_id(state), card_id=card_id),
    )
    print_result("verify_pin", result)


CHECKS: list[tuple[str, Check]] = [
    ("auth_user", check_auth_user),
    ("get_info", check_get_info),
    ("get_azs_filters", check_get_azs_filters),
    ("get_azs_list_v1", check_get_azs_list_v1),
    ("get_azs_list_v2", check_get_azs_list_v2),
    ("get_dictionary", check_get_dictionary),
    ("get_cards_v2", check_get_cards_v2),
    ("attach_card", check_attach_card),
    ("attach_contracts", check_attach_contracts),
    ("block_card", check_block_card),
    ("check_purchase", check_check_purchase),
    ("confirm_mpc", check_confirm_mpc),
    ("create_invite", check_create_invite),
    ("create_template", check_create_template),
    ("create_template_georestriction", check_create_template_georestriction),
    ("create_template_limit", check_create_template_limit),
    ("create_template_restriction", check_create_template_restriction),
    ("create_user", check_create_user),
    ("create_virtual_card", check_create_virtual_card),
    ("delete_invite", check_delete_invite),
    ("delete_mpc", check_delete_mpc),
    ("delete_template", check_delete_template),
    ("delete_template_georestriction", check_delete_template_georestriction),
    ("delete_template_limit", check_delete_template_limit),
    ("delete_template_restriction", check_delete_template_restriction),
    ("delete_user", check_delete_user),
    ("detach_card", check_detach_card),
    ("detach_contracts", check_detach_contracts),
    ("download_report_file", check_download_report_file),
    ("download_report_file_v1", check_download_report_file_v1),
    ("generate_payment_qr", check_generate_payment_qr),
    ("get_card_detail", check_get_card_detail),
    ("get_card_drivers", check_get_card_drivers),
    ("get_card_groups", check_get_card_groups),
    ("get_card_transactions_v2", check_get_card_transactions_v2),
    ("get_cards_by_group", check_get_cards_by_group),
    ("get_cards_v1", check_get_cards_v1),
    ("get_contract_data", check_get_contract_data),
    ("get_documents", check_get_documents),
    ("get_final_prices", check_get_final_prices),
    ("get_invites", check_get_invites),
    ("get_invoices", check_get_invoices),
    ("get_limits", check_get_limits),
    ("get_mpc_qr_list", check_get_mpc_qr_list),
    ("get_payments", check_get_payments),
    ("get_region_limits", check_get_region_limits),
    ("get_report_job_list_v1", check_get_report_job_list_v1),
    ("get_report_jobs", check_get_report_jobs),
    ("get_reports", check_get_reports),
    ("get_restrictions", check_get_restrictions),
    ("get_template_georestrictions", check_get_template_georestrictions),
    ("get_template_limits", check_get_template_limits),
    ("get_template_restrictions", check_get_template_restrictions),
    ("get_templates", check_get_templates),
    ("get_transaction_detail", check_get_transaction_detail),
    ("get_transactions_v1", check_get_transactions_v1),
    ("get_transactions_v2", check_get_transactions_v2),
    ("get_users", check_get_users),
    ("init_mpc", check_init_mpc),
    ("move_to_card", check_move_to_card),
    ("move_to_contract", check_move_to_contract),
    ("order_cards", check_order_cards),
    ("order_documents_email", check_order_documents_email),
    ("order_invoice", check_order_invoice),
    ("order_report", check_order_report),
    ("order_report_v1", check_order_report_v1),
    ("prolong_invite", check_prolong_invite),
    ("release_virtual_card", check_release_virtual_card),
    ("remove_card_group", check_remove_card_group),
    ("remove_limit", check_remove_limit),
    ("remove_region_limit", check_remove_region_limit),
    ("remove_restriction", check_remove_restriction),
    ("resend_invite", check_resend_invite),
    ("reset_mpc", check_reset_mpc),
    ("reset_pin", check_reset_pin),
    ("set_card_comment", check_set_card_comment),
    ("set_card_group", check_set_card_group),
    ("set_card_product", check_set_card_product),
    ("set_cards_to_group", check_set_cards_to_group),
    ("set_limit", check_set_limit),
    ("set_region_limit", check_set_region_limit),
    ("set_restriction", check_set_restriction),
    ("update_mpc", check_update_mpc),
    ("update_template", check_update_template),
    ("update_template_georestriction", check_update_template_georestriction),
    ("update_template_limit", check_update_template_limit),
    ("update_template_restriction", check_update_template_restriction),
    ("verify_pin", check_verify_pin),
    ("logoff", check_logoff),
]


async def main() -> None:
    global CURRENT_CLIENT, CURRENT_METHOD_NAME, CURRENT_STATE

    if len(CHECKS) != 89:
        raise RuntimeError(f"В скрипте должно быть 89 проверок, сейчас {len(CHECKS)}")

    env_file = resolve_env_file()
    print(color(f"Конфигурация: {env_file}", Color.DIM))
    print_header(f"Проверка apisdkopti24 {__version__}: {len(CHECKS)} методов")
    settings = ConnectionSettings.from_env(env_file=env_file)
    credentials = EnvironmentCredentialsProvider.from_env(env_file=env_file)
    tracing_http_client = TracingHTTPClient()
    transport = AsyncTransport(
        settings.base_url,
        default_timeout=settings.timeouts.default,
        retry_policy=settings.retry_policy,
        rate_limit_policy=settings.rate_limit_policy,
        concurrency_policy=settings.concurrency_policy,
        allow_insecure_http=settings.allow_insecure_http,
        http_client=tracing_http_client,
    )
    state: dict[str, Any] = {"logged_off": False}
    CURRENT_STATE = state
    results: list[tuple[str, str]] = []

    try:
        async with APIClient(
            settings=settings,
            credentials_provider=credentials,
            transport=transport,
        ) as client:
            CURRENT_CLIENT = client
            for method_name, check in CHECKS:
                while True:
                    print_method_intro(method_name)
                    try:
                        CURRENT_METHOD_NAME = method_name
                        await check(client, state)
                    except RetryMethod as exc:
                        print(color(f"\n{method_name}: EDIT - {exc}", Color.YELLOW))
                        continue
                    except SkipMethod as exc:
                        print(color(f"\n{method_name}: SKIPPED - {exc}", Color.YELLOW))
                        results.append((method_name, "SKIPPED"))
                    except Exception as exc:
                        print(color(f"\n{method_name}: ERROR - {compact_error(exc)}", Color.RED))
                        results.append((method_name, "ERROR"))
                    else:
                        results.append((method_name, "OK"))
                    break

            if not state.get("logged_off"):
                try:
                    await client.auth.logoff()
                except Exception as exc:
                    print(f"final logoff: ERROR - {type(exc).__name__}: {exc}")
    finally:
        await transport.aclose()
        await tracing_http_client.aclose()

    print_header("ИТОГ")
    for method_name, status in results:
        status_color = (
            Color.GREEN if status == "OK" else Color.YELLOW if status == "SKIPPED" else Color.RED
        )
        print(f"{method_name:40} {color(status, status_color)}")


if __name__ == "__main__":
    asyncio.run(main())
