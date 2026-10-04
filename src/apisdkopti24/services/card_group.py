from collections.abc import Mapping

from ..errors import RequestValidationError
from ..models import (
    CardGroupAssignmentRequest,
    CardGroupListResponse,
    RemoveCardGroupResponse,
    SetCardGroupResponse,
    SetCardsToGroupResponse,
)
from ..models.request_parts import ContractForm, ContractQuery
from ..operations import operation
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import require_identifier, validate_non_empty_value

GET_CARD_GROUPS = operation("get_card_groups", CardGroupListResponse)
SET_CARD_GROUP = operation("set_card_group", SetCardGroupResponse)
SET_CARDS_TO_GROUP = operation("set_cards_to_group", SetCardsToGroupResponse)
REMOVE_CARD_GROUP = operation("remove_card_group", RemoveCardGroupResponse)


# Сервер принимает имя от 1 до 50 символов (длиннее — 400), а на имя с двоеточием
# отвечает 500 «технические проблемы»; оба случая отклоняются до платного вызова.
_MAX_GROUP_NAME_LENGTH = 50


def _validate_group_name(name: str) -> str:
    group_name = validate_non_empty_value(name, "name")
    if len(group_name) > _MAX_GROUP_NAME_LENGTH:
        raise RequestValidationError(
            f"name: имя группы должно быть не длиннее {_MAX_GROUP_NAME_LENGTH} символов"
        )
    if ":" in group_name:
        raise RequestValidationError("name: двоеточие в имени группы API не принимает")
    return group_name


class CardGroupsService(_BaseService):
    """Методы работы с группами карт (v1)."""

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
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
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
        group_name = _validate_group_name(name)
        cid = await self._resolve_contract_id(contract_id)
        body = {
            **ContractForm.create(cid).model_dump(),
            "name": group_name,
        }
        if group_id is not None:
            body["id"] = require_identifier(group_id, "group_id")
        return await self._request(
            SET_CARD_GROUP,
            api_version=api_version,
            form=body,
            contract_header=cid,
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
            raise RequestValidationError("cards_list должен содержать хотя бы один элемент")
        cid = await self._resolve_contract_id(contract_id)
        assignments = [
            CardGroupAssignmentRequest.model_validate(card).model_dump() for card in cards_list
        ]
        return await self._request(
            SET_CARDS_TO_GROUP,
            api_version=api_version,
            form={
                "contract_id": cid,
                "group_id": require_identifier(group_id, "group_id"),
                "cards_list": to_json_param(assignments),
            },
            contract_header=cid,
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
            form={
                **ContractForm.create(cid).model_dump(),
                "group_id": require_identifier(group_id, "group_id"),
            },
            contract_header=cid,
        )
