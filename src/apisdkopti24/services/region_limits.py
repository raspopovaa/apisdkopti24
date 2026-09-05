from typing import Any

from ..models.region_limits import (
    RegionLimitRequestItem,
    RegionLimitResponse,
    RegionLimitSetResponse,
    RemoveRegionLimit,
)
from ..operations import operation
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import (
    require_identifier,
    validate_card_or_group_target,
    validate_model_sequence,
)

GET_REGION_LIMITS = operation("get_region_limits", RegionLimitResponse)
SET_REGION_LIMIT = operation("set_region_limit", RegionLimitSetResponse)
REMOVE_REGION_LIMIT = operation("remove_region_limit", RemoveRegionLimit)


class RegionLimitsService(_BaseService):
    """Methods for regional limits (v1)."""

    async def get_region_limits(
        self,
        *,
        contract_id: str | None = None,
        card_id: str | None = None,
        group_id: str | None = None,
        api_version: str | None = None,
    ) -> RegionLimitResponse:
        """Получить региональные лимиты договора, карты или группы карт."""
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
            GET_REGION_LIMITS,
            api_version=api_version,
            params=params,
            request_contract_id=cid,
        )

    async def set_region_limit(
        self,
        *,
        region_limits: list[RegionLimitRequestItem],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> RegionLimitSetResponse:
        """Создать или изменить региональные лимиты одного договора.

        Типовой сценарий:
            Разрешить обслуживание карты только в выбранных регионах.

        Пример:
            ``await client.region_limits.set_region_limit(region_limits=[item])``
        """
        parsed_limits = validate_model_sequence(
            region_limits,
            RegionLimitRequestItem,
            "region_limits",
        )
        for item in parsed_limits:
            validate_card_or_group_target(
                card_id=item.card_id,
                group_id=item.group_id,
                required=True,
            )

        cid = await self._resolve_batch_contract_id(
            contract_id=contract_id,
            item_contract_ids=[item.contract_id for item in parsed_limits],
        )
        serialized_limits: list[dict[str, Any]] = []
        for item in parsed_limits:
            serialized = item.model_dump(by_alias=True, exclude_none=True)
            serialized["contract_id"] = cid
            serialized_limits.append(serialized)

        return await self._request(
            SET_REGION_LIMIT,
            api_version=api_version,
            data={"region_limit": to_json_param(serialized_limits)},
            request_contract_id=cid,
        )

    async def remove_region_limit(
        self,
        *,
        contract_id: str | None = None,
        regionlimit_id: str,
        group_id: str | None = None,
        api_version: str | None = None,
    ) -> RemoveRegionLimit:
        """Удалить региональный лимит карты или группы карт."""
        cid = await self._resolve_contract_id(contract_id)
        body = {
            "regionlimit_id": require_identifier(regionlimit_id, "regionlimit_id"),
            "contract_id": cid,
        }
        if group_id is not None:
            body["group_id"] = require_identifier(group_id, "group_id")
        return await self._request(
            REMOVE_REGION_LIMIT,
            api_version=api_version,
            data=body,
            request_contract_id=cid,
        )
