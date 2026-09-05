from collections.abc import AsyncIterator

from ..models.cards import (
    BoolResponse,
    CardDetailResponse,
    CardDriversResponse,
    CardGroupResponse,
    CardsListResponse,
    CardsV2Response,
    CardV2Item,
    IDListResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import (
    require_identifier,
    validate_identifier_list,
    validate_non_empty_value,
    validate_positive_count,
)

GET_CARDS_V1 = operation("get_cards_v1", CardsListResponse)
GET_CARDS_V2 = operation("get_cards_v2", CardsV2Response)
GET_CARDS_BY_GROUP = operation("get_cards_by_group", CardGroupResponse)
GET_CARD_DRIVERS = operation("get_card_drivers", CardDriversResponse)
GET_CARD_DETAIL = operation("get_card_detail", CardDetailResponse)
BLOCK_CARD = operation("block_card", IDListResponse)
SET_CARD_COMMENT = operation("set_card_comment", BoolResponse)
VERIFY_PIN = operation("verify_pin", BoolResponse)
RESET_PIN = operation("reset_pin", BoolResponse)


class CardsService(_BaseService):
    """Methods for fuel cards."""

    async def get_cards_v1(
        self,
        *,
        contract_id: str | None = None,
        cache: bool = True,
        api_version: str | None = None,
    ) -> CardsListResponse:
        """Получить карты договора через API v1."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARDS_V1,
            api_version=api_version,
            params={"contract_id": cid, "cache": str(cache).lower()},
            request_contract_id=cid,
        )

    async def get_cards_v2(
        self,
        *,
        contract_id: str | None = None,
        sort: str = "-id",
        q: str | None = None,
        status: str | None = None,
        carrier: str | None = None,
        platon: bool | None = None,
        avtodor: bool | None = None,
        users: bool | None = None,
        group_id: str | None = None,
        page: int | None = None,
        onpage: int | None = None,
        api_version: str | None = None,
    ) -> CardsV2Response:
        """Получить страницу карт договора через API v2."""
        cid = await self._resolve_contract_id(contract_id)
        normalized_group = (
            require_identifier(group_id, "group_id") if group_id is not None else None
        )
        if page is not None:
            validate_positive_count(page)
        if onpage is not None:
            validate_positive_count(onpage)
        params = {
            "contract_id": cid,
            "sort": validate_non_empty_value(sort, "sort"),
            "q": q,
            "status": status,
            "carrier": carrier,
            "platon": platon,
            "avtodor": avtodor,
            "users": users,
            "group_id": normalized_group,
            "page": page,
            "onpage": onpage,
        }
        return await self._request(
            GET_CARDS_V2,
            api_version=api_version,
            params={key: value for key, value in params.items() if value is not None},
            request_contract_id=cid,
        )

    async def iter_cards_v2(
        self,
        *,
        contract_id: str | None = None,
        sort: str = "-id",
        q: str | None = None,
        status: str | None = None,
        carrier: str | None = None,
        group_id: str | None = None,
        onpage: int = 100,
        max_pages: int = 100,
        api_version: str | None = None,
    ) -> AsyncIterator[CardV2Item]:
        """Последовательно получить карты v2 с ограничением числа страниц."""
        validate_positive_count(onpage)
        validate_positive_count(max_pages)
        yielded = 0
        for page in range(1, max_pages + 1):
            response = await self.get_cards_v2(
                contract_id=contract_id,
                sort=sort,
                q=q,
                status=status,
                carrier=carrier,
                group_id=group_id,
                page=page,
                onpage=onpage,
                api_version=api_version,
            )
            for item in response.result:
                yield item
                yielded += 1
            if not response.result or yielded >= response.total_count:
                return

    async def get_cards_by_group(
        self,
        *,
        group_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> CardGroupResponse:
        """Получить карты выбранной группы."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARDS_BY_GROUP,
            api_version=api_version,
            params={"contract_id": cid, "group_id": require_identifier(group_id, "group_id")},
            request_contract_id=cid,
        )

    async def get_card_drivers(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> CardDriversResponse:
        """Получить пользователей, привязанных к карте."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARD_DRIVERS,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            params={"contract_id": cid},
            request_contract_id=cid,
        )

    async def get_card_detail(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> CardDetailResponse:
        """Получить детальную информацию о карте."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARD_DETAIL,
            api_version=api_version,
            params={"contract_id": cid, "card_id": require_identifier(card_id, "card_id")},
            request_contract_id=cid,
        )

    async def block_card(
        self,
        *,
        card_ids: list[str],
        contract_id: str | None = None,
        block: bool = True,
        api_version: str | None = None,
    ) -> IDListResponse:
        """Заблокировать или разблокировать список карт.

        Типовой сценарий:
            Немедленно заблокировать утраченную карту до её замены.

        Пример:
            ``await client.cards.block_card(card_ids=["card-id"], block=True)``
        """
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            BLOCK_CARD,
            api_version=api_version,
            data={
                "contract_id": cid,
                "card_id": validate_identifier_list(card_ids, "card_ids"),
                "block": str(block).lower(),
            },
            request_contract_id=cid,
        )

    async def set_card_comment(
        self,
        *,
        card_id: str,
        comment: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> BoolResponse:
        """Установить комментарий для карты."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            SET_CARD_COMMENT,
            api_version=api_version,
            data={
                "card_id": require_identifier(card_id, "card_id"),
                "contract_id": cid,
                "comment": validate_non_empty_value(comment, "comment"),
            },
            request_contract_id=cid,
        )

    async def verify_pin(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> BoolResponse:
        """Запросить проверочный код для сброса PIN карты."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            VERIFY_PIN,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            params={"contract_id": cid},
            request_contract_id=cid,
        )

    async def reset_pin(
        self,
        *,
        card_id: str,
        code: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> BoolResponse:
        """Сбросить PIN карты по проверочному коду."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            RESET_PIN,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            data={"contract_id": cid, "code": validate_non_empty_value(code, "code")},
            request_contract_id=cid,
        )
