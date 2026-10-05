from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel

from ..models.region_limits import RegionLimitRequestItem
from ..models.restrictions import RestrictionRequestItem
from ..validation import require_identifier, validate_card_or_group_target

TargetItemT = TypeVar("TargetItemT", RestrictionRequestItem, RegionLimitRequestItem)


def target_query(
    *,
    contract_id: str,
    card_id: str | None,
    group_id: str | None,
) -> dict[str, str]:
    card_id, group_id = validate_card_or_group_target(card_id=card_id, group_id=group_id)
    query = {"contract_id": contract_id}
    if card_id is not None:
        query["card_id"] = card_id
    if group_id is not None:
        query["group_id"] = group_id
    return query


def with_normalized_targets(items: Sequence[TargetItemT]) -> list[TargetItemT]:
    """Проверить цель каждого элемента и отправлять обрезанные card_id и group_id."""
    normalized_items: list[TargetItemT] = []
    for item in items:
        card_id, group_id = validate_card_or_group_target(
            card_id=item.card_id,
            group_id=item.group_id,
            required=True,
        )
        normalized_items.append(item.model_copy(update={"card_id": card_id, "group_id": group_id}))
    return normalized_items


def serialize_contract_items(
    items: Sequence[BaseModel],
    *,
    contract_id: str,
) -> list[dict[str, Any]]:
    serialized_items: list[dict[str, Any]] = []
    for item in items:
        serialized = item.model_dump(by_alias=True, exclude_none=True)
        serialized["contract_id"] = contract_id
        serialized_items.append(serialized)
    return serialized_items


def removal_form(
    *,
    identifier_name: str,
    identifier: str,
    group_id: str | None,
) -> dict[str, str]:
    """Проверенные поля формы удаления; договор добавляет сервис после его выбора."""
    form = {identifier_name: require_identifier(identifier, identifier_name)}
    if group_id is not None:
        form["group_id"] = require_identifier(group_id, "group_id")
    return form


__all__ = ["removal_form", "serialize_contract_items", "target_query", "with_normalized_targets"]
