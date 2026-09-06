from collections.abc import Mapping

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

GET_AZS_LIST_V1 = operation("get_azs_list_v1", AzsListV1Response)
GET_AZS_LIST_V2 = operation("get_azs_list_v2", AzsListV2Response)
GET_AZS_FILTERS = operation("get_azs_filters", AzsFiltersResponse)
GET_DICTIONARY = operation("get_dictionary", DictionaryResponse)


class DictionariesService(_BaseService):
    """Методы для работы со справочниками и торговыми точками"""

    # ==========================================================
    # 🔹 Получение списка торговых точек (v1)
    # ==========================================================
    async def get_azs_list_v1(
        self,
        *,
        page: int = 1,
        onpage: int = 10,
        filter: AzsV1Filter | Mapping[str, object] | None = None,
        id: str | None = None,
        q: str | None = None,
        api_version: str | None = None,
    ) -> AzsListV1Response:
        """
        Получение списка торговых точек (АЗС, версия 1)

        Позволяет получить список АЗС с фильтрацией и пагинацией.
        """
        self.logger.info("Получение списка торговых точек (v1), страница %s", page)

        request = AzsV1Query.model_validate(
            {"page": page, "onpage": onpage, "filter": filter, "id": id, "q": q}
        )
        params = request.model_dump(exclude_none=True)
        if request.filter is not None:
            params["filter"] = to_json_param(request.filter.model_dump(exclude_none=True))

        return await self._request(
            GET_AZS_LIST_V1,
            api_version=api_version,
            query=params,
        )

    # ==========================================================
    # 🔹 Получение списка торговых точек (v2)
    # ==========================================================
    async def get_azs_list_v2(
        self,
        *,
        filter: AzsV2Filter | Mapping[str, object] | None = None,
        q: str | None = None,
        id: str | None = None,
        page: int | None = None,
        on_page: int | None = None,
        api_version: str | None = None,
    ) -> AzsListV2Response:
        """
        Получение списка торговых точек (АЗС, версия 2)

        Новая версия метода с расширенной фильтрацией и улучшенной структурой ответа.

        Типовой сценарий:
            Получить доступные торговые точки перед расчётом финальных цен или
            построением маршрута.

        Пример вызова:
        ```python
        stations = await client.dictionaries.get_azs_list_v2(
            filter={"services": ["fuel"]},
            q="Новосибирск",
        )
        ```

        Пример query-параметров:
        ```json
        {"filter": {"services": ["fuel"]}, "q": "Новосибирск"}
        ```
        """
        self.logger.info("Получение списка торговых точек (v2) с фильтрацией: %s", filter)

        request = AzsV2Query.model_validate(
            {"filter": filter, "q": q, "id": id, "page": page, "on_page": on_page}
        )
        params = request.model_dump(exclude_none=True)
        if request.filter is not None:
            params["filter"] = to_json_param(request.filter.model_dump(exclude_none=True))

        return await self._request(
            GET_AZS_LIST_V2,
            api_version=api_version,
            query=params,
        )

    # ==========================================================
    # 🔹 Получение списка фильтров торговых точек
    # ==========================================================
    async def get_azs_filters(
        self,
        *,
        api_version: str | None = None,
    ) -> AzsFiltersResponse:
        """
        Получить список доступных фильтров для поиска торговых точек (АЗС)
        """
        self.logger.info("Получение списка фильтров торговых точек")

        response = await self._request(
            GET_AZS_FILTERS,
            api_version=api_version,
        )

        # У метода data — это словарь с результатом фильтров
        self.logger.info("Dictionary filters received")
        return response

    # ==========================================================
    # 🔹 Получение общего справочника
    # ==========================================================
    async def get_dictionary(
        self,
        *,
        name: str,
        api_version: str | None = None,
    ) -> DictionaryResponse:
        """
        Получить общий справочник по имени.

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
        """
        self.logger.info("Получение справочника: %s", name)

        params = {"name": name}

        return await self._request(
            GET_DICTIONARY,
            api_version=api_version,
            query=params,
        )
