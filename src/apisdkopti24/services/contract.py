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
from ..models.request_parts import ContractQuery, DateRangePaginationQuery
from ..operations import operation
from ..service_base import _BaseService
from ..validation import (
    decimal_to_wire,
    require_identifier,
    validate_document_order,
    validate_email,
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
    ) -> ContractDataResponse:
        """Получение информации о контракте (операция ``GET_CONTRACT_DATA``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``ContractDataResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CONTRACT_DATA,
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
        )

    async def get_payments(
        self,
        *,
        contract_id: str | None = None,
    ) -> PaymentsResponse:
        """Получение данных о платежах по контракту (операция ``GET_PAYMENTS``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``PaymentsResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_PAYMENTS,
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
        )

    async def get_documents(
        self,
        *,
        date_start: str,
        date_end: str,
        contract_id: str | None = None,
        page: int = 1,
        on_page: int = 10,
    ) -> DocumentsResponse:
        """Получение списка первичных документов (номер документа, дата, сумма, НДС, номер договора и пр.).

        Операция ``GET_DOCUMENTS``. Договор: явный ``contract_id`` или договор сессии. Аргументы
        проверяются до сети.

        :param date_start: Дата начала периода в формате ``YYYY-MM-DD``.
        :param date_end: Дата окончания периода в формате ``YYYY-MM-DD``.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param page: Номер страницы результата.
        :param on_page: Количество элементов на странице.
        :return: ``DocumentsResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        query = DateRangePaginationQuery.create(
            date_start=date_start,
            date_end=date_end,
            page=page,
            on_page=on_page,
        )
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_DOCUMENTS,
            query=query.model_dump(),
            contract_header=cid,
        )

    async def order_documents_email(
        self,
        *,
        ids: list[str],
        fmt: DocumentFormat,
        emails: list[str],
        contract_id: str | None = None,
    ) -> DocumentsOrderResponse:
        """Заказ первичных документов по ID документа на указанные email – адреса (до 5 адресов).

        Операция ``ORDER_DOCUMENTS_EMAIL``. Договор: явный ``contract_id`` или договор сессии.
        Аргументы проверяются до сети.

        :param ids: Список ID документов. В API параметр называется ``id``.
        :param fmt: Формат документа: ``pdf`` или ``xlsx``. В API параметр называется
            ``format``.
        :param emails: Список email-адресов для отправки документов, не более пяти.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``DocumentsOrderResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        ids, fmt, emails = validate_document_order(ids, fmt, emails)
        cid = await self._resolve_contract_id(contract_id)
        payload = {"id": ids, "format": fmt, "emails": emails}
        return await self._request(
            ORDER_DOCUMENTS_EMAIL,
            json_body=payload,
            contract_header=cid,
        )

    async def order_cards(
        self,
        *,
        count: int,
        office_id: str,
        contract_id: str | None = None,
    ) -> OrderCardsResponse:
        """Заказ необходимого количества топливных карт в определенном офисе продаж.

        Операция ``ORDER_CARDS``. Договор: явный ``contract_id`` или договор сессии. Аргументы
        проверяются до сети.

        :param count: Количество заказываемых карт.
        :param office_id: ID офиса продаж из справочника ``Office``.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``OrderCardsResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        payload = {
            "count": validate_positive_count(count),
            "office_id": require_identifier(office_id, "office_id"),
        }
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            ORDER_CARDS,
            form=payload,
            contract_header=cid,
        )

    async def order_invoice(
        self,
        *,
        amount: Decimal,
        email: str,
        contract_id: str | None = None,
    ) -> InvoiceOrderResponse:
        """Заказать счёт на оплату и отправить его на email (операция ``ORDER_INVOICE``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

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

        :param amount: Сумма счёта в рублях. В API параметр называется ``sum``.
        :param email: Email-адрес для отправки счёта.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``InvoiceOrderResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        payload = {
            "sum": decimal_to_wire(amount, "amount"),
            "email": validate_email(email),
        }
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            ORDER_INVOICE,
            form=payload,
            contract_header=cid,
        )

    async def get_invoices(
        self,
        *,
        contract_id: str | None = None,
    ) -> InvoicesResponse:
        """Получение списка счетов на оплату (операция ``GET_INVOICES``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``InvoicesResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_INVOICES,
            contract_header=cid,
        )
