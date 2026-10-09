"""Форматирование значений для страниц примеров: литералы, маскирование, HTTP-блоки.

Модуль генератора scripts/generate_method_examples.py; отдельно не запускается.
"""

import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, unquote

import httpx
from method_examples_common import (
    DATA_TYPES_DIR,
    MAX_LIST_ITEMS,
    PROJECT_ROOT,
    SECRET_FIELDS,
    SECRET_HEADERS,
    SHOWN_HEADERS,
)
from pydantic import ValidationError as PydanticValidationError

from apisdkopti24.operations import OperationSpec
from apisdkopti24.policies import SAFE_HTTP_METHODS

# Метод HTTP не всегда говорит о побочных эффектах: эти POST только читают данные,
# а эти GET заказывают отчёт или повторно отправляют приглашение.
READ_ONLY_POST = frozenset({"auth_user", "check_purchase", "get_final_prices"})


MUTATING_GET = frozenset({"order_report_v1", "resend_invite"})


def python_literal(value: object) -> str:
    """Значение константы: строка «=выражение» вставляется как код Python."""
    if isinstance(value, str) and value.startswith("="):
        return value[1:]
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(python_literal(item) for item in value) + "]"
    if isinstance(value, dict):
        items = (f"{python_literal(key)}: {python_literal(item)}" for key, item in value.items())
        return "{" + ", ".join(items) + "}"
    return repr(value)


def is_read_only(spec: OperationSpec) -> bool:
    if spec.name in MUTATING_GET:
        return False
    if spec.name in READ_ONLY_POST:
        return True
    return spec.http_method in SAFE_HTTP_METHODS


def confirmation_reason(spec: OperationSpec) -> str | None:
    """Почему пример должен спросить подтверждение перед вызовом реального API."""
    reasons = []
    if not is_read_only(spec):
        reasons.append("изменяет данные")
    if spec.billable:
        reasons.append("тарифицируется")
    return " и ".join(reasons) or None


def yes_no(value: bool | None) -> str:
    if value is None:
        return "—"
    return "Да" if value else "Нет"


def retry_text(spec: OperationSpec) -> str:
    if spec.retry_class == "never" or not spec.idempotent:
        return "Нет: при неясном результате проверьте состояние, а не повторяйте запрос"
    return "Да: при сетевой ошибке и ответе 429/509"


def json_block(value: object) -> list[str]:
    return ["```json", json.dumps(value, ensure_ascii=False, indent=2), "```"]


def shorten(value: object) -> tuple[object, bool]:
    """Оставить в списках первые элементы, чтобы пример ответа читался целиком."""
    if isinstance(value, list):
        items = [shorten(item)[0] for item in value[:MAX_LIST_ITEMS]]
        nested = any(shorten(item)[1] for item in value[:MAX_LIST_ITEMS])
        return items, nested or len(value) > MAX_LIST_ITEMS
    if isinstance(value, dict):
        result: dict[str, object] = {}
        truncated = False
        for key, item in value.items():
            result[key], item_truncated = shorten(item)
            truncated = truncated or item_truncated
        return result, truncated
    return value, False


def wire_type(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int | float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return "string"


def masked(key: str, value: str) -> str:
    return "***" if key in SECRET_FIELDS else value


def mask_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "***" if key in SECRET_FIELDS else mask_json(item) for key, item in value.items()
        }
    if isinstance(value, list):
        return [mask_json(item) for item in value]
    return value


