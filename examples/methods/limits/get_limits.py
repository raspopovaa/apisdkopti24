"""Список продуктовых лимитов: client.limits.get_limits().

Получить лимиты договора, конкретной карты или группы карт: сколько можно потратить и
сколько уже израсходовано за период.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/limits/get_limits.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/limits/get_limits/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "900030"


async def example(client: APIClient) -> None:
    response = await client.limits.get_limits(card_id=CARD_ID)
    for limit in response.data.result or []:
        if limit.amount is not None:
            amount = limit.amount
            print(f"{limit.id}: {amount.used} из {amount.value} {amount.unit}")


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
