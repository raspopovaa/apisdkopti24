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
from ._shared import removal_form, serialize_contract_items, target_query

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
        return await self._request(
            GET_REGION_LIMITS,
            api_version=api_version,
            query=target_query(contract_id=cid, card_id=card_id, group_id=group_id),
            contract_header=cid,
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
        serialized_limits = serialize_contract_items(parsed_limits, contract_id=cid)

        return await self._request(
            SET_REGION_LIMIT,
            api_version=api_version,
            form={"region_limit": to_json_param(serialized_limits)},
            contract_header=cid,
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
        return await self._request(
            REMOVE_REGION_LIMIT,
            api_version=api_version,
            form=removal_form(
                identifier_name="regionlimit_id",
                identifier=regionlimit_id,
                contract_id=cid,
                group_id=group_id,
            ),
            contract_header=cid,
        )
