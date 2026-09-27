"""Установка товарного ограничителя: client.restrictions.set_restriction().

Разрешить карте покупать только топливо или запретить определённые товары.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/restrictions/set_restriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/restrictions/set_restriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.restrictions import RestrictionRequestItem

# Условные значения: замените своими.
CARD_ID = "2748116"
FUEL_TYPE = "1-CK231"


async def example(client: APIClient) -> None:
    restriction = RestrictionRequestItem.model_validate(
        {"card_id": CARD_ID, "productType": FUEL_TYPE, "restriction_type": 1}
    )
    response = await client.restrictions.set_restriction(restrictions=[restriction])
    print(f"ID ограничителей: {', '.join(response.data or [])}")


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
