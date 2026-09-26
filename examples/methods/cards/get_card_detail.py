"""Сведения о карте: client.cards.get_card_detail().

Получить подробную информацию об одной карте: статус, способ авторизации, дату
последнего использования, срок действия и настройки таймаута операций.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_card_detail.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_card_detail/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    NotFoundError,
)

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    try:
        response = await client.cards.get_card_detail(card_id=CARD_ID)
    except NotFoundError:
        print("Карта не найдена: проверьте CARD_ID и выбранный договор")
        return
    for card in response.data.result:
        print(f"Карта {card.number}: статус {card.status}")
        print(f"Последнее использование: {card.date_last_usage}")


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
