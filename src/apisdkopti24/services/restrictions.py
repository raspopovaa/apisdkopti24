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
from ._shared import removal_form, serialize_contract_items, target_query

GET_RESTRICTIONS = operation("get_restrictions", RestrictionGetResponse)
SET_RESTRICTION = operation("set_restriction", RestrictionSetResponse)
REMOVE_RESTRICTION = operation("remove_restriction", RestrictionRemoveResponse)


class RestrictionsService(_BaseService):
    """Methods for product restrictions (v1)."""

    async def get_restrictions(
        self,
        *,
        contract_id: str | None = None,
        card_id: str | None = None,
        group_id: str | None = None,
        api_version: str | None = None,
    ) -> RestrictionGetResponse:
        """Получить товарные ограничители договора, карты или группы карт."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_RESTRICTIONS,
            api_version=api_version,
            query=target_query(contract_id=cid, card_id=card_id, group_id=group_id),
            contract_header=cid,
        )

    async def set_restriction(
        self,
        *,
        restrictions: list[RestrictionRequestItem],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> RestrictionSetResponse:
        """Создать или изменить товарные ограничители одного договора.

        Типовой сценарий:
            Запретить оплату отдельных категорий товаров по карте или группе карт.

        Пример:
            ``await client.restrictions.set_restriction(restrictions=[item])``
        """
        parsed_restrictions = validate_model_sequence(
            restrictions,
            RestrictionRequestItem,
            "restrictions",
        )
        for item in parsed_restrictions:
            validate_card_or_group_target(
                card_id=item.card_id,
                group_id=item.group_id,
                required=True,
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
            api_version=api_version,
            form={"restriction": to_json_param(serialized_restrictions)},
            contract_header=cid,
        )

    async def remove_restriction(
        self,
        *,
        contract_id: str | None = None,
        restriction_id: str,
        group_id: str | None = None,
        api_version: str | None = None,
    ) -> RestrictionRemoveResponse:
        """Удалить товарный ограничитель карты или группы карт."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            REMOVE_RESTRICTION,
            api_version=api_version,
            form=removal_form(
                identifier_name="restriction_id",
                identifier=restriction_id,
                contract_id=cid,
                group_id=group_id,
            ),
            contract_header=cid,
        )
