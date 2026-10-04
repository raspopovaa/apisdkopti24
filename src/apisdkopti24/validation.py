from __future__ import annotations

import calendar
import re
from collections.abc import Sequence
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TypeVar

from .errors import RequestValidationError

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DocumentFormatT = TypeVar("DocumentFormatT", bound=str)
ModelT = TypeVar("ModelT")


def validate_non_empty_value(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise RequestValidationError(f"{field_name}: значение не может быть пустым")
    return normalized


def require_identifier(value: str, field_name: str) -> str:
    return validate_non_empty_value(value, field_name)


def validate_identifier_list(values: Sequence[str], field_name: str) -> list[str]:
    if not values:
        raise RequestValidationError(f"{field_name}: необходим хотя бы один элемент")
    return [require_identifier(value, field_name) for value in values]


def validate_model_sequence(
    values: Sequence[object],
    model_type: type[ModelT],
    field_name: str,
) -> list[ModelT]:
    if not values:
        raise RequestValidationError(f"{field_name}: необходим хотя бы один элемент")
    validated: list[ModelT] = []
    for index, value in enumerate(values):
        if not isinstance(value, model_type):
            raise RequestValidationError(
                f"{field_name}[{index}] должен быть экземпляром {model_type.__name__}"
            )
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
        raise RequestValidationError("card_id и group_id нельзя задавать одновременно")
    if required and normalized_card is None and normalized_group is None:
        raise RequestValidationError("Необходимо указать card_id или group_id")
    return normalized_card, normalized_group


def validate_date_range(
    date_start: str,
    date_end: str,
    *,
    start_name: str = "date_start",
    end_name: str = "date_end",
) -> tuple[str, str]:
    try:
        start = date.fromisoformat(date_start)
        end = date.fromisoformat(date_end)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(
            f"{start_name} и {end_name} должны иметь формат YYYY-MM-DD"
        ) from exc
    if end < start:
        raise RequestValidationError(f"{end_name} не может предшествовать {start_name}")
    return date_start, date_end


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year, month = value.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(value.day, calendar.monthrange(year, month)[1]))


def validate_period_months(
    date_start: str,
    date_end: str,
    *,
    months: int,
    start_name: str,
    end_name: str,
) -> tuple[str, str]:
    """Проверить формат, порядок дат и длину периода в календарных месяцах.

    Конец периода может совпадать с той же датой через ``months`` месяцев: пример
    спецификации заказывает отчёт с 2022-11-01 по 2022-12-01. Длиннее сервер не
    отклоняет, а молча сокращает период.
    """
    validate_date_range(date_start, date_end, start_name=start_name, end_name=end_name)
    if date.fromisoformat(date_end) > _add_months(date.fromisoformat(date_start), months):
        raise RequestValidationError(
            f"Период {start_name}–{end_name} длиннее {months} календарн"
            f"{'ого месяца' if months == 1 else 'ых месяцев'}"
        )
    return date_start, date_end


def validate_email_list(values: Sequence[str], field_name: str) -> list[str]:
    if isinstance(values, str) or not values:
        raise RequestValidationError(f"{field_name}: ожидается непустой список адресов")
    return [validate_email(value, f"{field_name}[{index}]") for index, value in enumerate(values)]


def validate_pagination(page: int, on_page: int) -> tuple[int, int]:
    if page <= 0:
        raise RequestValidationError("page должен быть больше нуля")
    if on_page <= 0:
        raise RequestValidationError("on_page должен быть больше нуля")
    return page, on_page


def validate_offset_pagination(limit: int, offset: int) -> tuple[int, int]:
    if limit <= 0:
        raise RequestValidationError("limit должен быть больше нуля")
    if offset < 0:
        raise RequestValidationError("offset не может быть отрицательным")
    return limit, offset


def validate_positive_count(count: int) -> int:
    if count <= 0:
        raise RequestValidationError("count должен быть больше нуля")
    return count


def decimal_to_wire(value: Decimal, field_name: str = "amount") -> str:
    try:
        normalized = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RequestValidationError(
            f"{field_name}: ожидается корректное десятичное число"
        ) from exc
    if not normalized.is_finite() or normalized <= 0:
        raise RequestValidationError(f"{field_name}: значение должно быть больше нуля")
    # Денежные суммы — в рублях с копейками: доли копейки сервер мог бы округлить
    # или отбросить по-своему. 10.500 допустимо, 10.005 — нет.
    if normalized != normalized.quantize(Decimal("0.01")):
        raise RequestValidationError(f"{field_name}: не больше двух знаков после запятой (копейки)")
    return format(normalized, "f")


def validate_email(value: str, field_name: str = "email") -> str:
    normalized = value.strip()
    if not _EMAIL_PATTERN.fullmatch(normalized):
        raise RequestValidationError(f"{field_name}: ожидается корректный адрес электронной почты")
    return normalized


def validate_document_order(
    document_ids: list[str],
    document_format: DocumentFormatT,
    emails: list[str],
) -> tuple[list[str], DocumentFormatT, list[str]]:
    normalized_ids = validate_identifier_list(document_ids, "Идентификаторы документов")
    if document_format not in {"pdf", "xlsx"}:
        raise RequestValidationError("fmt должен быть равен 'pdf' или 'xlsx'")
    if not emails or len(emails) > 5:
        raise RequestValidationError("emails должен содержать от 1 до 5 адресов")
    normalized_emails = [validate_email(value, "email") for value in emails]
    return normalized_ids, document_format, normalized_emails


__all__ = [
    "decimal_to_wire",
    "require_identifier",
    "validate_card_or_group_target",
    "validate_date_range",
    "validate_document_order",
    "validate_email",
    "validate_email_list",
    "validate_identifier_list",
    "validate_model_sequence",
    "validate_non_empty_value",
    "validate_offset_pagination",
    "validate_pagination",
    "validate_period_months",
    "validate_positive_count",
]
