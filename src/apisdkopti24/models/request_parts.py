from __future__ import annotations

from typing import Annotated

from pydantic import StringConstraints

from ..modeling import Field, StrictRequestModel
from ..validation import require_identifier, validate_date_range, validate_pagination

Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
PositivePage = Annotated[int, Field(ge=1)]


class PaginationQuery(StrictRequestModel):
    """Общие параметры постраничных методов."""

    page: PositivePage | None = Field(None, description="Номер страницы начиная с 1")
    on_page: PositivePage | None = Field(None, description="Количество записей на странице")


class OffsetPaginationQuery(StrictRequestModel):
    """Общие параметры пагинации limit/offset."""

    limit: PositivePage = Field(..., description="Максимальное количество записей")
    offset: int = Field(0, ge=0, description="Смещение первой записи")


class ResourcePath(StrictRequestModel):
    """Строгий одиночный идентификатор path-параметра."""

    resource_id: Identifier


class ContractQuery(StrictRequestModel):
    contract_id: str = Field(..., description="ID договора")

    @classmethod
    def create(cls, contract_id: str) -> ContractQuery:
        return cls(contract_id=require_identifier(contract_id, "contract_id"))


class DateRangePaginationQuery(StrictRequestModel):
    date_start: str = Field(..., description="Дата начала периода в формате YYYY-MM-DD")
    date_end: str = Field(..., description="Дата окончания периода в формате YYYY-MM-DD")
    page: int = Field(1, description="Номер страницы")
    on_page: int = Field(10, description="Количество элементов на странице")

    @classmethod
    def create(
        cls, *, date_start: str, date_end: str, page: int, on_page: int
    ) -> DateRangePaginationQuery:
        start, end = validate_date_range(date_start, date_end)
        normalized_page, normalized_on_page = validate_pagination(page, on_page)
        return cls(
            date_start=start,
            date_end=end,
            page=normalized_page,
            on_page=normalized_on_page,
        )


class ContractForm(StrictRequestModel):
    contract_id: str = Field(..., description="ID договора")

    @classmethod
    def create(cls, contract_id: str) -> ContractForm:
        return cls(contract_id=require_identifier(contract_id, "contract_id"))


__all__ = [
    "ContractForm",
    "ContractQuery",
    "DateRangePaginationQuery",
    "Identifier",
    "OffsetPaginationQuery",
    "PaginationQuery",
    "PositivePage",
    "ResourcePath",
]
