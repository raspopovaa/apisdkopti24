"""Отправка документов на email: client.contracts.order_documents_email().

Отправить выбранные документы в PDF или XLSX на один или несколько адресов.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/order_documents_email.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/order_documents_email/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
DOCUMENT_ID = "6fffd550-b55f-11e9-8123-005056a969a3"


async def example(client: APIClient) -> None:
    response = await client.contracts.order_documents_email(
        ids=[DOCUMENT_ID], fmt="pdf", emails=["accounting@example.org"]
    )
    print("Документы отправлены" if response.data else "Сервер не подтвердил отправку")


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
