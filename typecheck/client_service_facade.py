from typing import assert_type

from apisdkopti24 import APIClient
from apisdkopti24.services.cards import CardsService


async def load_cards(client: APIClient) -> None:
    assert_type(client.cards, CardsService)
    response = await client.cards.get_cards_v2(page=1, onpage=5)
    print(response.total_count)
