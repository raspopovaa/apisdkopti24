"""Пополнение кошелька карты: client.ewallet.move_to_card().

Перевести деньги с договора на кошелёк карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/ewallet/move_to_card.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/ewallet/move_to_card/
"""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "90000003"
AMOUNT = Decimal("500.00")


async def example(client: APIClient) -> None:
    response = await client.ewallet.move_to_card(card_id=CARD_ID, amount=AMOUNT)
    print("Перевод выполнен" if response.data else "Сервер не подтвердил перевод")


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
