import json
from typing import Any

from ..models.limits import (
    LimitRequestItem,
    LimitsResponse,
    RemoveLimitResponse,
    SetLimitResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import (
    require_identifier,
    validate_card_or_group_target,
    validate_model_sequence,
)

GET_LIMITS = operation("get_limits", LimitsResponse)
SET_LIMIT = operation("set_limit", SetLimitResponse)
REMOVE_LIMIT = operation("remove_limit", RemoveLimitResponse)


class LimitsService(_BaseService):
    """Methods for product limits (v1)."""

    async def get_limits(
        self,
        *,
        contract_id: str | None = None,
        card_id: str | None = None,
        group_id: str | None = None,
        api_version: str | None = None,
    ) -> LimitsResponse:
        """Получить продуктовые лимиты договора, карты или группы карт."""
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
            GET_LIMITS,
            api_version=api_version,
            params=params,
            request_contract_id=cid,
        )

    async def set_limit(
        self,
        *,
        limits: list[LimitRequestItem],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> SetLimitResponse:
        """Создать или изменить продуктовые лимиты одного договора.

        Типовой сценарий:
            Ограничить суточный объём топлива для карты или группы карт.

        Пример:
            ``await client.limits.set_limit(limits=[LimitRequestItem(...)])``
        """
        parsed_limits = validate_model_sequence(limits, LimitRequestItem, "limits")
        for item in parsed_limits:
            validate_card_or_group_target(
                card_id=item.card_id,
                group_id=item.group_id,
                required=True,
            )
            if item.amount is None and item.sum is None:
                raise ValueError("each limit must contain amount or sum")

        cid = await self._resolve_batch_contract_id(
            contract_id=contract_id,
            item_contract_ids=[item.contract_id for item in parsed_limits],
        )
        serialized_limits: list[dict[str, Any]] = []
        for item in parsed_limits:
            serialized = item.model_dump(by_alias=True, exclude_none=True)
            serialized["contract_id"] = cid
            serialized_limits.append(serialized)

        body = {
            "limit": json.dumps(
                serialized_limits,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        }
        return await self._request(
            SET_LIMIT,
            api_version=api_version,
            data=body,
            request_contract_id=cid,
        )

    async def remove_limit(
        self,
        *,
        contract_id: str | None = None,
        limit_id: str,
        group_id: str | None = None,
        api_version: str | None = None,
    ) -> RemoveLimitResponse:
        """Удалить продуктовый лимит карты или группы карт."""
        cid = await self._resolve_contract_id(contract_id)
        body = {
            "limit_id": require_identifier(limit_id, "limit_id"),
            "contract_id": cid,
        }
        if group_id is not None:
            body["group_id"] = require_identifier(group_id, "group_id")
        return await self._request(
            REMOVE_LIMIT,
            api_version=api_version,
            data=body,
            request_contract_id=cid,
        )
