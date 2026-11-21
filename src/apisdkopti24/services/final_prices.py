from typing import Any

from ..models.final_prices import (
    CheckPurchaseRequest,
    CheckPurchaseResponse,
    FinalPricesResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import require_identifier, validate_identifier_list

GET_FINAL_PRICES = operation("get_final_prices", FinalPricesResponse)
CHECK_PURCHASE = operation("check_purchase", CheckPurchaseResponse)


class FinalPricesService(_BaseService):
    """Методы для получения финальных цен и проверки покупок по карте."""

    async def get_final_prices(
        self,
        *,
        card_id: str,
        poi_id: str,
        goods: list[str],
        contract_id: str | None = None,
    ) -> FinalPricesResponse:
        """Получение финальных цен на АЗС по карте (операция ``GET_FINAL_PRICES``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Типовой сценарий:
            Перед оплатой получить персональные цены для выбранной карты,
            торговой точки и перечня товаров.

        Пример вызова:
        ```python
        prices = await client.final_prices.get_final_prices(
            card_id="card-id",
            poi_id="poi-id",
            goods=["00000000000004", "00000000000006"],
        )
        ```

        ``goods`` — коды из справочника ``Goods`` (АИ-92 ``00000000000004``, ДТ
        ``00000000000006``), те же, что в ``prices[].GoodsCode`` списка АЗС. ID категории
        из ``ProductType`` (``1-CK231``) сервер отклоняет: ``400`` «Услуга не найдена».
        При нехватке средств на договоре ответ ``403`` с кодом процессинга ``51``
        (``ProcessingRefusalError``). См. «Справочники» в документации.

        Тело запроса (JSON; в форме сервер не принимает ``goods`` как массив):
        ```json
        {"poi_id": "poi-id", "goods": ["00000000000004", "00000000000006"]}
        ```

        :param card_id: Идентификатор топливной карты.
        :param poi_id: ID точки обслуживания.
        :param goods: Массив идентификаторов продуктов.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``FinalPricesResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        payload = {
            "poi_id": require_identifier(poi_id, "poi_id"),
            "goods": validate_identifier_list(goods, "goods"),
        }
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_FINAL_PRICES,
            path_params={"card_id": wire_card_id},
            json_body=payload,
            contract_header=cid,
        )

    async def check_purchase(
        self,
        *,
        card_id: str,
        poi_id: str,
        goods: list[dict[str, Any]],
        contract_id: str | None = None,
    ) -> CheckPurchaseResponse:
        """Проверка возможности проведения транзакции по карте (операция ``CHECK_PURCHASE``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        :param card_id: Идентификатор топливной карты.
        :param poi_id: ID точки обслуживания.
        :param goods: Массив данных о товарах; для каждого товара указываются ``code``,
            ``quantity`` и ``price``.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``CheckPurchaseResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        request = CheckPurchaseRequest.model_validate({"poi_id": poi_id, "goods": goods})
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            CHECK_PURCHASE,
            path_params={"card_id": wire_card_id},
            json_body=request.model_dump(by_alias=True),
            contract_header=cid,
        )
