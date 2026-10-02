"""Сгенерировать учебные примеры методов SDK и страницы документации к ним.

Источник — examples/methods/<домен>.yaml. Для каждого метода генератор:

1. создаёт запускаемый пример examples/methods/<домен>/<метод>.py;
2. прогоняет пример на подставном HTTP-транспорте с ответом из фикстуры
   спецификации и записывает запрос, который реально отправил SDK;
3. прогоняет ошибки API и неверные вызовы и записывает исключения SDK;
4. создаёт страницу docs/examples/<домен>/<метод>.md.

Сеть не используется. ``--check`` сравнивает результат с файлами в репозитории.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import functools
import inspect
import io
import json
import logging
import re
import sys
import textwrap
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Union, get_args, get_origin, get_type_hints
from urllib.parse import parse_qsl, unquote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
SCRIPTS_PATH = PROJECT_ROOT / "scripts"
for import_path in (SRC_PATH, SCRIPTS_PATH):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import black  # noqa: E402
import httpx  # noqa: E402
import yaml  # noqa: E402
from documentation_generator import (  # noqa: E402
    clean_docstring,
    format_type,
    load_metadata,
    parse_param_docs,
)
from pydantic import BaseModel  # noqa: E402
from pydantic import ValidationError as PydanticValidationError  # noqa: E402
from pydantic_docs import (  # noqa: E402
    _constraints,
    _model_types,
    _unwrap_annotated,
    code_cell,
)

from apisdkopti24 import APIClient, AsyncTransport  # noqa: E402
from apisdkopti24.operations import OperationSpec  # noqa: E402
from apisdkopti24.policies import SAFE_HTTP_METHODS  # noqa: E402
from apisdkopti24.registry import build_default_registry  # noqa: E402
from apisdkopti24.service_groups import ServiceContainer  # noqa: E402

EXAMPLES_DIR = PROJECT_ROOT / "examples" / "methods"
DOCS_DIR = PROJECT_ROOT / "docs" / "examples"
DATA_TYPES_DIR = PROJECT_ROOT / "docs" / "data-types"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "spec" / "1.1.60"
DOCS_SITE_URL = "https://raspopovaa.github.io/apisdkopti24/latest/"
BASE_URL = "https://api-demo.opti-24.ru/vip/"
# Договор из фикстуры authUser; пример выбирает его так же, как API_CONTRACT_ID.
CONTRACT_ID = "1-2Q4CN99"
SECRET_HEADERS = frozenset({"api_key", "session_id"})
# Значения этих полей запроса на страницах заменяются на «***», как в журналах SDK.
SECRET_FIELDS = frozenset({"password", "pin", "new_pin", "device_id"})
SHOWN_HEADERS = ("api_key", "session_id", "contract_id", "date_time", "content-type")
MAX_LIST_ITEMS = 2
BLACK_MODE = black.Mode(line_length=100, string_normalization=False)
REGISTRY = build_default_registry()
CONTRACTS_DIR = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"
API_CONTRACT = PROJECT_ROOT / "specifications" / "api-contract-v1.1.60.yaml"
QR_CONTRACT = PROJECT_ROOT / "specifications" / "api-qr-contract-v1.0.4.yaml"
COMPATIBILITY_DOC = PROJECT_ROOT / "docs" / "spec-compatibility.md"
DOC_METADATA = load_metadata()
# Общий конверт ответа описан один раз в «Типах данных», в таблицах метода не повторяется.
ENVELOPE_MODELS = frozenset({"ResponseStatus"})
# Параметр метода SDK называется иначе, чем поле запроса API.
PARAMETER_ALIASES = {"card_ids": "card_id"}
# То же для отдельных методов: (метод, параметр SDK) -> поле API.
METHOD_PARAMETER_ALIASES = {("set_card_group", "group_id"): "id"}


def api_parameter_name(method_name: str, parameter_name: str) -> str:
    return METHOD_PARAMETER_ALIASES.get(
        (method_name, parameter_name), PARAMETER_ALIASES.get(parameter_name, parameter_name)
    )


class _FrozenClock:
    """Постоянное время: запрос в документации не меняется от запуска к запуску."""

    def now(self) -> datetime:
        return datetime(2026, 1, 15, 10, 30, 0)

    def monotonic(self) -> float:
        return 0.0

    async def sleep(self, seconds: float) -> None:
        del seconds


def _quiet_logger() -> logging.Logger:
    quiet = logging.getLogger("apisdkopti24.examples.generator")
    quiet.handlers.clear()
    quiet.addHandler(logging.NullHandler())
    quiet.propagate = False
    return quiet


@dataclass(frozen=True)
class Recording:
    requests: tuple[httpx.Request, ...]
    stdout: str
    error: BaseException | None


def load_fixture(domain: str, name: str) -> dict[str, Any]:
    path = FIXTURES_DIR / domain / f"{name}.success.json"
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class MethodResponse:
    """Успешный ответ API для примера: JSON или файл."""

    body: object
    content_type: str | None = None

    @property
    def is_file(self) -> bool:
        return isinstance(self.body, bytes)


def method_response(domain: str, name: str, method: dict[str, Any]) -> MethodResponse:
    """Ответ из YAML, если фикстуры спецификации нет, иначе фикстура."""
    if "response_file" in method:
        file = method["response_file"]
        return MethodResponse(file["text"].encode("utf-8"), file["content_type"])
    if "response" in method:
        return MethodResponse(method["response"])
    fixture = FIXTURES_DIR / domain / f"{name}.success.json"
    if fixture.exists():
        return MethodResponse(load_fixture(domain, name))
    official = spec_official_response(name)
    if official is None:
        raise RuntimeError(f"{domain}.{name}: нет фикстуры, примера в спецификации и response")
    return MethodResponse(official)


def spec_official_response(name: str) -> object | None:
    """JSON из «Пример ответа» спецификации: первый объект, текст после него отбрасывается."""
    index = _api_contract_index(name)
    if index is None:
        return None
    raw = (api_contract_methods()[index]["api"].get("official_example") or {}).get("response") or ""
    start = raw.find("{")
    if start < 0:
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(raw[start:])
    except ValueError:
        return None
    return value


async def record(
    runner: Callable[[APIClient], Awaitable[object]],
    *,
    response: MethodResponse,
    status_code: int = 200,
    capture_auth: bool = False,
) -> Recording:
    """Выполнить сценарий на подставном транспорте и записать запросы SDK.

    Авторизацию SDK выполняет сам перед первым вызовом; её запрос не записывается,
    если пример не показывает саму авторизацию (``capture_auth``).
    """
    auth_body = load_fixture("auth", "auth_user")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/authUser") and not capture_auth:
            return httpx.Response(200, json=auth_body)
        requests.append(request)
        if response.is_file and status_code < 400:
            headers = {"content-type": response.content_type or "application/octet-stream"}
            return httpx.Response(status_code, content=response.body, headers=headers)
        return httpx.Response(status_code, json=response.body)

    logger = _quiet_logger()
    clock = _FrozenClock()
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = AsyncTransport(
        BASE_URL,
        http_client=http_client,
        logger=logger,
        clock=clock,
        jitter=lambda _cap: 0.0,
    )
    client = APIClient(
        base_url=BASE_URL,
        api_key="demo-api-key",
        login="demo-login",
        password="demo-password",
        transport=transport,
        logger=logger,
        clock=clock,
    )
    client.select_contract(contract_id=CONTRACT_ID)
    output = io.StringIO()
    error: BaseException | None = None
    try:
        with contextlib.redirect_stdout(output):
            await runner(client)
    except Exception as exc:  # noqa: BLE001 — ошибка и есть предмет записи
        error = exc
    finally:
        await client.aclose()
        await http_client.aclose()
    return Recording(tuple(requests), output.getvalue(), error)


def example_namespace(source: str, path: Path) -> dict[str, object]:
    """Импорты и константы примера: в них же вычисляются вызовы для ошибок."""
    namespace: dict[str, object] = {"__name__": "apisdkopti24_example"}
    # Выполняются только примеры, сгенерированные из examples/methods этого репозитория.
    exec(compile(source, str(path), "exec"), namespace)  # noqa: S102  # nosec B102
    return namespace


def expression_runner(
    expression: str,
    namespace: dict[str, object],
) -> Callable[[APIClient], Awaitable[object]]:
    async def run(client: APIClient) -> object:
        return await eval(expression, {**namespace, "client": client})  # noqa: S307  # nosec B307

    return run


def example_runner(namespace: dict[str, object]) -> Callable[[APIClient], Awaitable[object]]:
    example = namespace["example"]
    assert callable(example)
    return example  # type: ignore[return-value]


# ---------------------------------------------------------------- пример .py


def render_example(domain: str, name: str, method: dict[str, Any], spec: OperationSpec) -> str:
    constants: dict[str, str] = method.get("constants") or {}
    names = {"APIClient", "ConnectionSettings", "EnvironmentCredentialsProvider"}
    extra_imports: list[str] = []
    for item in method.get("imports") or []:
        if " " in item:
            extra_imports.append(item)
        else:
            names.add(item)
    # Порядок как у isort в ruff: без учёта регистра.
    sorted_names = sorted(names, key=str.lower)
    goal = textwrap.fill(" ".join(method["goal"].split()), width=88)
    lines = [
        f'"""{method["title"]}: client.{domain}.{name}().',
        "",
        goal,
        "",
        "Запуск:",
        "    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,",
        "       API_CONTRACT_ID.",
        "    2. Замените условные значения ниже своими.",
        f"    3. python examples/methods/{domain}/{name}.py",
        "",
        "Разбор запроса, ответа и ошибок:",
        f"{DOCS_SITE_URL}examples/{domain}/{name}/",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import asyncio",
        "import os",
        *sorted(line for line in extra_imports if not line.startswith("from apisdkopti24")),
        "",
        f"from apisdkopti24 import {', '.join(sorted_names)}",
        *sorted(line for line in extra_imports if line.startswith("from apisdkopti24")),
        "",
    ]
    if constants:
        lines.append("# Условные значения: замените своими.")
        lines.extend(f"{key} = {python_literal(value)}" for key, value in constants.items())
        lines.append("")
    lines.extend(["", "async def example(client: APIClient) -> None:"])
    lines.extend(textwrap.indent(method["body"].rstrip(), "    ").splitlines())
    lines.extend(["", "", "async def main() -> None:"])
    reason = confirmation_reason(spec)
    if reason:
        prompt = f"Вызов {reason} на реальном API. Продолжить? [yes/no] "
        lines.extend(
            [
                f"    answer = input({json.dumps(prompt, ensure_ascii=False)})",
                '    if answer.strip().lower() != "yes":',
                "        return",
            ]
        )
    lines.extend(
        [
            "    settings = ConnectionSettings.from_env()",
            "    credentials = EnvironmentCredentialsProvider.from_env()",
            "    async with APIClient(settings=settings, credentials_provider=credentials) as client:",
            '        contract_id = os.getenv("API_CONTRACT_ID")',
            "        if contract_id:",
            "            client.select_contract(contract_id=contract_id)",
            "        await example(client)",
            "",
            "",
            'if __name__ == "__main__":',
            "    asyncio.run(main())",
            "",
        ]
    )
    return black.format_str("\n".join(lines), mode=BLACK_MODE)


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


