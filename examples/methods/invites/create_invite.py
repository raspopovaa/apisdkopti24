"""Создание приглашения: client.invites.create_invite().

Пригласить водителя или другого пользователя зарегистрироваться. Приглашение уходит по
SMS или email; ссылку из ответа можно отправить и самостоятельно.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/invites/create_invite.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/invites/create_invite/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.invites import InviteCreateRequest

# Условные значения: замените своими.
CONTRACT_ID = "1-T000025"


async def example(client: APIClient) -> None:
    request = InviteCreateRequest(
        role="Driver", mobile="79990000000", contracts=[{"id": CONTRACT_ID}]
    )
    response = await client.invites.create_invite(data=request, with_send=True)
    print(f"Приглашение {response.data.id}: {response.data.url}")


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
