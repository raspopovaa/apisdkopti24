import warnings
from collections.abc import AsyncIterator, Callable
from typing import Any

from ..errors import RequestValidationError
from ..modeling import BaseModel
from ..models.request_parts import ContractQuery
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
    validate_month_span,
    validate_offset_pagination,
    validate_positive_count,
)
from ._shared import paginate

GET_TRANSACTIONS_V1 = operation("get_transactions_v1", TransactionsV1Response)
GET_TRANSACTIONS_V2 = operation("get_transactions_v2", TransactionsV2Response)
GET_CARD_TRANSACTIONS_V2 = operation("get_card_transactions_v2", TransactionsV2Response)
GET_TRANSACTION_DETAIL = operation("get_transaction_detail", TransactionDetailResponse)


def _warn_client_side_processing(
    filter_fn: Callable[..., Any] | None, sort_by: str | None, reverse: bool
) -> None:
    if filter_fn is not None or sort_by is not None or reverse:
        warnings.warn(
            "filter_fn, sort_by и reverse устарели: фильтруйте и сортируйте "
            "response.data.result в приложении",
            DeprecationWarning,
            stacklevel=3,
        )


def _validate_sort_field(model: type[BaseModel], sort_by: str | None) -> None:
    """Отклонить неизвестное поле сортировки до платного запроса."""
    if sort_by is not None and sort_by not in model.model_fields:
        raise RequestValidationError(
            f"sort_by: у транзакции нет поля {sort_by!r}; "
            f"допустимые поля: атрибуты {model.__name__}"
        )


