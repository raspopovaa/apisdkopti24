"""Выпуск мобильного профиля карты: client.virtual_cards.init_mpc().

Первый шаг выпуска МПК на устройстве водителя: задать PIN профиля и устройство. Затем
профиль подтверждается кодом из SMS через `confirm_mpc`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/init_mpc.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/init_mpc/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "90000008"
USER_ID = "1-T000023"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.init_mpc(
        card_id=CARD_ID,
        user_id=USER_ID,
        pin="4815",
        device_id="device-example",
        device_name="Pixel Example",
    )
    print("Код подтверждения отправлен по SMS" if response.data else "Выпуск не начат")


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
