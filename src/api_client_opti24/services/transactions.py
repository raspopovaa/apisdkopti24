from collections.abc import AsyncIterator, Callable
from typing import Any

from .. import utils
from ..models.transactions import (
    TransactionDetailResponse,
    TransactionItemV2,
    TransactionsV1Response,
    TransactionsV2Response,
    TransactionV1,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import (
    require_identifier,
    validate_offset_pagination,
    validate_positive_count,
)

GET_TRANSACTIONS_V1 = operation("get_transactions_v1", TransactionsV1Response)
GET_TRANSACTIONS_V2 = operation("get_transactions_v2", TransactionsV2Response)
GET_CARD_TRANSACTIONS_V2 = operation("get_card_transactions_v2", TransactionsV2Response)
GET_TRANSACTION_DETAIL = operation("get_transaction_detail", TransactionDetailResponse)


class TransactionsService(_BaseService):
    """Methods for transactions (v1 and v2)."""

    def _filter_and_sort(
        self,
        items: list[Any],
        *,
        filter_fn: Callable[..., Any] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> list[Any]:
        result = items
        if filter_fn:
            result = list(filter(filter_fn, result))
        if sort_by:

            def sort_key(item: Any) -> Any:
                value = getattr(item, sort_by, None)
                if value is None:
                    raise ValueError(f"transaction sort field is missing: {sort_by}")
                return value

            try:
                result.sort(key=sort_key, reverse=reverse)
            except (TypeError, ValueError):
                self.logger.warning("Transaction sorting failed sort_by=%s", sort_by)
        return result

    async def get_transactions_v1(
        self,
        *,
        contract_id: str | None = None,
        card_id: str | None = None,
        count: int = 20,
        api_version: str | None = None,
        filter_fn: Callable[[TransactionV1], bool] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> TransactionsV1Response:
        """Return the latest v1 transactions for a contract and optional card."""
        cid = await self._resolve_contract_id(contract_id)
        validate_positive_count(count)
        params = {"contract_id": cid, "count": count}
        if card_id is not None:
            params["card_id"] = require_identifier(card_id, "card_id")
        response = await self._request(
            GET_TRANSACTIONS_V1,
            api_version=api_version,
            params=params,
            request_contract_id=cid,
        )
        response.data.result = self._filter_and_sort(
            response.data.result,
            filter_fn=filter_fn,
            sort_by=sort_by,
            reverse=reverse,
        )
        return response

    async def iter_transactions_v2(
        self,
        *,
        contract_id: str | None = None,
        date_from: str,
        date_to: str,
        page_limit: int = 100,
        max_pages: int = 100,
        api_version: str | None = None,
    ) -> AsyncIterator[TransactionItemV2]:
        """Iterate over paginated v2 contract transactions for one date range."""
        validate_positive_count(page_limit)
        validate_positive_count(max_pages)
        yielded = 0
        for page in range(max_pages):
            response = await self.get_transactions_v2(
                contract_id=contract_id,
                date_from=date_from,
                date_to=date_to,
                page_limit=page_limit,
                page_offset=page * page_limit,
                api_version=api_version,
            )
            for item in response.data.result:
                yield item
                yielded += 1
            if not response.data.result or yielded >= response.data.total_count:
                return

    async def get_transactions_v2(
        self,
        *,
        contract_id: str | None = None,
        date_from: str,
        date_to: str,
        page_limit: int = 100,
        page_offset: int = 0,
        api_version: str | None = None,
        filter_fn: Callable[[TransactionItemV2], bool] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> TransactionsV2Response:
        """Получить страницу транзакций договора через API v2.

        Типовой сценарий:
            Выгрузить транзакции договора за период не более одного месяца,
            последовательно проходя страницы результата.

        Пример:
            ``await client.transactions.get_transactions_v2(date_from="2026-07-01", date_to="2026-07-31")``
        """
        cid = await self._resolve_contract_id(contract_id)
        utils.validate_month_span(date_from, date_to)
        validate_offset_pagination(page_limit, page_offset)
        response = await self._request(
            GET_TRANSACTIONS_V2,
            api_version=api_version,
            params={
                "contract_id": cid,
                "date_from": date_from,
                "date_to": date_to,
                "page_limit": page_limit,
                "page_offset": page_offset,
            },
            request_contract_id=cid,
        )
        response.data.result = self._filter_and_sort(
            response.data.result,
            filter_fn=filter_fn,
            sort_by=sort_by,
            reverse=reverse,
        )
        return response

    async def get_card_transactions_v2(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
        date_from: str,
        date_to: str,
        page_limit: int = 100,
        page_offset: int = 0,
        api_version: str | None = None,
        filter_fn: Callable[[TransactionItemV2], bool] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> TransactionsV2Response:
        """Return paginated v2 transactions for one card and one-month range."""
        utils.validate_month_span(date_from, date_to)
        validate_offset_pagination(page_limit, page_offset)
        cid = await self._resolve_contract_id(contract_id)
        response = await self._request(
            GET_CARD_TRANSACTIONS_V2,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            params={
                "contract_id": cid,
                "date_from": date_from,
                "date_to": date_to,
                "page_limit": page_limit,
                "page_offset": page_offset,
            },
            request_contract_id=cid,
        )
        response.data.result = self._filter_and_sort(
            response.data.result,
            filter_fn=filter_fn,
            sort_by=sort_by,
            reverse=reverse,
        )
        return response

    async def get_transaction_detail(
        self,
        *,
        transaction_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> TransactionDetailResponse:
        """Return detailed v2 data for one transaction."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_TRANSACTION_DETAIL,
            api_version=api_version,
            path_params={"transaction_id": require_identifier(transaction_id, "transaction_id")},
            params={"contract_id": cid},
            request_contract_id=cid,
        )
