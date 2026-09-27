"""Итоговая цена товаров на АЗС: client.final_prices.get_final_prices().

Узнать, сколько будет стоить литр топлива по карте на выбранной АЗС с учётом тарифа
договора, лимитов и ограничителей карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/final_prices/get_final_prices.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/final_prices/get_final_prices/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "989666"
POI_ID = "366038"


async def example(client: APIClient) -> None:
    response = await client.final_prices.get_final_prices(
        card_id=CARD_ID, poi_id=POI_ID, goods=["00000000000007", "00000000000009"]
    )
    for item in response.data.goods:
        print(f"{item.code}: {item.price}")


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