# ------------------------------------------------------------ страница .md


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


# ------------------------------------------------- спецификация и модели


def clean_text(value: object) -> str:
    """Одна строка для ячейки таблицы: без переносов и с экранированным «|»."""
    return " ".join(str(value).split()).replace("|", "\\|")


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


def method_notes(
    domain: str,
    name: str,
    wire_fields: list[tuple[str, str, str, str]],
) -> list[str]:
    """Факты о методе для раздела «Что важно знать»: без ссылок на документы-источники."""
    variant = spec_variant(domain, name) or {}
    function = service_function(domain, name)
    signature = inspect.signature(function, eval_str=True)
    sdk_parameters = {
        api_parameter_name(name, parameter.name): parameter
        for parameter in signature.parameters.values()
        if parameter.name != "self"
    }
    notes: list[str] = []
    request_deviations = request_compatibility_rows(name)
    confirmed_parameters = {cells[1].strip("`") for cells in request_deviations}
    for _, parameter_name, _documented, actual, sdk_behaviour in request_deviations:
        notes.append(f"Параметр {parameter_name}: {actual}. В SDK — {sdk_behaviour}.")
    wire_names = {field for field, *_ in wire_fields}
    supported_names = set(sdk_parameters) | {
        alias
        for model in request_models(domain, name)
        for field_name, field in model.model_fields.items()
        for alias in (field_name, field.alias)
        if alias
    }
    for path, parameter in spec_request_parameters(domain, name).items():
        sdk_parameter = sdk_parameters.get(path)
        if path in confirmed_parameters:
            continue
        if parameter.get("required") and sdk_parameter is not None:
            if sdk_parameter.default is inspect.Parameter.empty:
                continue
            if path == "contract_id":
                notes.append(
                    "`contract_id` можно не передавать: SDK подставит договор, выбранный "
                    "при авторизации."
                )
            elif sdk_parameter.default is None:
                notes.append(
                    f"`{path}` обязателен для API, хотя в SDK необязателен: без него SDK не "
                    "передаст поле, поэтому указывайте его явно."
                )
            else:
                notes.append(
                    f"`{path}` SDK передаёт всегда; значение по умолчанию — "
                    f"`{sdk_parameter.default!r}`."
                )
        if "." in path or "[" in path:
            continue
        if path == "data" and "(всё тело)" in wire_names:
            continue
        if path not in wire_names and path not in supported_names:
            notes.append(f"Параметр API `{path}` в SDK не поддерживается.")
    for _methods, field, _documented, actual, model in compatibility_rows(name):
        notes.append(f"Поле {field}: {actual}. Тип в модели SDK: {model}.")
    corrections = variant.get("fixture_corrections") or []
    if corrections:
        fields = ", ".join(f"`{item['path']}`" for item in corrections)
        notes.append(f"В примере ответа поля {fields} заполнены условными значениями.")
    return notes


