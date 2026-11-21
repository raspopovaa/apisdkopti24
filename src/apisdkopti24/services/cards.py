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
        """Получить карты договора через API v1 (операция ``GET_CARDS_V1``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param cache: ``True`` — данные из кеша карт; ``False`` — прямой запрос в процессинг
            (дольше, зато актуальнее).
        :return: ``CardsListResponse``: ``response.result`` (элементы) и
            ``response.total_count`` (всего по запросу).
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
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
        # exclude_none: незаданный фильтр не попадает в URL. Без него httpx отправил бы
        # пустое значение («status=»), и сервер мог бы искать по нему.
        # Договор уходит и в query (он поле модели), и в заголовок; оба места сверяет
        # tests/test_contract_placement.py.
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
        # Имена полей запроса совпадают с параметрами get_cards_v2. Договор передаётся
        # отдельно как уже выбранный cid, а номер страницы задаёт fetch_page.
        page_filters = filters.model_dump(exclude={"contract_id", "page"})

        async def fetch_page(page_index: int) -> tuple[list[CardV2Item], int]:
            # paginate считает страницы с 0, API — с 1. Вызов идёт через публичный
            # get_cards_v2: каждая страница проходит ту же проверку и аудит, а явный
            # cid не запускает повторный выбор договора и вход.
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
        """Получить карты выбранной группы (операция ``GET_CARDS_BY_GROUP``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param group_id: Идентификатор группы топливных карт.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``CardGroupResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
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
        """Получить пользователей, привязанных к карте (операция ``GET_CARD_DRIVERS``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param card_id: Идентификатор топливной карты.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``CardDriversResponse``: ``response.result`` (элементы) и
            ``response.total_count`` (всего по запросу).
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
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
        """Получить детальную информацию о карте (операция ``GET_CARD_DETAIL``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param card_id: Идентификатор топливной карты.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``CardDetailResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
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
        """Заблокировать или разблокировать список карт (операция ``BLOCK_CARD``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Типовой сценарий:
            Немедленно заблокировать утраченную карту до её замены.

        Пример:
            ``await client.cards.block_card(card_ids=["card-id"], block=True)``

        :param card_ids: Список идентификаторов топливных карт.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param block: ``true`` — заблокировать карту, ``false`` — разблокировать.
        :return: ``IDListResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
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
        """Установить комментарий для карты (операция ``SET_CARD_COMMENT``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param card_id: Идентификатор топливной карты.
        :param comment: Комментарий к топливной карте.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``BoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
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

        Операция ``VERIFY_PIN``. Договор: явный ``contract_id`` или договор сессии. Аргументы
        проверяются до сети.

        Код приходит на email учётной записи API; затем вызовите ``reset_pin`` с ним.
        Сам PIN карты не меняется.

        :param card_id: Идентификатор топливной карты.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``BoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
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

        Операция ``RESET_PIN``. Договор: явный ``contract_id`` или договор сессии. Аргументы
        проверяются до сети.

        Сам PIN карты не меняется: после сброса картой снова можно пользоваться со
        старым PIN.

        :param card_id: Идентификатор топливной карты.
        :param code: Код подтверждения, полученный по email.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``BoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
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
