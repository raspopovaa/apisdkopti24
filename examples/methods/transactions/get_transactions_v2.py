"""Транзакции договора за период: client.transactions.get_transactions_v2().

Получить все операции по картам договора за период: дату, АЗС, товар, количество и
сумму. Основной метод для выгрузки расхода.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/transactions/get_transactions_v2.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/transactions/get_transactions_v2/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.transactions.get_transactions_v2(
        date_from="2026-09-01", date_to="2026-09-30", page_limit=100, page_offset=0
    )
    print(f"Транзакций за период: {response.data.total_count}")
    for item in response.data.result:
        print(
            f"{item.timestamp}  карта {item.card_id}  {item.product_name}  {item.qty} × {item.price} = {item.sum}"
        )


async def main() -> None:
    answer = input("Вызов тарифицируется на реальном API. Продолжить? [yes/no] ")
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
