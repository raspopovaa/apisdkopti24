from typing import Any

from ..models.restrictions import (
    RestrictionGetResponse,
    RestrictionRemoveResponse,
    RestrictionRequestItem,
    RestrictionSetResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import (
    require_identifier,
    validate_card_or_group_target,
    validate_model_sequence,
)

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
        card_id, group_id = validate_card_or_group_target(
            card_id=card_id,
            group_id=group_id,
        )
        params = {"contract_id": cid}
        if card_id is not None:
            params["card_id"] = card_id
        if group_id is not None:
            params["group_id"] = group_id
        return await self._request(
            GET_RESTRICTIONS,
            api_version=api_version,
            params=params,
            request_contract_id=cid,
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
        serialized_restrictions: list[dict[str, Any]] = []
        for item in parsed_restrictions:
            serialized = item.model_dump(by_alias=True, exclude_none=True)
            serialized["contract_id"] = cid
            serialized_restrictions.append(serialized)

        return await self._request(
            SET_RESTRICTION,
            api_version=api_version,
            data={"restriction": to_json_param(serialized_restrictions)},
            request_contract_id=cid,
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
        body = {
            "restriction_id": require_identifier(restriction_id, "restriction_id"),
            "contract_id": cid,
        }
        if group_id is not None:
            body["group_id"] = require_identifier(group_id, "group_id")
        return await self._request(
            REMOVE_RESTRICTION,
            api_version=api_version,
            data=body,
            request_contract_id=cid,
        )
