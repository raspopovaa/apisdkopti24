"""Добавление лимита в шаблон: client.templates.create_template_limit().

Добавить лимит в шаблон: например, не больше 5000 рублей на бензин в месяц.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/create_template_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/create_template_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.templates import TemplateLimitCreateRequest

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000042"


async def example(client: APIClient) -> None:
    payload = TemplateLimitCreateRequest(
        product_type="1-276PF01",
        sum={"currency": "810", "value": 5000},
        time={"type": 5, "number": 1},
    )
    response = await client.templates.create_template_limit(
        template_id=TEMPLATE_ID, payload=payload
    )
    print(f"ID лимита: {response.data}")


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
