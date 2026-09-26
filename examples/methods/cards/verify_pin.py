"""Запрос кода для сброса PIN: client.cards.verify_pin().

Первый шаг сброса счётчика неверных вводов PIN: сервер отправляет одноразовый код.
Второй шаг — `reset_pin` с этим кодом.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/verify_pin.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/verify_pin/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    response = await client.cards.verify_pin(card_id=CARD_ID)
    if response.data:
        print("Код отправлен. Передайте его в client.cards.reset_pin(card_id=..., code=...)")


async def main() -> None:
    answer = input("Вызов изменяет данные на реальном API. Продолжить? [yes/no] ")
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
