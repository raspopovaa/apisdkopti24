"""Лимиты шаблона: client.templates.get_template_limits().

Получить лимиты, которые получат карты, выпущенные по шаблону.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/get_template_limits.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/get_template_limits/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000043"


async def example(client: APIClient) -> None:
    response = await client.templates.get_template_limits(template_id=TEMPLATE_ID)
    for limit in response.data.result:
        if limit.amount is not None:
            print(f"{limit.id}: {limit.productTypeName} — {limit.amount.value} {limit.amount.unit}")


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
