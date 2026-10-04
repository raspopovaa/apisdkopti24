"""Авторизация и выбор договора: client.auth.auth_user().

Войти в API и выбрать договор, с которым будут работать остальные методы. Обычно этот
метод вызывать не нужно: SDK авторизуется сам при первом запросе. Явный вызов полезен,
чтобы получить список договоров и данные пользователя.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/auth/auth_user.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/auth/auth_user/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    ContractSelectionError,
    EnvironmentCredentialsProvider,
)

# Условные значения: замените своими.
CONTRACT_ID = "1-T000025"


async def example(client: APIClient) -> None:
    try:
        response = await client.auth.auth_user(contract_id=CONTRACT_ID)
    except ContractSelectionError as error:
        print("Договор не найден. Доступные договоры:")
        for contract_id, number in error.available_contracts:
            print(f"  {contract_id}  {number}")
        return
    print(f"Организация: {response.data.org_name}")
    for contract in response.data.contracts:
        print(f"Договор {contract.number} ({contract.id}), карт: {contract.cards_count}")


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
