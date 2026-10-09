"""Список пользователей: client.users.get_users().

Получить пользователей клиента с ролью, контактами и признаком активности. Поддерживает
поиск, фильтр и пагинацию.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/users/get_users.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/users/get_users/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.users.get_users(
        filter={"role": "Driver", "active": True}, page=1, on_page=20
    )
    if response.data is None:
        print("Сервер не вернул данные")
        return
    print(f"Пользователей: {response.data.total_count}")
    for user in response.data.result or []:
        print(f"{user.id}  {user.last_name} {user.first_name}  роль: {user.role.name}")


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
