from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel

from ..validation import require_identifier, validate_card_or_group_target


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
    contract_id: str,
    group_id: str | None,
) -> dict[str, str]:
    form = {
        identifier_name: require_identifier(identifier, identifier_name),
        "contract_id": contract_id,
    }
    if group_id is not None:
        form["group_id"] = require_identifier(group_id, "group_id")
    return form


__all__ = ["removal_form", "serialize_contract_items", "target_query"]