def request_fields(request: httpx.Request, spec: OperationSpec) -> list[tuple[str, str, str, str]]:
    fields: list[tuple[str, str, str, str]] = []
    route = spec.resolve_route()
    template_parts = route.endpoint.split("/")
    path_parts = request.url.path.split("/")[-len(template_parts) :]
    for template_part, actual in zip(template_parts, path_parts, strict=True):
        if template_part.startswith("{") and template_part.endswith("}"):
            fields.append((template_part[1:-1], "путь", unquote(actual), "string"))
    for key, value in parse_qsl(request.url.query.decode(), keep_blank_values=True):
        fields.append((key, "строка запроса", masked(key, value), "string"))
    content_type = request.headers.get("content-type", "")
    body = request.content.decode()
    if "x-www-form-urlencoded" in content_type:
        for key, value in parse_qsl(body, keep_blank_values=True):
            fields.append((key, "форма", masked(key, value), "string"))
    elif "json" in content_type and body:
        payload = mask_json(json.loads(body))
        if isinstance(payload, dict):
            for key, value in payload.items():
                rendered = json.dumps(value, ensure_ascii=False)
                fields.append((key, "тело JSON", rendered, wire_type(value)))
        else:
            rendered = json.dumps(payload, ensure_ascii=False)
            fields.append(("(всё тело)", "тело JSON", rendered, wire_type(payload)))
    if "contract_id" in request.headers:
        fields.append(("contract_id", "заголовок", request.headers["contract_id"], "string"))
    return fields


def wire_field_row(
    field: str,
    place: str,
    value: str,
    kind: str,
    spec_parameters: dict[str, dict[str, Any]],
) -> str:
    spec_parameter = spec_parameters.get(field)
    if field == "(всё тело)":
        required = "Да"
        description = "Тело запроса — JSON-массив, а не объект с полями."
    elif place == "путь":
        required = "Да"
        description = "Часть пути запроса: подставляется в маршрут вместо шаблона."
    elif place == "заголовок":
        required = "—"
        description = (
            "Договор в заголовке запроса. API принимает договор и так; SDK отправляет "
            "заголовок вместе с полем запроса."
        )
    elif spec_parameter is None:
        required = "—"
        description = "—"
    else:
        required = "Да" if spec_parameter.get("required") else "Нет"
        description = spec_parameter.get("description") or "—"
    return f"| `{field}` | {place} | `{value}` | {kind} | {required} | {clean_text(description)} |"


def http_block(request: httpx.Request) -> list[str]:
    target = request.url.path
    if request.url.query:
        pairs = parse_qsl(request.url.query.decode(), keep_blank_values=True)
        target += "?" + "&".join(f"{key}={masked(key, value)}" for key, value in pairs)
    lines = ["```http", f"{request.method} {target} HTTP/1.1", f"Host: {request.url.host}"]
    for header in SHOWN_HEADERS:
        if header in request.headers:
            value = "***" if header in SECRET_HEADERS else request.headers[header]
            display = "Content-Type" if header == "content-type" else header
            lines.append(f"{display}: {value}")
    body = request.content.decode()
    if body:
        content_type = request.headers.get("content-type", "")
        lines.append("")
        if "json" in content_type:
            lines.append(json.dumps(mask_json(json.loads(body)), ensure_ascii=False, indent=2))
        else:
            pairs = parse_qsl(body, keep_blank_values=True)
            lines.append("&".join(f"{key}={masked(key, value)}" for key, value in pairs))
    lines.append("```")
    return lines


def exception_name(error: BaseException) -> str:
    if isinstance(error, PydanticValidationError):
        return "pydantic.ValidationError"
    return type(error).__name__


def exception_text(error: BaseException) -> str:
    lines = [
        line
        for line in str(error).splitlines()
        if "errors.pydantic.dev" not in line and "For further information" not in line
    ]
    return "\n".join(lines).strip()


def data_type_link(type_name: str, page_dir: Path) -> str | None:
    matches = sorted(DATA_TYPES_DIR.glob(f"**/{type_name}.md"))
    if not matches:
        return None
    return Path(
        *([".."] * len(page_dir.relative_to(PROJECT_ROOT / "docs").parts)),
        matches[0].relative_to(PROJECT_ROOT / "docs"),
    ).as_posix()


def clean_text(value: object) -> str:
    """Одна строка для ячейки таблицы: без переносов и с экранированным «|»."""
    return " ".join(str(value).split()).replace("|", "\\|")
