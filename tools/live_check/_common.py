"""Общий код ручной проверки методов SDK: по одному файлу на метод в tools/live_check.

Каждый файл метода задаёт параметры вызова и вызывает :func:`run`. Здесь:

- загрузка ``.env`` и общего списка данных ``test_data.json``;
- авторизация с договором из ``test_data.json`` и выход из сессии в конце;
- вывод фактического HTTP-запроса и ответа (скрыты только секреты);
- проверка ответа моделью SDK: при ошибке выводится список несовпавших полей;
- сохранение запроса, ответа и результата проверки в ``tools/live_check/results``.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import suppress
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

LIVE_CHECK_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = LIVE_CHECK_DIR.parents[1]
# В checkout репозитория используем SDK из src/, иначе — установленный пакет.
if (PROJECT_ROOT / "src" / "apisdkopti24").is_dir():
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

import httpx  # noqa: E402
from pydantic import ValidationError  # noqa: E402

import apisdkopti24.models as models  # noqa: E402, F401 — модели запросов для файлов методов
from apisdkopti24 import (  # noqa: E402
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    __version__,
)
from apisdkopti24.transport import AsyncTransport  # noqa: E402

DATA_FILE = LIVE_CHECK_DIR / "test_data.json"
RESULTS_DIR = LIVE_CHECK_DIR / "results"
ENV_CANDIDATES = (LIVE_CHECK_DIR / ".env", PROJECT_ROOT / ".env", Path.cwd() / ".env")
SECRET_KEYS = frozenset(
    {
        "api_key",
        "session_id",
        "login",
        "password",
        "pin",
        "new_pin",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "authorization",
        "device_id",
        "security",
        "payment_payload",
        # Номер карты и платёжные данные QR не выводятся (правила репозитория); card_id виден.
        "card_number",
        "qr",
        "qr_code",
    }
)
# В запросе code — SMS-код подтверждения; в ответе — код статуса или товара.
REQUEST_SECRET_KEYS = SECRET_KEYS | {"code"}


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"


def color(text: str, value: str) -> str:
    return f"{value}{text}{Color.RESET}"


def mask(value: Any, secret_keys: frozenset[str] = SECRET_KEYS) -> Any:
    """Скрыть только секреты; ID, даты и коды остаются видны."""
    if isinstance(value, dict):
        return {
            key: (
                "***"
                if str(key).strip().lower().replace("-", "_") in secret_keys
                else mask(item, secret_keys)
            )
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [mask(item, secret_keys) for item in value]
    return value


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


# ---------------------------------------------------------------- общий список данных


def load_data() -> dict[str, Any]:
    if not DATA_FILE.is_file():
        raise SystemExit(
            f"Нет файла данных {DATA_FILE}.\n"
            "Скопируйте test_data.example.json в test_data.json и заполните своими значениями."
        )
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


_DATA: dict[str, Any] | None = None


def data() -> dict[str, Any]:
    """Данные test_data.json; файл читается при первом обращении, а не при импорте."""
    global _DATA
    if _DATA is None:
        _DATA = load_data()
    return _DATA


def placeholder(value: Any) -> str | None:
    """Первая незаполненная заглушка вида <...> в значении, в том числе вложенная."""
    if value in (None, ""):
        return "пустое значение"
    if isinstance(value, str):
        return value if value.startswith("<") and value.endswith(">") else None
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        return next((found for item in value if (found := placeholder(item))), None)
    return None


def common(key: str) -> Any:
    """Общее значение из test_data.json -> common (договор, карта, пользователь и т. п.)."""
    value = data().get("common", {}).get(key)
    if found := placeholder(value):
        raise SystemExit(f"Заполните common.{key} в {DATA_FILE.name} (сейчас: {found})")
    return value


def method_value(operation: str, key: str) -> Any:
    """Значение параметра метода из test_data.json -> methods -> <метод>."""
    value = data().get("methods", {}).get(operation, {}).get(key)
    if found := placeholder(value):
        raise SystemExit(
            f"Заполните methods.{operation}.{key} в {DATA_FILE.name} (сейчас: {found})"
        )
    return value


def apply_overrides(operation: str, params: dict[str, Any]) -> dict[str, Any]:
    """Заменить параметры значениями из test_data.json -> overrides -> <метод>."""
    overrides = data().get("overrides", {}).get(operation, {})
    unknown = sorted(set(overrides) - set(params))
    if unknown:
        raise SystemExit(
            f"overrides.{operation} в {DATA_FILE.name} содержит неизвестные параметры: "
            + ", ".join(unknown)
        )
    for key, value in overrides.items():
        if found := placeholder(value):
            raise SystemExit(
                f"Заполните overrides.{operation}.{key} в {DATA_FILE.name} (сейчас: {found})"
            )
    return {**params, **overrides}


def decimal(value: Any) -> Decimal:
    return Decimal(str(value))


# ---------------------------------------------------------------- HTTP-трассировка


class TracingHTTPClient:
    """httpx-клиент, который печатает и запоминает каждый запрос и ответ."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient()
        self.exchanges: list[dict[str, Any]] = []

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        request = self._describe_request(method, url, kwargs)
        response = await self._client.request(method, url, **kwargs)
        self._remember(request, response, response_body(response))
        return response

    def stream(self, method: str, url: str, **kwargs: Any) -> Any:
        request = self._describe_request(method, url, kwargs)
        return _RecordedStream(self, request, self._client.stream(method, url, **kwargs))

    def _describe_request(self, method: str, url: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        params = kwargs.get("params")
        body = kwargs.get("json") if kwargs.get("json") is not None else kwargs.get("data")
        request = {
            "method": method.upper(),
            "url": str(httpx.URL(url, params=params)) if params else url,
            "headers": mask(dict(kwargs.get("headers") or {})),
            "params": mask(params, REQUEST_SECRET_KEYS),
            "body": mask(body, REQUEST_SECRET_KEYS),
        }
        print(color("\nHTTP-запрос:", Color.BOLD + Color.MAGENTA))
        print(f"{request['method']} {request['url']}")
        print(color(f"Заголовки: {dumps(request['headers'])}", Color.DIM))
        if request["body"] is not None:
            print(color(f"Тело: {dumps(request['body'])}", Color.YELLOW))
        return request

    def _remember(self, request: dict[str, Any], response: httpx.Response, body: Any) -> None:
        print(color("\nHTTP-ответ:", Color.BOLD + Color.MAGENTA))
        print(
            f"Статус: {response.status_code}, content-type: {response.headers.get('content-type')}"
        )
        print(color(dumps(body), Color.DIM))
        self.exchanges.append(
            {"request": request, "response": {"status": response.status_code, "body": body}}
        )

    async def aclose(self) -> None:
        await self._client.aclose()


class _RecordedStream:
    def __init__(self, owner: TracingHTTPClient, request: dict[str, Any], inner: Any) -> None:
        self._owner, self._request, self._inner = owner, request, inner

    async def __aenter__(self) -> httpx.Response:
        self._response = await self._inner.__aenter__()
        return self._response

    async def __aexit__(self, *exc: Any) -> Any:
        size = self._response.num_bytes_downloaded
        self._owner._remember(self._request, self._response, f"<двоичные данные, {size} байт>")
        return await self._inner.__aexit__(*exc)


def response_body(response: httpx.Response) -> Any:
    try:
        return mask(response.json())
    except (ValueError, UnicodeDecodeError):
        return response.text[:2000] if response.content else None


# ---------------------------------------------------------------- запуск метода


def env_file() -> Path:
    explicit = os.environ.get("APISDK_ENV_FILE")
    if explicit:
        return Path(explicit).expanduser().resolve()
    for candidate in ENV_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise SystemExit(
        "Не найден .env: положите его в tools/live_check/ или в корень репозитория "
        "либо укажите путь в переменной APISDK_ENV_FILE."
    )


def find_method(client: APIClient, operation: str) -> Any:
    for field in client.services.__dataclass_fields__:
        method = getattr(getattr(client.services, field), operation, None)
        if callable(method):
            return method
    raise SystemExit(f"Метод {operation} не найден в SDK {__version__}")


def confirm_mutation(operation: str) -> None:
    print(
        color(
            f"\n{operation} изменяет данные или тарифицируется. "
            "Введите yes, чтобы выполнить, иначе запуск отменяется: ",
            Color.BOLD + Color.RED,
        ),
        end="",
    )
    if input().strip().lower() not in {"yes", "y", "да", "д"}:
        raise SystemExit("Отменено пользователем")


def run(
    operation: str,
    params: dict[str, Any],
    *,
    mutating: bool,
    description: str = "",
) -> None:
    """Выполнить один метод SDK с параметрами и сохранить результат."""
    params = apply_overrides(operation, params)
    print(color(f"\n{'=' * 80}\n{operation} — apisdkopti24 {__version__}", Color.BOLD + Color.CYAN))
    if description:
        print(description)
    print(color(f"Параметры вызова: {dumps(mask(params, REQUEST_SECRET_KEYS))}", Color.YELLOW))
    if mutating:
        confirm_mutation(operation)
    asyncio.run(_run(operation, params, description))


async def _run(operation: str, params: dict[str, Any], description: str) -> None:
    path = env_file()
    settings = ConnectionSettings.from_env(env_file=path)
    credentials = EnvironmentCredentialsProvider.from_env(env_file=path)
    tracing = TracingHTTPClient()
    transport = AsyncTransport(
        settings.base_url,
        default_timeout=settings.timeouts.default,
        retry_policy=settings.retry_policy,
        rate_limit_policy=settings.rate_limit_policy,
        concurrency_policy=settings.concurrency_policy,
        allow_insecure_http=settings.allow_insecure_http,
        http_client=tracing,
    )
    outcome: dict[str, Any] = {"status": "OK"}
    result: Any = None
    try:
        async with APIClient(
            settings=settings, credentials_provider=credentials, transport=transport
        ) as client:
            authenticated = operation == "auth_user"
            try:
                if not authenticated:
                    await client.auth.auth_user(contract_id=common("contract_id"))
                    authenticated = True
                    tracing.exchanges.clear()  # в результат попадает только проверяемый метод
                result = await find_method(client, operation)(**params)
                authenticated = operation != "logoff"
            except ValidationError as error:
                outcome = {"status": "MODEL_ERROR", "errors": validation_errors(error)}
            # Граница ручной проверки: любую ошибку показываем и сохраняем в результат.
            except Exception as error:  # noqa: BLE001
                stage = "метод" if authenticated else "авторизация"
                outcome = {"status": "ERROR", "error": f"{stage}: {type(error).__name__}: {error}"}
            if authenticated:
                with suppress(Exception):
                    await client.auth.logoff()
    finally:
        await transport.aclose()
        await tracing.aclose()
    exchanges = [item for item in tracing.exchanges if "/logoff" not in item["request"]["url"]]
    report(operation, outcome, result)
    save(operation, description, params, exchanges, outcome, result)


def validation_errors(error: ValidationError) -> list[dict[str, Any]]:
    return [
        {
            "field": ".".join(str(part) for part in item["loc"]),
            "type": item["type"],
            "message": item["msg"],
            "value": repr(item.get("input"))[:200],
        }
        for item in error.errors()
    ]


def result_payload(result: Any) -> Any:
    if isinstance(result, bytes):
        return f"<двоичные данные, {len(result)} байт>"
    if hasattr(result, "model_dump"):
        return mask(result.model_dump(by_alias=True, mode="json"))
    return mask(result)


def report(operation: str, outcome: dict[str, Any], result: Any) -> None:
    status = outcome["status"]
    if status == "OK":
        print(color(f"\n{operation}: УСПЕХ — ответ прошёл проверку модели SDK", Color.GREEN))
        print(color(dumps(result_payload(result)), Color.DIM))
    elif status == "MODEL_ERROR":
        print(color(f"\n{operation}: ОШИБКА МОДЕЛИ — ответ не совпал с моделью SDK", Color.RED))
        for item in outcome["errors"][:30]:
            print(
                f"  {item['field']}: {item['type']} — {item['message']}; значение={item['value']}"
            )
        if len(outcome["errors"]) > 30:
            print(f"  … ещё {len(outcome['errors']) - 30}")
    else:
        print(color(f"\n{operation}: ОШИБКА — {outcome['error']}", Color.RED))


def save(
    operation: str,
    description: str,
    params: dict[str, Any],
    exchanges: list[dict[str, Any]],
    outcome: dict[str, Any],
    result: Any,
) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = RESULTS_DIR / f"{operation}-{stamp}.json"
    if isinstance(result, bytes):
        path.with_suffix(".bin").write_bytes(result)
    record = {
        "operation": operation,
        "description": description,
        "sdk_version": __version__,
        "time": datetime.now().isoformat(timespec="seconds"),
        "params": mask(params, REQUEST_SECRET_KEYS),
        "exchanges": exchanges,
        "outcome": outcome,
        "result": result_payload(result) if outcome["status"] == "OK" else None,
    }
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as file:
        file.write(dumps(record))
    print(color(f"\nРезультат сохранён: {path}", Color.DIM))
