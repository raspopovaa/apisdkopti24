"""Сброс счётчика неверных вводов PIN: client.cards.reset_pin().

Второй шаг сброса: подтвердить операцию кодом из письма, которое пришло после
`verify_pin`. После этого пластиковой картой снова можно пользоваться на АЗС с PIN.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/reset_pin.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/reset_pin/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    ValidationError,
)

# Условные значения: замените своими.
CARD_ID = "382359"
CODE = "123456"


async def example(client: APIClient) -> None:
    try:
        response = await client.cards.reset_pin(card_id=CARD_ID, code=CODE)
    except ValidationError:
        print("Код неверный или устарел: запросите новый через verify_pin")
        return
    print("Счётчик сброшен" if response.data else "Сервер не подтвердил сброс")


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
