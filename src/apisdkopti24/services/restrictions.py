from ..models.restrictions import (
    RestrictionGetResponse,
    RestrictionRemoveResponse,
    RestrictionRequestItem,
    RestrictionSetResponse,
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

GET_RESTRICTIONS = operation("get_restrictions", RestrictionGetResponse)
SET_RESTRICTION = operation("set_restriction", RestrictionSetResponse)
REMOVE_RESTRICTION = operation("remove_restriction", RestrictionRemoveResponse)


class RestrictionsService(_BaseService):
    """Методы работы с ограничителями товаров и услуг (v1)."""

    async def get_restrictions(
        self,
        *,
        contract_id: str | None = None,
        card_id: str | None = None,
        group_id: str | None = None,
    ) -> RestrictionGetResponse:
        """Получить товарные ограничители договора, карты или группы карт.

        Операция ``GET_RESTRICTIONS``. Договор: явный ``contract_id`` или договор сессии.
        Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param card_id: Идентификатор топливной карты.
        :param group_id: Идентификатор группы топливных карт.
        :return: ``RestrictionGetResponse``, данные в ``response.data``.
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
            GET_RESTRICTIONS,
            query=target_query(contract_id=cid, card_id=card_id, group_id=group_id),
            contract_header=cid,
        )

    async def set_restriction(
        self,
        *,
        restrictions: list[RestrictionRequestItem],
        contract_id: str | None = None,
    ) -> RestrictionSetResponse:
        """Создать или изменить товарные ограничители одного договора.

        Операция ``SET_RESTRICTION``. Договор: явный ``contract_id`` или договор сессии.
        Аргументы проверяются до сети.

        Типовой сценарий:
            Запретить оплату отдельных категорий товаров по карте или группе карт.

        Пример:
            ``await client.restrictions.set_restriction(restrictions=[item])``

        :param restrictions: Массив параметров товарного ограничителя: ID ограничителя, карты,
            группы и договора, группа и тип продукта, а также ``restriction_type`` (``1`` —
            разрешающий, ``2`` — запрещающий).
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``RestrictionSetResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        parsed_restrictions = with_normalized_targets(
            validate_model_sequence(restrictions, RestrictionRequestItem, "restrictions")
        )

        cid = await self._resolve_batch_contract_id(
            contract_id=contract_id,
            item_contract_ids=[item.contract_id for item in parsed_restrictions],
        )
        serialized_restrictions = serialize_contract_items(
            parsed_restrictions,
            contract_id=cid,
        )

        return await self._request(
            SET_RESTRICTION,
            form={"restriction": to_json_param(serialized_restrictions)},
            contract_header=cid,
        )

    async def remove_restriction(
        self,
        *,
        contract_id: str | None = None,
        restriction_id: str,
        group_id: str | None = None,
    ) -> RestrictionRemoveResponse:
        """Удалить товарный ограничитель карты или группы карт (операция ``REMOVE_RESTRICTION``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param restriction_id: ID товарного ограничителя.
        :param group_id: Идентификатор группы топливных карт.
        :return: ``RestrictionRemoveResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        form = removal_form(
            identifier_name="restriction_id",
            identifier=restriction_id,
            group_id=group_id,
        )
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            REMOVE_RESTRICTION,
            form={**form, "contract_id": cid},
            contract_header=cid,
        )
