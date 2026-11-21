from collections.abc import Mapping

from ..errors import RequestValidationError
from ..models.dictionaries import (
    AzsFiltersResponse,
    AzsListV1Response,
    AzsListV2Response,
    AzsV1Filter,
    AzsV1Query,
    AzsV2Filter,
    AzsV2Query,
    DictionaryResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import require_identifier

GET_AZS_LIST_V1 = operation("get_azs_list_v1", AzsListV1Response)
GET_AZS_LIST_V2 = operation("get_azs_list_v2", AzsListV2Response)
GET_AZS_FILTERS = operation("get_azs_filters", AzsFiltersResponse)
GET_DICTIONARY = operation("get_dictionary", DictionaryResponse)


class DictionariesService(_BaseService):
    """Методы для работы со справочниками и торговыми точками"""

    async def get_azs_list_v1(
        self,
        *,
        page: int = 1,
        onpage: int = 10,
        filter: AzsV1Filter | Mapping[str, object] | None = None,
        id: str | None = None,
        q: str | None = None,
    ) -> AzsListV1Response:
        """Получение списка торговых точек (АЗС, версия 1) (операция ``GET_AZS_LIST_V1``).

        Аргументы проверяются до сети.

        Позволяет получить список АЗС с фильтрацией и пагинацией.

        ``onpage=0`` по контракту возвращает все точки одним ответом. Такой ответ
        может превысить предел ``max_json_response_bytes``, и SDK прервёт чтение с
        ``ResponseTooLargeError``; для полной выгрузки листайте страницы.

        :param page: Номер страницы результата.
        :param onpage: Количество точек на странице. 0 возвращает все точки одним ответом,
            который может превысить max_json_response_bytes (ResponseTooLargeError).
        :param filter: JSON-объект для фильтрации списка торговых точек.
        :param id: ID торговой точки для получения одной детальной записи.
        :param q: Строка полнотекстового поиска.
        :return: ``AzsListV1Response``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = AzsV1Query.model_validate(
            {"page": page, "onpage": onpage, "filter": filter, "id": id, "q": q}
        )
        params = request.model_dump(exclude_none=True)
        if request.filter is not None:
            params["filter"] = to_json_param(request.filter.model_dump(exclude_none=True))

        return await self._request(
            GET_AZS_LIST_V1,
            query=params,
        )

    async def get_azs_list_v2(
        self,
        *,
        filter: AzsV2Filter | Mapping[str, object] | None = None,
        q: str | None = None,
        id: str | None = None,
        page: int | None = None,
        on_page: int | None = None,
    ) -> AzsListV2Response:
        """Получение списка торговых точек (АЗС, версия 2) (операция ``GET_AZS_LIST_V2``).

        Аргументы проверяются до сети.

        Новая версия метода с расширенной фильтрацией и улучшенной структурой ответа.

        Типовой сценарий:
            Получить доступные торговые точки перед расчётом финальных цен или
            построением маршрута.

        Пример вызова:
        ```python
        stations = await client.dictionaries.get_azs_list_v2(
            filter={"poi_types": ["AZS"]},
            q="Новосибирск",
            page=1,
            on_page=100,
        )
        ```

        Пример query-параметров:
        ```json
        {"filter": "{"poi_types": ["AZS"]}", "q": "Новосибирск", "page": 1, "on_page": 100}
        ```

        Сервер делит ответ на страницы, только когда заданы оба параметра ``page`` и
        ``on_page``; если задан один из них, SDK выдаёт ``RequestValidationError`` до
        запроса. Без обоих параметров API возвращает всю сеть АЗС одним ответом,
        который превышает предел ``max_json_response_bytes`` по умолчанию, и SDK
        прерывает чтение с ``ResponseTooLargeError``.

        Полная выгрузка: запрашивайте ``page=1, 2, …`` с ``on_page=1000``, пока не
        получите ``data.total_count`` точек, или поднимите ``max_json_response_bytes``.

        :param filter: JSON-объект для фильтрации списка торговых точек.
        :param q: Строка полнотекстового поиска.
        :param id: ID торговой точки.
        :param page: Номер страницы, начиная с 1. Задаётся вместе с on_page: сервер делит ответ
            на страницы только при обоих, поэтому один из них SDK отклоняет
            (RequestValidationError). Без обоих API возвращает всю сеть АЗС одним ответом
            (несколько тысяч точек, десятки мегабайт), больше предела max_json_response_bytes по
            умолчанию: SDK прерывает чтение с ResponseTooLargeError.
        :param on_page: Количество точек на странице. Задаётся вместе с page.
        :return: ``AzsListV2Response``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        if (page is None) != (on_page is None):
            raise RequestValidationError(
                "page и on_page задаются вместе: сервер без одного из них возвращает всю сеть АЗС"
            )
        request = AzsV2Query.model_validate(
            {"filter": filter, "q": q, "id": id, "page": page, "on_page": on_page}
        )
        params = request.model_dump(exclude_none=True)
        if request.filter is not None:
            params["filter"] = to_json_param(request.filter.model_dump(exclude_none=True))

        return await self._request(
            GET_AZS_LIST_V2,
            query=params,
        )

    async def get_azs_filters(
        self,
    ) -> AzsFiltersResponse:
        """Получить список доступных фильтров для поиска торговых точек (АЗС)

        Операция ``GET_AZS_FILTERS``.

        :return: ``AzsFiltersResponse``, данные в ``response.data``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            GET_AZS_FILTERS,
        )

    async def get_dictionary(
        self,
        *,
        name: str,
    ) -> DictionaryResponse:
        """Получить общий справочник по имени (операция ``GET_DICTIONARY``).

        Аргументы проверяются до сети.

        Примеры доступных справочников:
        - CardStatus – статусы карт
        - ContractStatus – статусы договоров
        - Country – список стран
        - Currency – список валют
        - Goods – виды топлива
        - PaymentScheme – схемы оплаты
        - PaymentTerm – условия оплаты
        - ProductGroup – группы продуктов
        - ProductType – типы продуктов
        - POIType – типы торговых точек
        - Region – регионы
        - Services – услуги на АЗС
        - Unit – единицы измерения
        - Office – офисы продаж
        - POIPartner – партнёры
        - DiscountScheme – схемы расчёта скидок

        Ещё сервер знает ``OwnType`` – принадлежность АЗС (на него ссылается фильтр
        ``get_azs_list_v1``); он отвечает с ``totalCount``, SDK принимает оба написания.

        Какой ID куда передавать: ``ProductGroup``/``ProductType`` – лимиты и товарные
        ограничители, ``Region`` – региональные ограничения, ``Office`` – ``order_cards``,
        ``Goods`` – цены АЗС и ``get_final_prices``. Актуальность записи – поле ``active``;
        в ``CardStatus`` один ``id`` бывает дважды (``active=false`` и ``true``).
        Подробно – страница «Справочники».

        Пустое ``name`` SDK отклоняет до запроса (``RequestValidationError``);
        неизвестное имя сервер отклоняет ответом ``404`` (``NotFoundError``).
        Справочника ``GoodsCode``, на который ссылается описание фильтра
        ``get_azs_list_v1``, сервер не знает (``404``).

        :param name: Наименование справочника: ``CardStatus``, ``ContractStatus``, ``Country``,
            ``Currency``, ``Goods``, ``PaymentScheme``, ``PaymentTerm``, ``ProductGroup``,
            ``ProductType``, ``POIType``, ``Region``, ``Services``, ``Unit``, ``Office``,
            ``POIPartner`` или ``DiscountScheme``.
        :return: ``DictionaryResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        params = {"name": require_identifier(name, "name")}
        return await self._request(
            GET_DICTIONARY,
            query=params,
        )
