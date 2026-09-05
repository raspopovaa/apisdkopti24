from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TypeVar

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DocumentFormatT = TypeVar("DocumentFormatT", bound=str)
ModelT = TypeVar("ModelT")


def validate_non_empty_value(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def require_identifier(value: str, field_name: str) -> str:
    return validate_non_empty_value(value, field_name)


def validate_identifier_list(values: Sequence[str], field_name: str) -> list[str]:
    if not values:
        raise ValueError(f"{field_name} must contain at least one item")
    return [require_identifier(value, field_name) for value in values]


def validate_model_sequence(
    values: Sequence[object],
    model_type: type[ModelT],
    field_name: str,
) -> list[ModelT]:
    if not values:
        raise ValueError(f"{field_name} must contain at least one item")
    validated: list[ModelT] = []
    for index, value in enumerate(values):
        if not isinstance(value, model_type):
            raise TypeError(f"{field_name}[{index}] must be an instance of {model_type.__name__}")
        validated.append(value)
    return validated


def validate_card_or_group_target(
    *,
    card_id: str | None,
    group_id: str | None,
    required: bool = False,
) -> tuple[str | None, str | None]:
    normalized_card = require_identifier(card_id, "card_id") if card_id is not None else None
    normalized_group = require_identifier(group_id, "group_id") if group_id is not None else None
    if normalized_card is not None and normalized_group is not None:
        raise ValueError("card_id and group_id are mutually exclusive")
    if required and normalized_card is None and normalized_group is None:
        raise ValueError("either card_id or group_id is required")
    return normalized_card, normalized_group


def validate_date_range(date_start: str, date_end: str) -> tuple[str, str]:
    try:
        start = date.fromisoformat(date_start)
        end = date.fromisoformat(date_end)
    except ValueError as exc:
        raise ValueError("date_start and date_end must use YYYY-MM-DD format") from exc
    if end < start:
        raise ValueError("date_end must not be earlier than date_start")
    return date_start, date_end


def validate_pagination(page: int, on_page: int) -> tuple[int, int]:
    if page <= 0:
        raise ValueError("page must be greater than zero")
    if on_page <= 0:
        raise ValueError("on_page must be greater than zero")
    return page, on_page


def validate_offset_pagination(limit: int, offset: int) -> tuple[int, int]:
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    if offset < 0:
        raise ValueError("offset must not be negative")
    return limit, offset


def validate_positive_count(count: int) -> int:
    if count <= 0:
        raise ValueError("count must be greater than zero")
    return count


def decimal_to_wire(value: Decimal, field_name: str = "amount") -> str:
    try:
        normalized = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid decimal value") from exc
    if not normalized.is_finite() or normalized <= 0:
        raise ValueError(f"{field_name} must be greater than zero")
    return format(normalized, "f")


def validate_email(value: str, field_name: str = "email") -> str:
    normalized = value.strip()
    if not _EMAIL_PATTERN.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a valid email address")
    return normalized


def validate_document_order(
    document_ids: list[str],
    document_format: DocumentFormatT,
    emails: list[str],
) -> tuple[list[str], DocumentFormatT, list[str]]:
    normalized_ids = validate_identifier_list(document_ids, "document ID")
    if document_format not in {"pdf", "xlsx"}:
        raise ValueError("fmt must be either 'pdf' or 'xlsx'")
    if not emails or len(emails) > 5:
        raise ValueError("emails must contain from 1 to 5 addresses")
    normalized_emails = [validate_email(value, "email") for value in emails]
    return normalized_ids, document_format, normalized_emails


__all__ = [
    "decimal_to_wire",
    "require_identifier",
    "validate_card_or_group_target",
    "validate_date_range",
    "validate_document_order",
    "validate_email",
    "validate_identifier_list",
    "validate_model_sequence",
    "validate_non_empty_value",
    "validate_offset_pagination",
    "validate_pagination",
    "validate_positive_count",
]