def error_body(error: dict[str, Any]) -> dict[str, object]:
    return {
        "status": {
            "code": error["status"],
            "errors": [{"type": error["type"], "message": error["message"]}],
        }
    }


def render_page(
    domain: str,
    name: str,
    method: dict[str, Any],
    spec: OperationSpec,
    example_source: str,
    method_result: MethodResponse,
    success: Recording,
    errors: list[tuple[dict[str, Any], Recording]],
    invalid: list[tuple[dict[str, Any], Recording]],
) -> str:
    page_dir = DOCS_DIR / domain
    route = spec.resolve_route()
    request = success.requests[-1]
    response, truncated = (
        shorten(method_result.body) if not method_result.is_file else (None, False)
    )
    response_type = spec.response_type.__name__ if spec.response_type else "bytes"
    model_link = data_type_link(response_type, page_dir)
    description = (
        f"{method['title']}: пример client.{domain}.{name}() с запросом, ответом и ошибками."
    )
    lines = [
        "---",
        f"description: {json.dumps(description, ensure_ascii=False)}",
        "---",
        "",
        "<!-- Сгенерировано scripts/generate_method_examples.py из "
        f"examples/methods/{domain}.yaml. Не редактируйте вручную. -->",
        "",
        f"# {method['title']}",
        "",
        f"`client.{domain}.{name}()` · [справочник метода](../../methods/{domain}.md) · "
        f"[исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/"
        f"examples/methods/{domain}/{name}.py)",
        "",
        " ".join(method["goal"].split()),
        "",
        "| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |",
        "|---|---|:---:|:---:|:---:|---|",
        f"| {route.http_method} | `{route.api_version}/{route.endpoint}` | "
        f"{yes_no(not is_read_only(spec))} | {yes_no(spec.billable)} | "
        f"{yes_no(spec.demo_available)} | {retry_text(spec)} |",
        "",
    ]
    reason = confirmation_reason(spec)
    if reason:
        lines.extend(
            [
                f'!!! warning "Вызов {reason}"',
                "    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает "
                "подтверждение перед вызовом.",
                "",
            ]
        )
    lines.extend(["## Пример", "", "```python", example_source.rstrip(), "```", ""])
    lines.extend(["### Параметры метода", "", *parameter_rows(domain, name), ""])
    lines.extend(["### Модели запроса", "", *request_model_blocks(domain, name, page_dir)])
    wire_fields = request_fields(request, spec)
    spec_parameters = spec_request_parameters(domain, name)
    lines.extend(
        [
            "## Что отправляет SDK",
            "",
            "Запрос записан при запуске примера выше: это ровно то, что SDK отправляет "
            "на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.",
            "",
            *http_block(request),
            "",
            "| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |",
            "|---|---|---|---|:---:|---|",
            *(
                wire_field_row(field, place, value, kind, spec_parameters)
                for field, place, value, kind in wire_fields
            ),
            "",
            "Значения в строке запроса и в форме передаются строками: `True` превращается "
            'в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и '
            "`session_id` SDK добавляет сам; сессию он получает при первом вызове.",
            "",
        ]
    )
    lines.extend(["## Что возвращает API", ""])
    if method_result.is_file:
        lines.extend(
            [
                "Метод возвращает файл: SDK отдаёт его содержимое как `bytes`, без "
                "проверки моделью. Если API вместо файла ответил ошибкой в JSON, SDK "
                "выбросит исключение, как для обычных методов.",
                "",
                f"В примере сервер отвечает файлом с `Content-Type: "
                f"{method_result.content_type}`.",
                "",
            ]
        )
    else:
        if model_link:
            lines.append(f"SDK проверяет ответ моделью [`{response_type}`]({model_link}).")
        else:
            lines.append(f"SDK проверяет ответ моделью `{response_type}`.")
        source_text = " ".join(str(method.get("response_note") or "Пример ответа").split())
        lines.extend(
            [
                source_text
                + (f"; списки сокращены до {MAX_LIST_ITEMS} элементов." if truncated else "."),
                "",
                *json_block(response),
                "",
            ]
        )
    lines.extend(
        [
            "Вывод примера на этом ответе:",
            "",
            "```text",
            success.stdout.rstrip() or "(пример ничего не выводит)",
            "```",
            "",
        ]
    )
    response_blocks = response_model_blocks(domain, name, spec, page_dir)
    if response_blocks:
        lines.extend(["### Модели ответа", "", *response_blocks])
    lines.extend(["## Ошибки", ""])
    if errors:
        lines.extend(
            [
                "Ошибки API, характерные для метода. Формат тела ответа — как у "
                "API; текст сообщения сервера условный. Исключение и его текст записаны "
                "при выполнении вызова в SDK.",
                "",
            ]
        )
    for error, recording in errors:
        assert recording.error is not None
        lines.extend(
            [
                f"### {error['status']} · `{exception_name(recording.error)}`",
                "",
                f"**Почему:** {' '.join(error['why'].split())}",
                "",
                f"**Что делать:** {' '.join(error['fix'].split())}",
                "",
                "Ответ API:",
                "",
                *json_block(error_body(error)),
                "",
                "Что выбросит SDK (`str(error)`):",
                "",
                "```text",
                exception_text(recording.error),
                "```",
                "",
            ]
        )
    if invalid:
        lines.extend(
            [
                "### Ошибки до отправки запроса",
                "",
                "SDK проверяет параметры до обращения к методу API: запрос метода не "
                "отправляется и не расходует лимит запросов.",
                "",
            ]
        )
        for item, recording in invalid:
            assert recording.error is not None
            lines.extend(
                [
                    "```python",
                    f"await {item['code']}",
                    "```",
                    "",
                    f"{' '.join(item['why'].split())} Исключение "
                    f"`{exception_name(recording.error)}`:",
                    "",
                    "```text",
                    exception_text(recording.error),
                    "```",
                    "",
                ]
            )
    lines.extend(
        [
            "### Общие ошибки",
            "",
            "Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` "
            "(401 — SDK один раз авторизуется заново и повторяет запрос), "
            "`RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, "
            "`OperationTimeoutError`. Как их обрабатывать — в разделе "
            "[Ошибки и повторы](../../errors.md).",
            "",
        ]
    )
    notes = [
        *(" ".join(note.split()) for note in method.get("notes") or []),
        *method_notes(domain, name, wire_fields),
    ]
    if notes:
        lines.extend(["## Что важно знать", ""])
        lines.extend(f"- {note}" for note in notes)
        lines.append("")
    return "\n".join(lines)


