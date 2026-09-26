"""Карты группы: client.cards.get_cards_by_group().

Получить карты, входящие в группу карт договора.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_cards_by_group.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_cards_by_group/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
GROUP_ID = "1-CRPDCT2"


async def example(client: APIClient) -> None:
    response = await client.cards.get_cards_by_group(group_id=GROUP_ID)
    for card in response.data.result:
        print(f"{card.id}  {card.number}  {card.status}")


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
