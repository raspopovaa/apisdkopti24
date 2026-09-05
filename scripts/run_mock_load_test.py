from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
import tracemalloc
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from api_client_opti24 import APIClient, APISettings


class MockTransport:
    def __init__(self) -> None:
        self.request_count = 0
        self.auth_calls = 0
        self.endpoint_counts: Counter[str] = Counter()

    async def request(
        self,
        method: str,
        endpoint: str,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> dict[str, Any]:
        self.request_count += 1
        self.endpoint_counts[f"{api_version}:{method}:{endpoint}"] += 1
        await asyncio.sleep(0)

        if endpoint == "authUser":
            self.auth_calls += 1
            return {
                "status": {"code": 200},
                "data": {
                    "session_id": "SESSION123",
                    "client_id": "client-1",
                    "client_status": "active",
                    "user_id": "user-1",
                    "contracts": [
                        {"id": "1-AAA", "number": "NV0001"},
                        {"id": "1-BBB", "number": "NV0002"},
                    ],
                },
                "timestamp": 1710000000,
            }

        if endpoint == "info":
            period = kwargs.get("params", {}).get("period", "2025-01-01 00:00:00")
            return {
                "status": {"code": 200},
                "data": {
                    "from": period,
                    "to": period,
                    "client_info": {
                        "Client": "client-1",
                        "ClientType": "D",
                        "Contract": "1-AAA",
                        "ContractName": "Demo Client",
                    },
                    "methods": {"all": 42, "cards": 10, "cardgroups": 3, "card": 4},
                    "methods_info": {"actions_bill": {}, "actions_not_bill": {}},
                },
                "timestamp": 1710000000,
            }

        if endpoint == "cards" and api_version == "v2":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "19647206",
                            "group_id": "1-1F56KR",
                            "group_name": "Тестовая группа",
                            "contract_id": "1-AAA",
                            "contract_name": "СЗ01590002",
                            "number": "7005830900073164",
                            "status": "Active",
                            "status_name": "Активна",
                            "product": "limit",
                            "product_name": "Лимитная схема",
                            "carrier": "Virtual Card",
                            "carrier_name": "Виртуальная карта",
                            "platon": False,
                            "avtodor": True,
                            "sync_group_state": "Не синхронизирована",
                            "users": ["1-PBQRL0E"],
                            "mpc": True,
                        }
                    ],
                },
                "timestamp": 1710000000,
            }

        if endpoint == "cards" and api_version == "v1":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "382359",
                            "contract_id": "1-AAA",
                            "number": "7005830001422138",
                            "status": "Active",
                            "can_work_offline": True,
                            "card_auth_type": "PIN",
                            "comment": "Комментарий",
                            "date_expired": "2034-09-30 23:59:59",
                            "date_last_usage": "2015-04-27 00:00:00",
                            "date_released": "2014-09-24 00:00:00",
                            "servicecenter_last_usage_name": "AZS103261",
                            "transaction_last_detail": "",
                            "transaction_timeout": {"type": "H", "value": "1"},
                            "product": "limit",
                            "payment_of_tolls": "N",
                        }
                    ],
                },
                "timestamp": 1710000000,
            }

        if endpoint == "users" and method.upper() == "GET":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "1-USER",
                            "login": "79999999999",
                            "first_name": "Иван",
                            "last_name": "Иванов",
                            "date": "2020-01-01",
                            "active": True,
                            "role": {"id": "driver", "name": "Водитель"},
                            "access": {"web": True, "api": True, "mobile": True},
                            "mobile_phone": "79999999999",
                        }
                    ],
                },
                "timestamp": 1710000000,
            }

        if endpoint == "reports" and api_version == "v2" and method.upper() == "GET":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "report-1",
                            "name": "Транзакционный отчет",
                            "formats": ["pdf", "xlsx"],
                            "parameters": [
                                {
                                    "name": "contract_id",
                                    "value": "1-AAA",
                                    "label": "Договор",
                                    "default_value": "1-AAA",
                                    "menu_values": None,
                                    "type": "Contract",
                                }
                            ],
                        }
                    ],
                },
                "timestamp": 1710000000,
            }

        if endpoint == "reports/jobs" and api_version == "v2":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "date": "2025-01-01 00:00:00",
                            "client_id": "client-1",
                            "user_id": "user-1",
                            "contract_id": "1-AAA",
                            "contract_name": "Demo Client",
                            "job_id": "job-1",
                            "report_name": "Transactions",
                            "report_format": "xlsx",
                            "available_after": 0,
                        }
                    ],
                },
                "timestamp": 1710000000,
            }

        raise ValueError(f"Unexpected request: {api_version} {method} {endpoint}")

    async def aclose(self) -> None:
        return None


