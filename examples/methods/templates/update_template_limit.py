"""Изменение лимита шаблона: client.templates.update_template_limit().

Изменить сумму, объём или период лимита шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/update_template_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/update_template_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-3BDYGX5"
LIMIT_ID = "1-3BDZNGO"


async def example(client: APIClient) -> None:
    limit = {
        "product_type": "1-276PF01",
        "sum": {"currency": "810", "value": 7000},
        "time": {"type": 5, "number": 1},
    }
    response = await client.templates.update_template_limit(
        template_id=TEMPLATE_ID, limit_id=LIMIT_ID, limit=limit
    )
    print(f"Лимит обновлён: {response.data}")


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
