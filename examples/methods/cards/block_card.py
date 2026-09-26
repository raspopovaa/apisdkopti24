"""Блокировка и разблокировка карт: client.cards.block_card().

Заблокировать утраченную карту до её замены. Тот же метод с `block=False` разблокирует
карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/block_card.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/block_card/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    AccessDeniedError,
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
)

# Условные значения: замените своими.
CARD_ID = "517945"


async def example(client: APIClient) -> None:
    try:
        response = await client.cards.block_card(card_ids=[CARD_ID], block=True)
    except AccessDeniedError as error:
        print(f"Блокировка запрещена: {error.hint}")
        return
    print(f"Обработаны карты: {', '.join(response.data or [])}")


async def main() -> None:
    answer = input("Пример изменяет данные на реальном API. Продолжить? [yes/no] ")
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
