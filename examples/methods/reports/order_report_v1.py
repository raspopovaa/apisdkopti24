"""Заказ транзакционного отчёта (API v1): client.reports.order_report_v1().

Заказать транзакционный отчёт за период по договору, списку карт или группам карт через
первую версию API.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/reports/order_report_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/reports/order_report_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CONTRACT_ID = "1-T000025"


async def example(client: APIClient) -> None:
    response = await client.reports.order_report_v1(
        contract_id=CONTRACT_ID,
        start="2026-09-01",
        end="2026-09-30",
        report_format="xlsx",
        email="accounting@example.org",
    )
    print(f"Задачи отчёта: {', '.join(response.data or [])}")


async def main() -> None:
    answer = input("Вызов изменяет данные и тарифицируется на реальном API. Продолжить? [yes/no] ")
    if answer.strip().lower() != "yes":
        return
    settings = ConnectionSettings.from_env()
    credentials = EnvironmentCredentialsProvider.from_env()
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        contract_id = os.getenv("API_CONTRACT_ID")
        if contract_id:
            client.select_contract(contract_id=contract_id)
        await example(client)


if __name__ == "__main__":
    asyncio.run(main())
