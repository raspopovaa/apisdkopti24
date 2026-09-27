"""Изменение географического ограничения шаблона: client.templates.update_template_georestriction().

Изменить страну, регион или вид географического ограничения шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/update_template_georestriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/update_template_georestriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-3BDZMRJ"
GEORESTRICTION_ID = "1-3BE55MK"


async def example(client: APIClient) -> None:
    response = await client.templates.update_template_georestriction(
        template_id=TEMPLATE_ID,
        georestriction_id=GEORESTRICTION_ID,
        payload={"country": "RUS", "region": "50", "restriction_type": 1},
    )
    print(f"Ограничение обновлено: {response.data}")


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
