"""Установка продуктового лимита: client.limits.set_limit().

Ограничить расход по карте: например, не больше 100 литров топлива в сутки. Тот же метод
с `id` существующего лимита изменяет его.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/limits/set_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/limits/set_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.limits import LimitRequestItem

# Условные значения: замените своими.
CARD_ID = "900030"
FUEL_GROUP = "1-CK235"
FUEL_TYPE = "1-CK231"


async def example(client: APIClient) -> None:
    limit = LimitRequestItem.model_validate(
        {
            "card_id": CARD_ID,
            "productGroup": FUEL_GROUP,
            "productType": FUEL_TYPE,
            "amount": {"value": 100, "unit": "LIT"},
            "time": {"number": 1, "type": 3},
        }
    )
    response = await client.limits.set_limit(limits=[limit])
    print(f"ID лимитов: {', '.join(response.data or [])}")


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
