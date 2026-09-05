import json
from collections.abc import Mapping

from ..models import (
    CardGroupAssignmentRequest,
    CardGroupListResponse,
    RemoveCardGroupResponse,
    SetCardGroupResponse,
    SetCardsToGroupResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import require_identifier, validate_non_empty_value

GET_CARD_GROUPS = operation("get_card_groups", CardGroupListResponse)
SET_CARD_GROUP = operation("set_card_group", SetCardGroupResponse)
SET_CARDS_TO_GROUP = operation("set_cards_to_group", SetCardsToGroupResponse)
REMOVE_CARD_GROUP = operation("remove_card_group", RemoveCardGroupResponse)


class CardGroupsService(_BaseService):
    """Methods for card groups (v1)."""

    async def get_card_groups(
        self,
        *,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> CardGroupListResponse:
        """Получить группы карт выбранного договора."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARD_GROUPS,
            api_version=api_version,
            params={"contract_id": cid},
            request_contract_id=cid,
        )

    async def set_card_group(
        self,
        *,
        name: str,
        contract_id: str | None = None,
        group_id: str | None = None,
        api_version: str | None = None,
    ) -> SetCardGroupResponse:
        """Создать группу карт или изменить существующую.

        Типовой сценарий:
            Создать группу для подразделения, затем добавить карты через
            ``set_cards_to_group``.

        Пример:
            ``await client.card_groups.set_card_group(name="Служебные автомобили")``
        """
        cid = await self._resolve_contract_id(contract_id)
        body = {
            "contract_id": cid,
            "name": validate_non_empty_value(name, "name"),
        }
        if group_id is not None:
            body["id"] = require_identifier(group_id, "group_id")
        return await self._request(
            SET_CARD_GROUP,
            api_version=api_version,
            data=body,
            request_contract_id=cid,
        )

    async def set_cards_to_group(
        self,
        *,
        group_id: str,
        cards_list: list[CardGroupAssignmentRequest | Mapping[str, object]],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> SetCardsToGroupResponse:
        """Добавить карты в группу или удалить их из группы."""
        if not cards_list:
            raise ValueError("cards_list must contain at least one item")
        cid = await self._resolve_contract_id(contract_id)
        assignments = [
            CardGroupAssignmentRequest.model_validate(card).model_dump() for card in cards_list
        ]
        return await self._request(
            SET_CARDS_TO_GROUP,
            api_version=api_version,
            data={
                "contract_id": cid,
                "group_id": require_identifier(group_id, "group_id"),
                "cards_list": json.dumps(assignments),
            },
            request_contract_id=cid,
        )

    async def remove_card_group(
        self,
        *,
        group_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> RemoveCardGroupResponse:
        """Удалить группу карт."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            REMOVE_CARD_GROUP,
            api_version=api_version,
            data={"contract_id": cid, "group_id": require_identifier(group_id, "group_id")},
            request_contract_id=cid,
        )
