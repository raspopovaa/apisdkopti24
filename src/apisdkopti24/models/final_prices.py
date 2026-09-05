from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel


class FinalPriceItem(BaseModel):
    """Информация о финальной цене товара на АЗС"""

    code: str = Field(..., description="Код товарной позиции")
    price: float = Field(..., description="Финальная цена товара (с учетом всех скидок и тарифов)")


class FinalPricesData(BaseModel):
    """Основные данные о финальных ценах"""

    total_count: int = Field(..., description="Количество товарных позиций в ответе")
    goods: list[FinalPriceItem] = Field(
        ..., description="Список товарных позиций с рассчитанными финальными ценами"
    )


class FinalPricesResponse(APIEnvelope[FinalPricesData]):
    """Ответ метода получения финальных цен на АЗС"""


class PurchaseGoodItem(BaseModel):
    """Описание товарной позиции для проверки возможности покупки"""

    code: str = Field(..., description="Код товара (SKU или PLU на АЗС)")
    quantity: float = Field(..., description="Количество товара для покупки")
    price: float = Field(..., description="Цена за единицу товара")


class CheckPurchaseRequest(StrictRequestModel):
    """Параметры запроса для проверки покупки"""

    poi_id: str = Field(..., description="ID точки продажи (АЗС)")
    goods: list[PurchaseGoodItem] = Field(
        ..., description="Список товаров для проверки возможности покупки"
    )


class CheckPurchaseResponse(APIEnvelope[bool]):
    """Ответ метода проверки возможности проведения транзакции"""
