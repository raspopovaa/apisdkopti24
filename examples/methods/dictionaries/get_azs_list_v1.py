"""Список АЗС (API v1): client.dictionaries.get_azs_list_v1().

Получить торговые точки через первую версию API: с терминалами, ценами и услугами. Для
новых интеграций удобнее `get_azs_list_v2`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/dictionaries/get_azs_list_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/dictionaries/get_azs_list_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.dictionaries.get_azs_list_v1(
        page=1, onpage=10, filter={"country": ["RUS"], "region": ["40"]}
    )
    if response.data is None:
        print("Сервер не вернул данные")
        return
    for azs in response.data.result or []:
        print(f"{azs.id}  {azs.type}  регион {azs.regionCode}  {azs.belongsTo}")


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
