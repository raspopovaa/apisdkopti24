"""Поиск АЗС (API v2): client.dictionaries.get_azs_list_v2().

Найти торговые точки по фильтрам и строке поиска: адрес, бренд, тип точки, услуги и
цены. Основной метод для поиска АЗС.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/dictionaries/get_azs_list_v2.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/dictionaries/get_azs_list_v2/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.dictionaries.get_azs_list_v2(
        filter={"poi_types": ["AZS"], "countries": ["RUS"]}, q="Поспелиха", page=1, on_page=20
    )
    print(f"Найдено точек: {response.data.total_count}")
    for azs in response.data.result:
        print(f"{azs.id}  {azs.full_name}  {azs.address_full}")


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
