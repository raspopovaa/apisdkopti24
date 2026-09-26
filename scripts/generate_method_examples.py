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
import inspect
import io
import json
import logging
import sys
import textwrap
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, get_type_hints
from urllib.parse import parse_qsl, unquote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import black  # noqa: E402
import httpx  # noqa: E402
import yaml  # noqa: E402
from pydantic import ValidationError as PydanticValidationError  # noqa: E402

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
SHOWN_HEADERS = ("api_key", "session_id", "contract_id", "date_time", "content-type")
MAX_LIST_ITEMS = 2
BLACK_MODE = black.Mode(line_length=100, string_normalization=False)
REGISTRY = build_default_registry()


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


async def record(
    runner: Callable[[APIClient], Awaitable[object]],
    *,
    response_body: object,
    status_code: int = 200,
) -> Recording:
    """Выполнить сценарий на подставном транспорте и записать запросы SDK."""
    auth_body = load_fixture("auth", "auth_user")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/authUser"):
            return httpx.Response(200, json=auth_body)
        requests.append(request)
        return httpx.Response(status_code, json=response_body)

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


def expression_runner(
    expression: str,
    constants: dict[str, str],
) -> Callable[[APIClient], Awaitable[object]]:
    async def run(client: APIClient) -> object:
        namespace: dict[str, object] = {**constants, "client": client}
        return await eval(expression, namespace)  # noqa: S307 — выражение из репозитория

    return run


def example_runner(source: str, path: Path) -> Callable[[APIClient], Awaitable[object]]:
    namespace: dict[str, object] = {"__name__": "apisdkopti24_example"}
    exec(compile(source, str(path), "exec"), namespace)  # noqa: S102 — сгенерированный пример
    example = namespace["example"]
    assert callable(example)
    return example  # type: ignore[return-value]


# ---------------------------------------------------------------- пример .py


def render_example(domain: str, name: str, method: dict[str, Any], spec: OperationSpec) -> str:
    constants: dict[str, str] = method.get("constants") or {}
    names = sorted({"APIClient", "ConnectionSettings", "EnvironmentCredentialsProvider"})
    # Порядок как у isort в ruff: без учёта регистра.
    names = sorted({*names, *(method.get("imports") or [])}, key=str.lower)
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
        "",
        f"from apisdkopti24 import {', '.join(names)}",
        "",
    ]
    if constants:
        lines.append("# Условные значения: замените своими.")
        lines.extend(
            f"{key} = {json.dumps(value, ensure_ascii=False)}" for key, value in constants.items()
        )
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


def request_fields(request: httpx.Request, spec: OperationSpec) -> list[tuple[str, str, str, str]]:
    fields: list[tuple[str, str, str, str]] = []
    route = spec.resolve_route()
    template_parts = route.endpoint.split("/")
    path_parts = request.url.path.split("/")[-len(template_parts) :]
    for template_part, actual in zip(template_parts, path_parts, strict=True):
        if template_part.startswith("{") and template_part.endswith("}"):
            fields.append((template_part[1:-1], "путь", unquote(actual), "string"))
    for key, value in parse_qsl(request.url.query.decode(), keep_blank_values=True):
        fields.append((key, "строка запроса", value, "string"))
    content_type = request.headers.get("content-type", "")
    body = request.content.decode()
    if "x-www-form-urlencoded" in content_type:
        for key, value in parse_qsl(body, keep_blank_values=True):
            fields.append((key, "форма", value, "string"))
    elif "json" in content_type and body:
        for key, value in json.loads(body).items():
            rendered = json.dumps(value, ensure_ascii=False)
            fields.append((key, "тело JSON", rendered, wire_type(value)))
    if "contract_id" in request.headers:
        fields.append(("contract_id", "заголовок", request.headers["contract_id"], "string"))
    return fields


def http_block(request: httpx.Request) -> list[str]:
    target = request.url.path
    if request.url.query:
        target += "?" + unquote(request.url.query.decode())
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
            lines.append(json.dumps(json.loads(body), ensure_ascii=False, indent=2))
        else:
            lines.append(unquote(body.replace("+", " ")))
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


