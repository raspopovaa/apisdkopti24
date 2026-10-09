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
import inspect
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
SCRIPTS_PATH = PROJECT_ROOT / "scripts"
for import_path in (SRC_PATH, SCRIPTS_PATH):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import black  # noqa: E402
import yaml  # noqa: E402
from method_examples_common import (  # noqa: E402
    BLACK_MODE,
    DOCS_DIR,
    DOCS_SITE_URL,
    EXAMPLES_DIR,
    MAX_LIST_ITEMS,
    REGISTRY,
    api_parameter_name,
)
from method_examples_contracts import (  # noqa: E402
    compatibility_rows,
    request_compatibility_rows,
    spec_request_parameters,
    spec_variant,
)
from method_examples_format import (  # noqa: E402
    confirmation_reason,
    data_type_link,
    exception_name,
    exception_text,
    http_block,
    is_read_only,
    json_block,
    python_literal,
    request_fields,
    retry_text,
    shorten,
    wire_field_row,
    yes_no,
)
from method_examples_models import (  # noqa: E402
    parameter_rows,
    request_model_blocks,
    request_models,
    response_model_blocks,
    service_function,
)
from method_examples_recording import (  # noqa: E402
    MethodResponse,
    Recording,
    example_namespace,
    example_runner,
    expression_runner,
    method_response,
    record,
)

from apisdkopti24.operations import OperationSpec  # noqa: E402


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
        "1. Установите SDK по инструкции из раздела",
        "   [Установка через pip](../getting-started.md#pip).",
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
