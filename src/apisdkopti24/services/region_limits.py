from ..models.region_limits import (
    RegionLimitRequestItem,
    RegionLimitResponse,
    RegionLimitSetResponse,
    RemoveRegionLimit,
)
from ..operations import operation
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import validate_card_or_group_target, validate_model_sequence
from ._shared import (
    removal_form,
    serialize_contract_items,
    target_query,
    with_normalized_targets,
)

GET_REGION_LIMITS = operation("get_region_limits", RegionLimitResponse)
SET_REGION_LIMIT = operation("set_region_limit", RegionLimitSetResponse)
REMOVE_REGION_LIMIT = operation("remove_region_limit", RemoveRegionLimit)


class RegionLimitsService(_BaseService):
    """Методы работы с региональными ограничениями (v1)."""

    async def get_region_limits(
        self,
        *,
        contract_id: str | None = None,
        card_id: str | None = None,
        group_id: str | None = None,
    ) -> RegionLimitResponse:
        """Получить региональные лимиты договора, карты или группы карт.

        Операция ``GET_REGION_LIMITS``. Договор: явный ``contract_id`` или договор сессии.
        Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param card_id: Идентификатор топливной карты.
        :param group_id: Идентификатор группы топливных карт.
        :return: ``RegionLimitResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        card_id, group_id = validate_card_or_group_target(card_id=card_id, group_id=group_id)
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_REGION_LIMITS,
            query=target_query(contract_id=cid, card_id=card_id, group_id=group_id),
            contract_header=cid,
        )

    async def set_region_limit(
        self,
        *,
        region_limits: list[RegionLimitRequestItem],
        contract_id: str | None = None,
    ) -> RegionLimitSetResponse:
        """Создать или изменить региональные лимиты одного договора (операция ``SET_REGION_LIMIT``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Типовой сценарий:
            Разрешить обслуживание карты только в выбранных регионах.

        Пример:
            ``await client.region_limits.set_region_limit(region_limits=[item])``

        :param region_limits: Массив параметров регионального лимита: ID лимита, карты, группы и
            договора, страна, регион, АЗС, партнёр и ``limit_type`` (``1`` — разрешающий, ``2``
            — запрещающий).
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``RegionLimitSetResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        parsed_limits = with_normalized_targets(
            validate_model_sequence(region_limits, RegionLimitRequestItem, "region_limits")
        )

        cid = await self._resolve_batch_contract_id(
            contract_id=contract_id,
            item_contract_ids=[item.contract_id for item in parsed_limits],
        )
        serialized_limits = serialize_contract_items(parsed_limits, contract_id=cid)

        return await self._request(
            SET_REGION_LIMIT,
            form={"region_limit": to_json_param(serialized_limits)},
            contract_header=cid,
        )

    async def remove_region_limit(
        self,
        *,
        contract_id: str | None = None,
        regionlimit_id: str,
        group_id: str | None = None,
    ) -> RemoveRegionLimit:
        """Удалить региональный лимит карты или группы карт (операция ``REMOVE_REGION_LIMIT``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param regionlimit_id: ID регионального лимита.
        :param group_id: Идентификатор группы топливных карт.
        :return: ``RemoveRegionLimit``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        form = removal_form(
            identifier_name="regionlimit_id",
            identifier=regionlimit_id,
            group_id=group_id,
        )
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            REMOVE_REGION_LIMIT,
            form={**form, "contract_id": cid},
            contract_header=cid,
        )
