from typing import Any

from ..models.final_prices import (
    CheckPurchaseRequest,
    CheckPurchaseResponse,
    FinalPricesResponse,
)
from ..operations import operation
from ..service_base import _BaseService

GET_FINAL_PRICES = operation("get_final_prices", FinalPricesResponse)
CHECK_PURCHASE = operation("check_purchase", CheckPurchaseResponse)


class FinalPricesService(_BaseService):
    """
    Методы для получения финальных цен и проверки покупок по карте.
    """

    async def get_final_prices(
        self,
        *,
        card_id: str,
        poi_id: str,
        goods: list[str],
        api_version: str | None = None,
    ) -> FinalPricesResponse:
        """
        Получение финальных цен на АЗС по карте (POST /vip/v2/cards/{card_id}/calculatePrices)

        Типовой сценарий:
            Перед оплатой получить персональные цены для выбранной карты,
            торговой точки и перечня товаров.

        Пример вызова:
        ```python
        prices = await client.final_prices.get_final_prices(
            card_id="card-id",
            poi_id="poi-id",
            goods=["fuel-code-1", "fuel-code-2"],
        )
        ```

        Пример payload:
        ```json
        {"poi_id": "poi-id", "goods": ["fuel-code-1", "fuel-code-2"]}
        ```
        """
        payload = {"poi_id": poi_id, "goods": goods}
        self.logger.info("Requesting final prices")

        return await self._request(
            GET_FINAL_PRICES,
            api_version=api_version,
            path_params={"card_id": card_id},
            data=payload,
        )

    async def check_purchase(
        self,
        *,
        card_id: str,
        poi_id: str,
        goods: list[dict[str, Any]],
        api_version: str | None = None,
    ) -> CheckPurchaseResponse:
        """
        Проверка возможности проведения транзакции по карте
        (POST /vip/v2/cards/{card_id}/checkPurchase)
        """
        request = CheckPurchaseRequest.model_validate({"poi_id": poi_id, "goods": goods})
        self.logger.info("Checking purchase availability")

        return await self._request(
            CHECK_PURCHASE,
            api_version=api_version,
            path_params={"card_id": card_id},
            data=request.model_dump(by_alias=True),
        )