def render_domain_section(domain: str, source: dict[str, Any]) -> list[str]:
    """Раздел общей страницы примеров: описание домена и таблица его методов."""
    lines = [
        f"### {source['title']}",
        "",
        " ".join(source["summary"].split()),
        "",
        "| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |",
        "|---|---|:---:|:---:|:---:|",
    ]
    for name, method in source["methods"].items():
        spec = REGISTRY.get(name)
        route = spec.resolve_route()
        lines.append(
            f"| [{method['title']}]({domain}/{name}.md) | {route.http_method} "
            f"`{route.endpoint}` | {yes_no(not is_read_only(spec))} | "
            f"{yes_no(spec.billable)} | {yes_no(spec.demo_available)} |"
        )
    lines.append("")
    return lines


# ------------------------------------------------------------------ сборка


def load_sources() -> dict[str, dict[str, Any]]:
    return {
        path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(EXAMPLES_DIR.glob("*.yaml"))
    }


async def build_method(
    domain: str,
    name: str,
    method: dict[str, Any],
) -> dict[Path, str]:
    spec = REGISTRY.get(name)
    example_path = EXAMPLES_DIR / domain / f"{name}.py"
    example_source = render_example(domain, name, method, spec)
    namespace = example_namespace(example_source, example_path)
    response = method_response(domain, name, method)
    capture_auth = name == "auth_user"

    success = await record(example_runner(namespace), response=response, capture_auth=capture_auth)
    if success.error is not None:
        raise RuntimeError(f"Пример {domain}.{name} завершился ошибкой: {success.error!r}")
    if len(success.requests) != 1:
        raise RuntimeError(
            f"Пример {domain}.{name} должен отправить ровно один запрос, "
            f"отправлено: {len(success.requests)}"
        )

    errors = []
    for error in method.get("errors") or []:
        recording = await record(
            expression_runner(method["call"], namespace),
            response=MethodResponse(error_body(error)),
            status_code=error["status"],
            capture_auth=capture_auth,
        )
        if recording.error is None:
            raise RuntimeError(f"{domain}.{name}: ошибка {error['status']} не воспроизвелась")
        errors.append((error, recording))

    invalid = []
    for item in method.get("invalid") or []:
        recording = await record(
            expression_runner(item["code"], namespace),
            response=response,
            capture_auth=capture_auth,
        )
        if recording.error is None or recording.requests:
            raise RuntimeError(f"{domain}.{name}: вызов {item['code']} должен отклоняться до API")
        invalid.append((item, recording))

    page = render_page(
        domain, name, method, spec, example_source, response, success, errors, invalid
    )
    return {example_path: example_source, DOCS_DIR / domain / f"{name}.md": page}


