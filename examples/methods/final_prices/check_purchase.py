"""Проверка возможности покупки: client.final_prices.check_purchase().

Проверить до поездки, пройдёт ли покупка набора товаров по карте на выбранной АЗС:
хватит ли лимитов и не запрещены ли товары ограничителями.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/final_prices/check_purchase.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/final_prices/check_purchase/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "989666"
POI_ID = "366038"


async def example(client: APIClient) -> None:
    goods = [{"code": "00000000000007", "quantity": 40, "price": 54.35}]
    response = await client.final_prices.check_purchase(card_id=CARD_ID, poi_id=POI_ID, goods=goods)
    print("Покупка возможна" if response.data else "Покупка не пройдёт")


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