def parameter_rows(domain: str, name: str) -> list[str]:
    service_class = get_type_hints(ServiceContainer)[domain]
    signature = inspect.signature(getattr(service_class, name), eval_str=True)
    rows = ["| Параметр | Тип | По умолчанию |", "|---|---|---|"]
    for parameter in signature.parameters.values():
        if parameter.name == "self":
            continue
        annotation = inspect.formatannotation(parameter.annotation).replace("|", "\\|")
        default = (
            "обязательный"
            if parameter.default is inspect.Parameter.empty
            else f"`{parameter.default!r}`"
        )
        rows.append(f"| `{parameter.name}` | `{annotation}` | {default} |")
    return rows


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
    success: Recording,
    errors: list[tuple[dict[str, Any], Recording]],
    invalid: list[tuple[dict[str, Any], Recording]],
) -> str:
    page_dir = DOCS_DIR / domain
    route = spec.resolve_route()
    request = success.requests[-1]
    response, truncated = shorten(load_fixture(domain, name))
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
    lines.extend(
        [
            "## Что отправляет SDK",
            "",
            "Запрос записан при запуске примера выше: это ровно то, что SDK отправляет "
            "на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.",
            "",
            *http_block(request),
            "",
            "| Поле | Где передаётся | Значение | Тип в запросе |",
            "|---|---|---|---|",
            *(
                f"| `{field}` | {place} | `{value}` | {kind} |"
                for field, place, value, kind in request_fields(request, spec)
            ),
            "",
            "Значения в строке запроса и в форме передаются строками: `True` превращается "
            'в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и '
            "`session_id` SDK добавляет сам; сессию он получает при первом вызове.",
            "",
        ]
    )
    lines.extend(["## Что возвращает API", ""])
    if model_link:
        lines.append(f"SDK проверяет ответ моделью [`{response_type}`]({model_link}).")
    else:
        lines.append(f"SDK проверяет ответ моделью `{response_type}`.")
    lines.extend(
        [
            "Пример ответа взят из спецификации API 1.1.60"
            + (f"; списки сокращены до {MAX_LIST_ITEMS} элементов." if truncated else "."),
            "",
            *json_block(response),
            "",
            "Вывод примера на этом ответе:",
            "",
            "```text",
            success.stdout.rstrip() or "(пример ничего не выводит)",
            "```",
            "",
        ]
    )
    lines.extend(["## Ошибки", ""])
    if errors:
        lines.extend(
            [
                "Ошибки API, характерные для метода. Формат тела ответа — как у реального "
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
    notes = method.get("notes") or []
    if notes:
        lines.extend(["## Что важно знать", ""])
        lines.extend(f"- {' '.join(note.split())}" for note in notes)
        lines.append("")
    return "\n".join(lines)


def render_domain_index(source: dict[str, Any]) -> str:
    lines = [
        "---",
        f"description: {json.dumps('Учебные примеры: ' + source['title'], ensure_ascii=False)}",
        "---",
        "",
        f"# {source['title']}",
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
            f"| [{method['title']}]({name}.md) | {route.http_method} `{route.endpoint}` | "
            f"{yes_no(not is_read_only(spec))} | {yes_no(spec.billable)} | "
            f"{yes_no(spec.demo_available)} |"
        )
    lines.append("")
    return "\n".join(lines)


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
    constants: dict[str, str] = method.get("constants") or {}

    success = await record(
        example_runner(example_source, example_path),
        response_body=load_fixture(domain, name),
    )
    if success.error is not None:
        raise RuntimeError(f"Пример {domain}.{name} завершился ошибкой: {success.error!r}")
    if len(success.requests) != 1:
        raise RuntimeError(f"Пример {domain}.{name} должен отправить ровно один запрос")

    errors = []
    for error in method.get("errors") or []:
        recording = await record(
            expression_runner(method["call"], constants),
            response_body=error_body(error),
            status_code=error["status"],
        )
        if recording.error is None:
            raise RuntimeError(f"{domain}.{name}: ошибка {error['status']} не воспроизвелась")
        errors.append((error, recording))

    invalid = []
    for item in method.get("invalid") or []:
        recording = await record(
            expression_runner(item["code"], constants),
            response_body=load_fixture(domain, name),
        )
        if recording.error is None or recording.requests:
            raise RuntimeError(f"{domain}.{name}: вызов {item['code']} должен отклоняться до API")
        invalid.append((item, recording))

    page = render_page(domain, name, method, spec, example_source, success, errors, invalid)
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
        "## Разделы",
        "",
    ]
    for domain, source in sources.items():
        lines.append(
            f"- [{source['title']}]({domain}/index.md) — {' '.join(source['summary'].split())}"
        )
    lines.append("")
    return "\n".join(lines)


async def build_all() -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    sources = load_sources()
    for domain, source in sources.items():
        for name, method in source["methods"].items():
            outputs.update(await build_method(domain, name, method))
        outputs[DOCS_DIR / domain / "index.md"] = render_domain_index(source)
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
