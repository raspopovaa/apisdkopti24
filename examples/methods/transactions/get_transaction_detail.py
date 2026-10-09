"""Детали транзакции: client.transactions.get_transaction_detail().

Получить подробности одной транзакции по её ID: точку обслуживания, товар, цену до и
после скидки.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/transactions/get_transaction_detail.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/transactions/get_transaction_detail/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TRANSACTION_ID = "9000000041"


async def example(client: APIClient) -> None:
    response = await client.transactions.get_transaction_detail(transaction_id=TRANSACTION_ID)
    for item in response.data.result or []:
        print(f"{item.product_name}: {item.qty} по {item.price}, скидка {item.discount}")


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
