"""Водители карты: client.cards.get_card_drivers().

Получить пользователей (водителей), которым доступна карта.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_card_drivers.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_card_drivers/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    response = await client.cards.get_card_drivers(card_id=CARD_ID)
    print(f"Водителей: {response.total_count}")
    for driver in response.result:
        print(f"{driver.id}  {driver.last_name} {driver.first_name}  роль: {driver.role}")


async def main() -> None:
    answer = input("Вызов тарифицируется на реальном API. Продолжить? [yes/no] ")
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