class TransactionsService(_BaseService):
    """Методы работы с транзакциями (v1 и v2)."""

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
                    raise ValueError(f"Отсутствует поле сортировки транзакции: {sort_by}")
                return value

            try:
                result.sort(key=sort_key, reverse=reverse)
            except (TypeError, ValueError):
                self.logger.warning("Не удалось отсортировать транзакции по полю %s", sort_by)
        return result

    async def get_transactions_v1(
        self,
        *,
        contract_id: str | None = None,
        card_id: str | None = None,
        count: int = 20,
        filter_fn: Callable[[TransactionV1], bool] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> TransactionsV1Response:
        """Получить последние транзакции договора, при необходимости: одной карты (v1).

        Операция ``GET_TRANSACTIONS_V1``. Договор: явный ``contract_id`` или договор сессии.
        Аргументы проверяются до сети.

        ``filter_fn``, ``sort_by`` и ``reverse`` устарели (``DeprecationWarning``):
        они обрабатывают уже полученную страницу на стороне SDK. Фильтруйте и
        сортируйте ``response.data.result`` в приложении.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param card_id: Идентификатор топливной карты.
        :param count: Сколько последних транзакций вернуть, больше 0.
        :param filter_fn: Устарел: фильтр уже полученной страницы на стороне SDK, выдаёт
            ``DeprecationWarning``.
        :param sort_by: Устарел: поле для сортировки уже полученной страницы на стороне SDK,
            выдаёт ``DeprecationWarning``.
        :param reverse: Устарел: обратный порядок для ``sort_by``, выдаёт
            ``DeprecationWarning``.
        :return: ``TransactionsV1Response``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        _warn_client_side_processing(filter_fn, sort_by, reverse)
        _validate_sort_field(TransactionV1, sort_by)
        validate_positive_count(count)
        wire_card_id = require_identifier(card_id, "card_id") if card_id is not None else None
        cid = await self._resolve_contract_id(contract_id)
        params = {"contract_id": cid, "count": count}
        if wire_card_id is not None:
            params["card_id"] = wire_card_id
        response = await self._request(
            GET_TRANSACTIONS_V1,
            query=params,
            contract_header=cid,
        )
        response.data.result = self._filter_and_sort(
            response.data.result or [],
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
        strict: bool = False,
    ) -> AsyncIterator[TransactionItemV2]:
        """Перебирать транзакции договора за период постранично, не более max_pages страниц (v2).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до первого
        запроса. Остальные параметры значат то же, что в ``get_transactions_v2``.

        Если ``max_pages`` закончились раньше ``total_count``, перебор останавливается
        с предупреждением в журнале, а при ``strict=True``: с ``PaginationLimitError``.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param date_from: Начало периода, ``YYYY-MM-DD``.
        :param date_to: Конец периода, ``YYYY-MM-DD``; период не длиннее числа дней в месяце
            ``date_from``.
        :param page_limit: Транзакций на странице, больше 0.
        :param max_pages: Наибольшее число страниц (запросов), больше 0.
        :param strict: Что делать, если ``max_pages`` кончились раньше ``total_count``:
            ``False`` — остановиться и записать предупреждение в журнал, ``True`` — поднять
            ``PaginationLimitError``.
        :return: Асинхронный итератор ``TransactionItemV2``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запросы не отправлены.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises PaginationLimitError: Только при ``strict=True``: транзакций больше, чем
            помещается в ``max_pages`` страниц.
        :raises Opti24Error: Ошибка API или сети на любой странице; уже выданные элементы
            остаются у вызывающего кода.
        """
        validate_positive_count(page_limit)
        validate_positive_count(max_pages)
        validate_month_span(date_from, date_to)
        # Договор выбирается один раз: select_contract() во время перебора не должен
        # смешать страницы двух договоров.
        cid = await self._resolve_contract_id(contract_id)

        async def fetch_page(page_index: int) -> tuple[list[TransactionItemV2], int]:
            response = await self.get_transactions_v2(
                contract_id=cid,
                date_from=date_from,
                date_to=date_to,
                page_limit=page_limit,
                page_offset=page_index * page_limit,
            )
            return list(response.data.result or []), response.data.total_count

        async for item in paginate(
            fetch_page,
            max_pages=max_pages,
            operation="iter_transactions_v2",
            logger=self.logger,
            strict=strict,
        ):
            yield item

    async def get_transactions_v2(
        self,
        *,
        contract_id: str | None = None,
        date_from: str,
        date_to: str,
        page_limit: int = 100,
        page_offset: int = 0,
        filter_fn: Callable[[TransactionItemV2], bool] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> TransactionsV2Response:
        """Получить страницу транзакций договора через API v2 (операция ``GET_TRANSACTIONS_V2``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Типовой сценарий:
            Выгрузить транзакции договора за период не более одного месяца,
            последовательно проходя страницы результата.

        Пример:
            ``await client.transactions.get_transactions_v2(date_from="2026-07-01", date_to="2026-07-31")``

        ``filter_fn``, ``sort_by`` и ``reverse`` устарели (``DeprecationWarning``):
        они обрабатывают уже полученную страницу на стороне SDK. Фильтруйте и
        сортируйте ``response.data.result`` в приложении.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param date_from: Начало периода, ``YYYY-MM-DD``.
        :param date_to: Конец периода, ``YYYY-MM-DD``; период не длиннее числа дней в месяце
            ``date_from``.
        :param page_limit: Транзакций на странице, больше 0.
        :param page_offset: Сколько транзакций пропустить от начала выборки, не меньше 0.
        :param filter_fn: Устарел: фильтр уже полученной страницы на стороне SDK, выдаёт
            ``DeprecationWarning``.
        :param sort_by: Устарел: поле для сортировки уже полученной страницы на стороне SDK,
            выдаёт ``DeprecationWarning``.
        :param reverse: Устарел: обратный порядок для ``sort_by``, выдаёт
            ``DeprecationWarning``.
        :return: ``TransactionsV2Response``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        validate_month_span(date_from, date_to)
        validate_offset_pagination(page_limit, page_offset)
        _warn_client_side_processing(filter_fn, sort_by, reverse)
        _validate_sort_field(TransactionItemV2, sort_by)
        cid = await self._resolve_contract_id(contract_id)
        response = await self._request(
            GET_TRANSACTIONS_V2,
            query={
                "contract_id": cid,
                "date_from": date_from,
                "date_to": date_to,
                "page_limit": page_limit,
                "page_offset": page_offset,
            },
            contract_header=cid,
        )
        response.data.result = self._filter_and_sort(
            response.data.result or [],
            filter_fn=filter_fn,
            sort_by=sort_by,
            reverse=reverse,
        )
        return response

    async def iter_card_transactions_v2(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
        date_from: str,
        date_to: str,
        page_limit: int = 100,
        max_pages: int = 100,
        strict: bool = False,
    ) -> AsyncIterator[TransactionItemV2]:
        """Перебирать транзакции карты за период постранично, не более max_pages страниц (v2).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до первого
        запроса. Остальные параметры значат то же, что в ``get_card_transactions_v2``.

        Если ``max_pages`` закончились раньше ``total_count``, перебор останавливается
        с предупреждением в журнале, а при ``strict=True``: с ``PaginationLimitError``.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param date_from: Начало периода, ``YYYY-MM-DD``.
        :param date_to: Конец периода, ``YYYY-MM-DD``; период не длиннее числа дней в месяце
            ``date_from``.
        :param page_limit: Транзакций на странице, больше 0.
        :param max_pages: Наибольшее число страниц (запросов), больше 0.
        :param strict: Что делать, если ``max_pages`` кончились раньше ``total_count``:
            ``False`` — остановиться и записать предупреждение в журнал, ``True`` — поднять
            ``PaginationLimitError``.
        :return: Асинхронный итератор ``TransactionItemV2``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запросы не отправлены.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises PaginationLimitError: Только при ``strict=True``: транзакций больше, чем
            помещается в ``max_pages`` страниц.
        :raises Opti24Error: Ошибка API или сети на любой странице; уже выданные элементы
            остаются у вызывающего кода.
        """
        validate_positive_count(page_limit)
        validate_positive_count(max_pages)
        require_identifier(card_id, "card_id")
        validate_month_span(date_from, date_to)
        cid = await self._resolve_contract_id(contract_id)

        async def fetch_page(page_index: int) -> tuple[list[TransactionItemV2], int]:
            response = await self.get_card_transactions_v2(
                card_id=card_id,
                contract_id=cid,
                date_from=date_from,
                date_to=date_to,
                page_limit=page_limit,
                page_offset=page_index * page_limit,
            )
            return list(response.data.result or []), response.data.total_count

        async for item in paginate(
            fetch_page,
            max_pages=max_pages,
            operation="iter_card_transactions_v2",
            logger=self.logger,
            strict=strict,
        ):
            yield item

    async def get_card_transactions_v2(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
        date_from: str,
        date_to: str,
        page_limit: int = 100,
        page_offset: int = 0,
        filter_fn: Callable[[TransactionItemV2], bool] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> TransactionsV2Response:
        """Получить страницу транзакций карты за период не более месяца (v2).

        Операция ``GET_CARD_TRANSACTIONS_V2``. Договор: явный ``contract_id`` или договор
        сессии. Аргументы проверяются до сети.

        ``filter_fn``, ``sort_by`` и ``reverse`` устарели (``DeprecationWarning``):
        они обрабатывают уже полученную страницу на стороне SDK. Фильтруйте и
        сортируйте ``response.data.result`` в приложении.

        :param card_id: Идентификатор топливной карты.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param date_from: Начало периода, ``YYYY-MM-DD``.
        :param date_to: Конец периода, ``YYYY-MM-DD``; период не длиннее числа дней в месяце
            ``date_from``.
        :param page_limit: Количество транзакций на странице.
        :param page_offset: Количество транзакций, которые нужно пропустить.
        :param filter_fn: Устарел: фильтр уже полученной страницы на стороне SDK, выдаёт
            ``DeprecationWarning``.
        :param sort_by: Устарел: поле для сортировки уже полученной страницы на стороне SDK,
            выдаёт ``DeprecationWarning``.
        :param reverse: Устарел: обратный порядок для ``sort_by``, выдаёт
            ``DeprecationWarning``.
        :return: ``TransactionsV2Response``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        validate_month_span(date_from, date_to)
        validate_offset_pagination(page_limit, page_offset)
        _warn_client_side_processing(filter_fn, sort_by, reverse)
        _validate_sort_field(TransactionItemV2, sort_by)
        wire_card_id = require_identifier(card_id, "card_id")
        cid = await self._resolve_contract_id(contract_id)
        response = await self._request(
            GET_CARD_TRANSACTIONS_V2,
            path_params={"card_id": wire_card_id},
            query={
                "contract_id": cid,
                "date_from": date_from,
                "date_to": date_to,
                "page_limit": page_limit,
                "page_offset": page_offset,
            },
            contract_header=cid,
        )
        response.data.result = self._filter_and_sort(
            response.data.result or [],
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
    ) -> TransactionDetailResponse:
        """Получить подробные данные одной транзакции (v2) (операция ``GET_TRANSACTION_DETAIL``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Для несуществующего ``transaction_id`` сервер отвечает ``200`` с
        ``data.total_count == 0`` и пустым ``data.result``, а не ``404``: SDK не
        выбрасывает ``NotFoundError``. Проверяйте ``total_count`` перед чтением
        ``result[0]``. ID транзакций из ``get_transactions_v1`` в этом методе могут не
        находиться: v1 и v2 показывают разные наборы транзакций.

        :param transaction_id: Идентификатор транзакции.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``TransactionDetailResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_transaction_id = require_identifier(transaction_id, "transaction_id")
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_TRANSACTION_DETAIL,
            path_params={"transaction_id": wire_transaction_id},
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
        )
