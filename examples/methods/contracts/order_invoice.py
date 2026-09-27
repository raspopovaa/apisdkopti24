"""Заказ счёта на оплату: client.contracts.order_invoice().

Сформировать счёт на пополнение договора на заданную сумму и отправить его на email.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/order_invoice.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/order_invoice/
"""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
AMOUNT = Decimal("50000.00")
EMAIL = "billing@example.org"


async def example(client: APIClient) -> None:
    response = await client.contracts.order_invoice(amount=AMOUNT, email=EMAIL)
    print("Счёт заказан" if response.data else "Сервер не подтвердил заказ")


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
