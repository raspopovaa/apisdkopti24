from __future__ import annotations

from ..modeling import StrictRequestModel
from ..validation import require_identifier, validate_date_range, validate_pagination


class ContractQuery(StrictRequestModel):
    contract_id: str

    @classmethod
    def create(cls, contract_id: str) -> ContractQuery:
        return cls(contract_id=require_identifier(contract_id, "contract_id"))


class DateRangePaginationQuery(StrictRequestModel):
    date_start: str
    date_end: str
    page: int = 1
    on_page: int = 10

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
    contract_id: str

    @classmethod
    def create(cls, contract_id: str) -> ContractForm:
        return cls(contract_id=require_identifier(contract_id, "contract_id"))


__all__ = ["ContractForm", "ContractQuery", "DateRangePaginationQuery"]
