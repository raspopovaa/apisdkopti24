"""Запуск примера на подставном транспорте и запись запроса, ответа и исключений.

Модуль генератора scripts/generate_method_examples.py; отдельно не запускается.
"""

import contextlib
import io
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from method_examples_common import BASE_URL, CONTRACT_ID, FIXTURES_DIR
from method_examples_contracts import _api_contract_index, api_contract_methods

from apisdkopti24 import APIClient, AsyncTransport


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
    # Пример начинается с открытой сессии, как после авторизации: logoff() без
    # сессии запрос не отправляет, а заголовки остальных примеров не меняются.
    client.restore_session(session_id=auth_body["data"]["session_id"], contract_id=CONTRACT_ID)
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
