"""Привязка договоров к пользователю: client.users.attach_contracts().

Закрепить пользователя за договорами, указать шаблон виртуальной карты и разрешить
выпуск мобильного профиля карты (МПК).

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/users/attach_contracts.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/users/attach_contracts/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.users import UserAttachContractRequest

# Условные значения: замените своими.
USER_ID = "1-T000066"
CONTRACT_ID = "1-T000036"


async def example(client: APIClient) -> None:
    contracts = [UserAttachContractRequest(sid=CONTRACT_ID, use_mpc=True)]
    response = await client.users.attach_contracts(user_id=USER_ID, contracts=contracts)
    print("Договоры привязаны" if response.data else "Сервер не подтвердил привязку")


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