async def run_load_test(total_operations: int, concurrency: int) -> dict[str, Any]:
    transport = MockTransport()
    logger = logging.getLogger("api_client_opti24.mock_load")
    logger.addHandler(logging.NullHandler())
    client = APIClient(
        settings=APISettings(
            base_url="https://example.invalid/vip/",
            api_key="FAKE_API_KEY",
            login="demo",
            password="secret",
        ),
        transport=transport,
        logger=logger,
    )
    client.select_contract(contract_id="1-AAA")

    initial_burst = min(concurrency, total_operations)
    remaining = total_operations - initial_burst

    tracemalloc.start()
    started_at = time.perf_counter()

    burst_results = await asyncio.gather(
        *(client.cards.get_cards_v2() for _ in range(initial_burst))
    )
    assert all(item.total_count == 1 for item in burst_results)

    operations = [
        lambda: client.cards.get_cards_v2(),
        lambda: client.cards.get_cards_v1(contract_id="1-AAA"),
        lambda: client.users.get_users(),
        lambda: client.reports.get_reports(),
        lambda: client.reports.get_report_jobs(),
        lambda: client.auth.get_info(period="2025-01-15 12:30:00"),
    ]

    semaphore = asyncio.Semaphore(concurrency)
    latencies: list[float] = []

    async def execute(index: int) -> str:
        async with semaphore:
            operation_started_at = time.perf_counter()
            result = await operations[index % len(operations)]()
            latencies.append(time.perf_counter() - operation_started_at)
            return type(result).__name__

    remaining_results = await asyncio.gather(*(execute(index) for index in range(remaining)))
    elapsed = time.perf_counter() - started_at
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    sorted_latencies = sorted(latencies)

    def percentile(fraction: float) -> float | None:
        if not sorted_latencies:
            return None
        index = min(len(sorted_latencies) - 1, int(len(sorted_latencies) * fraction))
        return round(sorted_latencies[index] * 1000, 3)

    summary = {
        "total_operations": total_operations,
        "concurrency": concurrency,
        "elapsed_seconds": round(elapsed, 3),
        "operations_per_second": round(total_operations / elapsed, 2) if elapsed else None,
        "latency_ms_p50": percentile(0.50),
        "latency_ms_p95": percentile(0.95),
        "latency_ms_p99": percentile(0.99),
        "peak_memory_mib": round(peak_memory / (1024 * 1024), 3),
        "auth_calls": transport.auth_calls,
        "request_count": transport.request_count,
        "result_types": dict(
            Counter([type(item).__name__ for item in burst_results] + remaining_results)
        ),
        "endpoint_counts": dict(sorted(transport.endpoint_counts.items())),
    }
    await client.aclose()
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run mock load test for 1000+ SDK operations.")
    parser.add_argument(
        "--operations", type=int, default=1200, help="Total business operations to execute."
    )
    parser.add_argument("--concurrency", type=int, default=100, help="Concurrent operations limit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.operations < 1000:
        raise SystemExit("--operations must be at least 1000")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be positive")

    summary = asyncio.run(run_load_test(args.operations, args.concurrency))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
