from typing import Any

from ..models.dictionaries import (
    AzsFiltersResponse,
    AzsListV1Response,
    AzsListV2Response,
    DictionaryResponse,
)
from ..operations import operation
from ..service_base import _BaseService

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
        filter: dict[str, Any] | None = None,
        id: str | None = None,
        api_version: str | None = None,
    ) -> AzsListV1Response:
        """
        Получение списка торговых точек (АЗС, версия 1)

        Позволяет получить список АЗС с фильтрацией и пагинацией.
        """
        self.logger.info("Получение списка торговых точек (v1), страница %s", page)

        params: dict[str, Any] = {"page": page, "onpage": onpage}
        if filter:
            params["filter"] = filter
        if id:
            params["id"] = id

        return await self._request(
            GET_AZS_LIST_V1,
            api_version=api_version,
            params=params,
        )

    # ==========================================================
    # 🔹 Получение списка торговых точек (v2)
    # ==========================================================
    async def get_azs_list_v2(
        self,
        *,
        filter: dict[str, Any] | None = None,
        q: str | None = None,
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

        params: dict[str, Any] = {}
        if filter:
            params["filter"] = filter
        if q:
            params["q"] = q

        return await self._request(
            GET_AZS_LIST_V2,
            api_version=api_version,
            params=params,
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
            params=params,
        )
