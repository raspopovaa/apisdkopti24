"""Добавление и удаление карт в группе: client.card_groups.set_cards_to_group().

Добавить карты в группу или убрать их из неё одним запросом. Для каждой карты
указывается действие `Attach` или `Detach`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/card_groups/set_cards_to_group.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/card_groups/set_cards_to_group/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.card_group import CardGroupAssignmentRequest

# Условные значения: замените своими.
GROUP_ID = "1-2656PK1"
ATTACH_CARD_ID = "2728111"
DETACH_CARD_ID = "2728112"


async def example(client: APIClient) -> None:
    cards = [
        CardGroupAssignmentRequest(id=ATTACH_CARD_ID, type="Attach"),
        CardGroupAssignmentRequest(id=DETACH_CARD_ID, type="Detach"),
    ]
    response = await client.card_groups.set_cards_to_group(group_id=GROUP_ID, cards_list=cards)
    print("Состав группы изменён" if response.data else "Сервер не подтвердил изменение")


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
