from decimal import Decimal
from typing import Literal

from ..models.contracts import (
    ContractDataResponse,
    DocumentsOrderResponse,
    DocumentsResponse,
    InvoiceOrderResponse,
    InvoicesResponse,
    OrderCardsResponse,
    PaymentsResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import (
    decimal_to_wire,
    require_identifier,
    validate_date_range,
    validate_document_order,
    validate_email,
    validate_pagination,
    validate_positive_count,
)

DocumentFormat = Literal["pdf", "xlsx"]
GET_CONTRACT_DATA = operation("get_contract_data", ContractDataResponse)
GET_PAYMENTS = operation("get_payments", PaymentsResponse)
GET_DOCUMENTS = operation("get_documents", DocumentsResponse)
ORDER_DOCUMENTS_EMAIL = operation("order_documents_email", DocumentsOrderResponse)
ORDER_CARDS = operation("order_cards", OrderCardsResponse)
ORDER_INVOICE = operation("order_invoice", InvoiceOrderResponse)
GET_INVOICES = operation("get_invoices", InvoicesResponse)


class ContractsService(_BaseService):
    async def get_contract_data(
        self,
        *,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> ContractDataResponse:
        """Получение информации о контракте."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CONTRACT_DATA,
            api_version=api_version,
            params={"contract_id": cid},
            request_contract_id=cid,
        )

    async def get_payments(
        self,
        *,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> PaymentsResponse:
        """Получение данных о платежах по контракту."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_PAYMENTS,
            api_version=api_version,
            params={"contract_id": cid},
            request_contract_id=cid,
        )

    async def get_documents(
        self,
        *,
        date_start: str,
        date_end: str,
        contract_id: str | None = None,
        api_version: str | None = None,
        page: int = 1,
        on_page: int = 10,
    ) -> DocumentsResponse:
        """Получение списка первичных документов (номер документа, дата, сумма, НДС, номер договора и пр.)."""
        cid = await self._resolve_contract_id(contract_id)
        date_start, date_end = validate_date_range(date_start, date_end)
        page, on_page = validate_pagination(page, on_page)
        params = {
            "date_start": date_start,
            "date_end": date_end,
            "page": page,
            "on_page": on_page,
        }
        return await self._request(
            GET_DOCUMENTS,
            api_version=api_version,
            params=params,
            request_contract_id=cid,
        )

    async def order_documents_email(
        self,
        *,
        ids: list[str],
        fmt: DocumentFormat,
        emails: list[str],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> DocumentsOrderResponse:
        """Заказ первичных документов по ID документа на указанные email – адреса (до 5 адресов)."""
        cid = await self._resolve_contract_id(contract_id)
        ids, fmt, emails = validate_document_order(ids, fmt, emails)
        payload = {"id": ids, "format": fmt, "emails": emails}
        return await self._request(
            ORDER_DOCUMENTS_EMAIL,
            api_version=api_version,
            json=payload,
            request_contract_id=cid,
        )

    async def order_cards(
        self,
        *,
        count: int,
        office_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> OrderCardsResponse:
        """Заказ необходимого количества топливных карт в определенном офисе продаж."""
        cid = await self._resolve_contract_id(contract_id)
        payload = {
            "count": validate_positive_count(count),
            "office_id": require_identifier(office_id, "office_id"),
        }
        return await self._request(
            ORDER_CARDS,
            api_version=api_version,
            data=payload,
            request_contract_id=cid,
        )

    async def order_invoice(
        self,
        *,
        amount: Decimal,
        email: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> InvoiceOrderResponse:
        """Заказать счёт на оплату и отправить его на email.

        Типовой сценарий:
            Сформировать счёт на заданную сумму после проверки адреса
            получателя. Повтор запроса выполняйте только после проверки статуса
            предыдущей операции.

        Пример вызова:
        ```python
        invoice = await client.contracts.order_invoice(
            amount=Decimal("15000.00"),
            email="billing@example.org",
        )
        ```

        Пример payload:
        ```json
        {"sum": "15000.00", "email": "billing@example.org"}
        ```
        """
        cid = await self._resolve_contract_id(contract_id)
        payload = {
            "sum": decimal_to_wire(amount, "amount"),
            "email": validate_email(email),
        }
        return await self._request(
            ORDER_INVOICE,
            api_version=api_version,
            data=payload,
            request_contract_id=cid,
        )

    async def get_invoices(
        self,
        *,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> InvoicesResponse:
        """Получение списка счетов на оплату."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_INVOICES,
            api_version=api_version,
            request_contract_id=cid,
        )
