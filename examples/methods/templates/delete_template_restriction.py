"""Удаление товарного ограничителя шаблона: client.templates.delete_template_restriction().

Удалить товарный ограничитель из шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/delete_template_restriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/delete_template_restriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000043"
RESTRICTION_ID = "1-T000047"


async def example(client: APIClient) -> None:
    response = await client.templates.delete_template_restriction(
        template_id=TEMPLATE_ID, restriction_id=RESTRICTION_ID
    )
    print("Ограничитель удалён" if response.data else "Сервер не подтвердил удаление")


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
