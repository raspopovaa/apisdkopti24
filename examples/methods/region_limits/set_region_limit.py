"""Установка регионального ограничения: client.region_limits.set_region_limit().

Разрешить карте работать только в одном регионе или запретить конкретную страну, регион
или АЗС.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/region_limits/set_region_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/region_limits/set_region_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.region_limits import RegionLimitRequestItem

# Условные значения: замените своими.
CARD_ID = "2725116"


async def example(client: APIClient) -> None:
    limit = RegionLimitRequestItem(card_id=CARD_ID, country="RUS", region="04", limit_type=1)
    response = await client.region_limits.set_region_limit(region_limits=[limit])
    print(f"ID ограничений: {', '.join(response.data or [])}")


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
