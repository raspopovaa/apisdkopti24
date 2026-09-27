"""Список мобильных профилей карт: client.virtual_cards.get_mpc_qr_list().

Получить выпущенные мобильные профили карт (МПК): на каком устройстве выпущен профиль,
сколько попыток оплаты разрешено и работает ли он.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/get_mpc_qr_list.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/get_mpc_qr_list/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.get_mpc_qr_list()
    for item in response.data.result:
        state = "работает" if item.use_mpc else "отключён"
        print(f"Карта {item.card_id} на устройстве «{item.device_name}» — {state}")


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
