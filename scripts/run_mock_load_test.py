"""Нагрузочная проверка SDK на заглушке HTTP без обращения к API.

Запросы проходят весь путь SDK: сервис, исполнитель, ограничитель частоты,
`AsyncTransport` и разбор ответа. Сеть заменена `httpx.MockTransport`, ответы —
обезличенные фикстуры `tests/fixtures/live/1.1.60`.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
import tracemalloc
from collections import Counter
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from apisdkopti24 import APIClient, AsyncTransport, ConnectionSettings, RateLimitPolicy
from apisdkopti24.credentials import StaticCredentialsProvider
from apisdkopti24.registry import build_default_registry

BASE_URL = "https://api.example.test/vip/"
CONTRACT_ID = "contract-id"
FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "live" / "1.1.60"
# Ограничитель частоты нельзя отключить: без значения он берёт 1 запрос/с для
# любой среды. Для заглушки задаём заведомо недостижимый предел.
UNBOUNDED_REQUESTS_PER_SECOND = 1_000_000.0
LOAD_OPERATIONS = {
    "auth_user": "auth",
    "get_info": "auth",
    "get_cards_v1": "cards",
    "get_cards_v2": "cards",
    "get_users": "users",
    "get_reports": "reports",
    "get_report_jobs": "reports",
}


def _fixture(domain: str, operation: str) -> dict[str, Any]:
    path = FIXTURES / domain / f"{operation}.success.json"
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def _auth_fixture() -> dict[str, Any]:
    # В обезличенной фикстуре у договоров одинаковые ID; для выбора договора нужны разные.
    payload = _fixture("auth", "auth_user")
    contracts = payload["data"]["contracts"]
    for index, contract in enumerate(contracts):
        contract["id"] = CONTRACT_ID if index == 0 else f"{CONTRACT_ID}-{index}"
    return payload


def _route_table() -> dict[tuple[str, str], tuple[str, dict[str, Any]]]:
    """Сопоставить метод и путь запроса с операцией и её ответом по реестру SDK."""
    registry = build_default_registry()
    routes: dict[tuple[str, str], tuple[str, dict[str, Any]]] = {}
    for operation, domain in LOAD_OPERATIONS.items():
        spec = registry.get(operation)
        path = f"/vip/{spec.default_version}/{spec.endpoint}"
        payload = _auth_fixture() if operation == "auth_user" else _fixture(domain, operation)
        routes[(spec.http_method.upper(), path)] = (operation, payload)
    return routes


class MockAPI:
    """Обработчик ``httpx.MockTransport``, который считает запросы по операциям."""

    def __init__(self) -> None:
        self.routes = _route_table()
        self.operation_counts: Counter[str] = Counter()

    def __call__(self, request: httpx.Request) -> httpx.Response:
        key = (request.method.upper(), request.url.path)
        if key not in self.routes:
            return httpx.Response(404, json={"status": {"code": 404}})
        operation, payload = self.routes[key]
        self.operation_counts[operation] += 1
        return httpx.Response(200, json=payload)

    @property
    def request_count(self) -> int:
        return sum(self.operation_counts.values())


async def run_load_test(total_operations: int, concurrency: int) -> dict[str, Any]:
    api = MockAPI()
    logger = logging.getLogger("apisdkopti24.mock_load")
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    rate_limit = RateLimitPolicy(requests_per_second=UNBOUNDED_REQUESTS_PER_SECOND)
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(api))
    transport = AsyncTransport(
        BASE_URL,
        http_client=http_client,
        rate_limit_policy=rate_limit,
        logger=logger,
    )
    client = APIClient(
        settings=ConnectionSettings(base_url=BASE_URL, rate_limit_policy=rate_limit),
        credentials_provider=StaticCredentialsProvider(
            api_key="api-key", login="login", password="password"
        ),
        transport=transport,
        logger=logger,
    )
    client.select_contract(contract_id=CONTRACT_ID)

    operations: list[Callable[[], Awaitable[Any]]] = [
        lambda: client.cards.get_cards_v2(),
        lambda: client.cards.get_cards_v1(contract_id=CONTRACT_ID),
        lambda: client.users.get_users(),
        lambda: client.reports.get_reports(),
        lambda: client.reports.get_report_jobs(),
        lambda: client.auth.get_info(period="2026-01"),
    ]
    semaphore = asyncio.Semaphore(concurrency)
    latencies: list[float] = []

    async def execute(index: int) -> str:
        async with semaphore:
            started = time.perf_counter()
            result = await operations[index % len(operations)]()
            latencies.append(time.perf_counter() - started)
            return type(result).__name__

    tracemalloc.start()
    started_at = time.perf_counter()
    try:
        # Первая волна идёт одновременно и проверяет единственный вход на все вызовы.
        results = await asyncio.gather(*(execute(index) for index in range(total_operations)))
    finally:
        elapsed = time.perf_counter() - started_at
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        await client.aclose()
        await transport.aclose()
        await http_client.aclose()

    sorted_latencies = sorted(latencies)

    def percentile(fraction: float) -> float | None:
        if not sorted_latencies:
            return None
        index = min(len(sorted_latencies) - 1, int(len(sorted_latencies) * fraction))
        return round(sorted_latencies[index] * 1000, 3)

    return {
        "total_operations": total_operations,
        "concurrency": concurrency,
        "elapsed_seconds": round(elapsed, 3),
        "operations_per_second": round(total_operations / elapsed, 2) if elapsed else None,
        "latency_ms_p50": percentile(0.50),
        "latency_ms_p95": percentile(0.95),
        "latency_ms_p99": percentile(0.99),
        "peak_memory_mib": round(peak_memory / (1024 * 1024), 3),
        "auth_calls": api.operation_counts["auth_user"],
        "request_count": api.request_count,
        "result_types": dict(Counter(results)),
        "operation_counts": dict(sorted(api.operation_counts.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Запустить нагрузочную проверку не менее 1000 операций SDK на заглушках."
    )
    parser.add_argument(
        "--operations", type=int, default=1200, help="Общее число выполняемых операций."
    )
    parser.add_argument(
        "--concurrency", type=int, default=100, help="Максимальное число одновременных операций."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.operations < 1000:
        raise SystemExit("--operations должен быть не меньше 1000")
    if args.concurrency < 1:
        raise SystemExit("--concurrency должен быть положительным")

    summary = asyncio.run(run_load_test(args.operations, args.concurrency))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
