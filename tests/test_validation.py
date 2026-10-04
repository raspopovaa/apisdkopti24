import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.models.users import UserCreateRequest
from apisdkopti24.utils import validate_month_span
from apisdkopti24.validation import (
    require_identifier,
    validate_date_range,
    validate_identifier_list,
    validate_mobile,
    validate_non_empty_value,
    validate_offset_pagination,
    validate_period_months,
    validate_sort_fields,
)


def test_validate_identifier_list_normalizes_and_preserves_order() -> None:
    assert validate_identifier_list([" first ", "second"], "ids") == [
        "first",
        "second",
    ]


@pytest.mark.parametrize("values", [[], ["valid", "  "]])
def test_validate_identifier_list_rejects_empty_values(values: list[str]) -> None:
    with pytest.raises(ValueError):
        validate_identifier_list(values, "ids")


def test_validate_non_empty_value_normalizes_whitespace() -> None:
    assert validate_non_empty_value(" xlsx ", "format") == "xlsx"
    with pytest.raises(ValueError, match="format"):
        validate_non_empty_value("  ", "format")


@pytest.mark.parametrize(("limit", "offset"), [(0, 0), (10, -1)])
def test_validate_offset_pagination_rejects_invalid_values(
    limit: int,
    offset: int,
) -> None:
    with pytest.raises(ValueError):
        validate_offset_pagination(limit, offset)


@pytest.mark.parametrize("value", ["20260901", "2026-W36-1", "2026-09-01T00:00", "２０２６-09-01"])
def test_dates_accept_only_plain_yyyy_mm_dd(value: str) -> None:
    with pytest.raises(RequestValidationError, match="YYYY-MM-DD"):
        validate_date_range(value, "2026-09-30")
    with pytest.raises(RequestValidationError, match="YYYY-MM-DD"):
        validate_period_months(value, "2026-09-30", months=1, start_name="start", end_name="end")
    with pytest.raises(RequestValidationError, match="YYYY-MM-DD"):
        validate_month_span(value, "2026-09-30")


@pytest.mark.parametrize("mobile", ["٧٩٩٩٠٠٠٠٠٠٠", "７９９９０００００００"])
def test_mobile_accepts_only_ascii_digits(mobile: str) -> None:
    with pytest.raises(RequestValidationError):
        validate_mobile(mobile)
    with pytest.raises(ValueError):
        UserCreateRequest(uuid="external-1", mobile=mobile)


@pytest.mark.parametrize(
    "call",
    [
        lambda: validate_mobile(79990000000),  # type: ignore[arg-type]
        lambda: validate_sort_fields(123, {"id"}, "x"),  # type: ignore[arg-type]
        lambda: require_identifier(None, "card_id"),  # type: ignore[arg-type]
    ],
    ids=["mobile-int", "sort-int", "identifier-none"],
)
def test_non_string_scalars_raise_typed_validation_error(call) -> None:
    with pytest.raises(RequestValidationError, match="ожидается строка"):
        call()
