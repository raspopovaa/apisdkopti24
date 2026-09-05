import pytest

from api_client_opti24.validation import (
    validate_identifier_list,
    validate_non_empty_value,
    validate_offset_pagination,
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
