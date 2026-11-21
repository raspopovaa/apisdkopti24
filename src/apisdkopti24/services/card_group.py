from collections.abc import Mapping, Sequence

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


# Сервер принимает имя от 1 до 50 символов (длиннее: 400), а на имя с двоеточием
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
    ) -> CardGroupListResponse:
        """Получить группы карт выбранного договора (операция ``GET_CARD_GROUPS``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``CardGroupListResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARD_GROUPS,
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
        )

    async def set_card_group(
        self,
        *,
        name: str,
        contract_id: str | None = None,
        group_id: str | None = None,
    ) -> SetCardGroupResponse:
        """Создать группу карт или изменить существующую (операция ``SET_CARD_GROUP``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Типовой сценарий:
            Создать группу для подразделения, затем добавить карты через
            ``set_cards_to_group``.

        Пример:
            ``await client.card_groups.set_card_group(name="Служебные автомобили")``

        :param name: Имя группы карт.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param group_id: Идентификатор группы топливных карт.
        :return: ``SetCardGroupResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        group_name = _validate_group_name(name)
        wire_group_id = require_identifier(group_id, "group_id") if group_id is not None else None
        cid = await self._resolve_contract_id(contract_id)
        body = {
            **ContractForm.create(cid).model_dump(),
            "name": group_name,
        }
        if wire_group_id is not None:
            body["id"] = wire_group_id
        return await self._request(
            SET_CARD_GROUP,
            form=body,
            contract_header=cid,
        )

    async def set_cards_to_group(
        self,
        *,
        group_id: str,
        cards_list: Sequence[CardGroupAssignmentRequest | Mapping[str, object]],
        contract_id: str | None = None,
    ) -> SetCardsToGroupResponse:
        """Добавить карты в группу или удалить их из группы (операция ``SET_CARDS_TO_GROUP``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param group_id: Идентификатор группы топливных карт.
        :param cards_list: Список карт договора, добавляемых в группу или удаляемых из неё.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``SetCardsToGroupResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        if not cards_list:
            raise RequestValidationError("cards_list должен содержать хотя бы один элемент")
        wire_group_id = require_identifier(group_id, "group_id")
        assignments = [
            CardGroupAssignmentRequest.model_validate(card).model_dump() for card in cards_list
        ]
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            SET_CARDS_TO_GROUP,
            form={
                "contract_id": cid,
                "group_id": wire_group_id,
                "cards_list": to_json_param(assignments),
            },
            contract_header=cid,
        )

    async def remove_card_group(
        self,
        *,
        group_id: str,
        contract_id: str | None = None,
    ) -> RemoveCardGroupResponse:
        """Удалить группу карт (операция ``REMOVE_CARD_GROUP``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param group_id: Идентификатор группы топливных карт.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``RemoveCardGroupResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_group_id = require_identifier(group_id, "group_id")
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            REMOVE_CARD_GROUP,
            form={
                **ContractForm.create(cid).model_dump(),
                "group_id": wire_group_id,
            },
            contract_header=cid,
        )
