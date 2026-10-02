"""Статистика обращений к API: client.auth.get_info().

Узнать тариф, размер пакета запросов и сколько раз вызывались методы API за месяц или за
день. Помогает следить за расходом тарифицируемых запросов.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/auth/get_info.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/auth/get_info/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
PERIOD = "2026-09"


async def example(client: APIClient) -> None:
    response = await client.auth.get_info(period=PERIOD)
    info = response.data.client_info
    print(f"Тариф: {info.PricePlan}, оплачено запросов: {info.Queries}")
    print(f"Всего вызовов за период: {response.data.methods.all}")


async def main() -> None:
    settings = ConnectionSettings.from_env()
    credentials = EnvironmentCredentialsProvider.from_env()
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        contract_id = os.getenv("API_CONTRACT_ID")
        if contract_id:
            client.select_contract(contract_id=contract_id)
        await example(client)


if __name__ == "__main__":
    asyncio.run(main())
