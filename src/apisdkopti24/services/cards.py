from collections.abc import AsyncIterator

from ..models.cards import (
    BlockCardRequest,
    BoolResponse,
    CardDetailResponse,
    CardDriversResponse,
    CardGroupResponse,
    CardsListResponse,
    CardsV2Query,
    CardsV2Response,
    CardV2Item,
    IDListResponse,
    ResetPinRequest,
    SetCardCommentRequest,
)
from ..models.request_parts import ContractForm, ContractQuery
from ..operations import operation
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import require_identifier, validate_positive_count
from ._shared import paginate

GET_CARDS_V1 = operation("get_cards_v1", CardsListResponse)
GET_CARDS_V2 = operation("get_cards_v2", CardsV2Response)
GET_CARDS_BY_GROUP = operation("get_cards_by_group", CardGroupResponse)
GET_CARD_DRIVERS = operation("get_card_drivers", CardDriversResponse)
GET_CARD_DETAIL = operation("get_card_detail", CardDetailResponse)
BLOCK_CARD = operation("block_card", IDListResponse)
SET_CARD_COMMENT = operation("set_card_comment", BoolResponse)
VERIFY_PIN = operation("verify_pin", BoolResponse)
RESET_PIN = operation("reset_pin", BoolResponse)


class CardsService(_BaseService):
    """Методы работы с топливными картами."""

    async def get_cards_v1(
        self,
        *,
        contract_id: str | None = None,
        cache: bool = True,
    ) -> CardsListResponse:
        """Получить карты договора через API v1."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARDS_V1,
            query={"contract_id": cid, "cache": str(cache).lower()},
            contract_header=cid,
        )

    async def get_cards_v2(
        self,
        *,
        contract_id: str | None = None,
        sort: str = "-id",
        q: str | None = None,
        status: str | None = None,
        carrier: str | None = None,
        platon: bool | None = None,
        avtodor: bool | None = None,
        users: bool | None = None,
        group_id: str | None = None,
        page: int | None = None,
        onpage: int | None = None,
    ) -> CardsV2Response:
        """Получить одну страницу карт договора (API v2, операция ``GET_CARDS_V2``).

        Договор: явный ``contract_id`` или договор сессии. SDK всегда передаёт договор
        серверу: без него API подставил бы первый договор логина. Аргументы проверяются
        до сети; если договор не передан и сессии ещё нет, перед запросом выполнится
        вход. Маршрут, тарификация и повторы описаны в ``GET_CARDS_V2``.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param sort: Поле сортировки; префикс ``-`` сортирует по убыванию.
        :param q: Поиск по номеру карты и комментарию на карте.
        :param status: Статус карты, значение из справочника ``CardStatus``.
        :param carrier: Тип носителя: ``Plastic`` (пластиковая) или ``Virtual Card``
            (виртуальная).
        :param platon: ``True`` оставляет только карты с услугой «Платон».
        :param avtodor: ``True`` оставляет только карты с услугой «Автодор».
        :param users: ``True`` заполняет у карт поля ``users`` и ``mpc``; ответ
            приходит дольше, чем больше карт и пользователей.
        :param group_id: ID группы: вернутся только карты этой группы.
        :param page: Номер страницы, начиная с 1.
        :param onpage: Число карт на странице.
        :return: Страница карт: ``response.result`` (карты) и ``response.total_count``
            (всего карт по фильтру, без учёта страниц).
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не
            выбран. Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни
            один не выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid, request = await self._validated_with_contract(
            CardsV2Query,
            contract_id,
            {
                "sort": sort,
                "q": q,
                "status": status,
                "carrier": carrier,
                "platon": platon,
                "avtodor": avtodor,
                "users": users,
                "group_id": group_id,
                "page": page,
                "onpage": onpage,
            },
        )
        return await self._request(
            GET_CARDS_V2,
            query=request.model_dump(exclude_none=True),
            contract_header=cid,
        )

    async def iter_cards_v2(
        self,
        *,
        contract_id: str | None = None,
        sort: str = "-id",
        q: str | None = None,
        status: str | None = None,
        carrier: str | None = None,
        platon: bool | None = None,
        avtodor: bool | None = None,
        users: bool | None = None,
        group_id: str | None = None,
        onpage: int = 100,
        max_pages: int = 100,
        strict: bool = False,
    ) -> AsyncIterator[CardV2Item]:
        """Перебрать все карты договора по страницам (API v2, через ``get_cards_v2``).

        Договор выбирается один раз на весь перебор, каждая страница — отдельный
        запрос с тем же договором и фильтрами. Перебор заканчивается на пустой
        странице или когда получено ``total_count`` карт. Аргументы проверяются до
        первого запроса.

        Фильтры ``contract_id``, ``sort``, ``q``, ``status``, ``carrier``, ``platon``,
        ``avtodor``, ``users`` и ``group_id`` значат то же, что в ``get_cards_v2``.

        :param onpage: Число карт на странице, больше 0.
        :param max_pages: Наибольшее число страниц (запросов), больше 0.
        :param strict: Что делать, если ``max_pages`` кончились раньше ``total_count``:
            ``False`` — остановиться и записать предупреждение в журнал, ``True`` —
            поднять ``PaginationLimitError``.
        :return: Асинхронный итератор карт ``CardV2Item``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не
            выбран. Запросы не отправлены.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни
            один не выбран.
        :raises PaginationLimitError: Только при ``strict=True``: карт больше, чем
            помещается в ``max_pages`` страниц.
        :raises Opti24Error: Ошибка API или сети на любой странице; уже выданные
            карты остаются у вызывающего кода.
        """
        validate_positive_count(onpage)
        validate_positive_count(max_pages)
        # Фильтры проверяются до входа; договор выбирается один раз на весь перебор.
        cid, filters = await self._validated_with_contract(
            CardsV2Query,
            contract_id,
            {
                "sort": sort,
                "q": q,
                "status": status,
                "carrier": carrier,
                "platon": platon,
                "avtodor": avtodor,
                "users": users,
                "group_id": group_id,
                "onpage": onpage,
            },
        )
        # Имена полей запроса совпадают с параметрами get_cards_v2.
        page_filters = filters.model_dump(exclude={"contract_id", "page"})

        async def fetch_page(page_index: int) -> tuple[list[CardV2Item], int]:
            response = await self.get_cards_v2(contract_id=cid, page=page_index + 1, **page_filters)
            return list(response.result), response.total_count

        async for item in paginate(
            fetch_page,
            max_pages=max_pages,
            operation="iter_cards_v2",
            logger=self.logger,
            strict=strict,
        ):
            yield item

    async def get_cards_by_group(
        self,
        *,
        group_id: str,
        contract_id: str | None = None,
    ) -> CardGroupResponse:
        """Получить карты выбранной группы."""
        wire_group_id = require_identifier(group_id, "group_id")
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARDS_BY_GROUP,
            query={"contract_id": cid, "group_id": wire_group_id},
            contract_header=cid,
        )

    async def get_card_drivers(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
    ) -> CardDriversResponse:
        """Получить пользователей, привязанных к карте."""
        wire_card_id = require_identifier(card_id, "card_id")
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARD_DRIVERS,
            path_params={"card_id": wire_card_id},
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
        )

    async def get_card_detail(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
    ) -> CardDetailResponse:
        """Получить детальную информацию о карте."""
        wire_card_id = require_identifier(card_id, "card_id")
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_CARD_DETAIL,
            query={"contract_id": cid, "card_id": wire_card_id},
            contract_header=cid,
        )

    async def block_card(
        self,
        *,
        card_ids: list[str],
        contract_id: str | None = None,
        block: bool = True,
    ) -> IDListResponse:
        """Заблокировать или разблокировать список карт.

        Типовой сценарий:
            Немедленно заблокировать утраченную карту до её замены.

        Пример:
            ``await client.cards.block_card(card_ids=["card-id"], block=True)``
        """
        cid, request = await self._validated_with_contract(
            BlockCardRequest, contract_id, {"card_id": card_ids, "block": block}
        )
        payload = request.model_dump()
        # Сервер разбирает card_id как одну строку JSON-массива; из повторяющихся полей
        # он молча берёт только последнее значение (проверено на DEMO-стенде).
        payload["card_id"] = to_json_param(request.card_id)
        payload["block"] = str(request.block).lower()
        return await self._request(
            BLOCK_CARD,
            form=payload,
            contract_header=cid,
        )

    async def set_card_comment(
        self,
        *,
        card_id: str,
        comment: str,
        contract_id: str | None = None,
    ) -> BoolResponse:
        """Установить комментарий для карты."""
        cid, request = await self._validated_with_contract(
            SetCardCommentRequest, contract_id, {"card_id": card_id, "comment": comment}
        )
        return await self._request(
            SET_CARD_COMMENT,
            form=request.model_dump(),
            contract_header=cid,
        )

    async def verify_pin(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
    ) -> BoolResponse:
        """Запросить одноразовый код для сброса счётчика неверных вводов PIN.

        Код приходит на email учётной записи API; затем вызовите ``reset_pin`` с ним.
        Сам PIN карты не меняется.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            VERIFY_PIN,
            path_params={"card_id": wire_card_id},
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
        )

    async def reset_pin(
        self,
        *,
        card_id: str,
        code: str,
        contract_id: str | None = None,
    ) -> BoolResponse:
        """Сбросить счётчик неверных вводов PIN кодом из письма после ``verify_pin``.

        Сам PIN карты не меняется: после сброса картой снова можно пользоваться со
        старым PIN.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        reset_request = ResetPinRequest(code=code)
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            RESET_PIN,
            path_params={"card_id": wire_card_id},
            form={
                **ContractForm.create(cid).model_dump(),
                **reset_request.model_dump(),
            },
            contract_header=cid,
        )
