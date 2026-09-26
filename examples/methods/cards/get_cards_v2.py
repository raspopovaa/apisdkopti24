"""Список карт договора (API v2): client.cards.get_cards_v2().

Получить первую страницу активных карт договора и вывести номер, статус и группу каждой
карты. Это основной метод для списков карт: он поддерживает фильтры, поиск и пагинацию.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_cards_v2.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_cards_v2/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.cards.get_cards_v2(status="Active", page=1, onpage=20)
    print(f"Найдено карт: {response.total_count}")
    for card in response.result:
        print(f"{card.id}  {card.number}  {card.status_name}  группа: {card.group_name}")


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
