"""Платёжная строка для оплаты по QR: client.virtual_cards.generate_payment_qr().

Получить платёжную строку по мобильному профилю карты. Приложение водителя показывает её
как QR-код на кассе АЗС.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/generate_payment_qr.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/generate_payment_qr/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "90000008"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.generate_payment_qr(card_id=CARD_ID, pin="4815")
    qr = response.data
    print(f"Строка действует до {qr.end_date}, попыток оплаты: {qr.tries}")


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