def render_examples_index(sources: dict[str, dict[str, Any]]) -> str:
    lines = [
        "---",
        "description: "
        + json.dumps(
            "Учебные примеры вызова методов SDK: код, HTTP-запрос, ответ и ошибки.",
            ensure_ascii=False,
        ),
        "---",
        "",
        "# Учебные примеры",
        "",
        "Каждый пример — короткий запускаемый скрипт и страница с его разбором:",
        "",
        "- **Пример** — код вызова метода с обработкой характерных ошибок;",
        "- **Что отправляет SDK** — HTTP-запрос и таблица полей: где передаётся каждое",
        "  поле и в каком виде;",
        "- **Что возвращает API** — пример ответа, модель проверки и вывод примера;",
        "- **Ошибки** — ответы API с ошибкой, исключения SDK с их текстом, причины и",
        "  что делать; отдельно — ошибки, которые SDK находит до отправки запроса.",
        "",
        "Запросы и тексты исключений на страницах не написаны вручную: генератор",
        "выполняет каждый пример на подставном транспорте и записывает, что отправил",
        "и выбросил SDK. Проверка в CI не даёт примерам разойтись с кодом.",
        "",
        "## Как запустить пример",
        "",
        "1. Установите SDK: `pip install apisdkopti24`.",
        "2. Создайте `.env` по образцу `.env.example`: `API_BASE_URL`, `API_KEY`,",
        "   `API_LOGIN`, `API_PASSWORD` и `API_CONTRACT_ID`.",
        "3. Замените в начале файла примера условные значения своими.",
        "4. Выполните `python examples/methods/<раздел>/<метод>.py`.",
        "",
        "Примеры, которые изменяют данные или тарифицируются, спрашивают подтверждение",
        "перед вызовом. Начинайте с DEMO-стенда.",
        "",
        "## Примеры по разделам",
        "",
    ]
    for domain, source in sources.items():
        lines.extend(render_domain_section(domain, source))
    lines.append("")
    return "\n".join(lines)


async def build_all() -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    sources = load_sources()
    for domain, source in sources.items():
        for name, method in source["methods"].items():
            outputs.update(await build_method(domain, name, method))
    outputs[DOCS_DIR / "index.md"] = render_examples_index(sources)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Сгенерировать учебные примеры методов SDK")
    parser.add_argument("--check", action="store_true", help="только проверить актуальность")
    args = parser.parse_args()
    outputs = asyncio.run(build_all())
    if args.check:
        stale = [
            path.relative_to(PROJECT_ROOT).as_posix()
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(
                "Учебные примеры устарели; запустите scripts/generate_method_examples.py:\n"
                + "\n".join(stale)
            )
        print("Учебные примеры актуальны")
        return
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Записано файлов: {len(outputs)}")


if __name__ == "__main__":
    main()
