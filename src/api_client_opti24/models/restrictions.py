from typing import Literal

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel


class RestrictionRequestItem(StrictRequestModel):
    """Строгий элемент запроса установки товарного ограничителя."""

    id: str | None = Field(None, min_length=1)
    contract_id: str | None = Field(None, min_length=1)
    card_id: str | None = Field(None, min_length=1)
    group_id: str | None = Field(None, min_length=1)
    product_type: str = Field(..., alias="productType", min_length=1)
    product_group: str | None = Field(None, alias="productGroup", min_length=1)
    restriction_type: Literal[1, 2]


class RestrictionItem(BaseModel):
    """
    Модель одного товарного ограничителя (ограничение по продукту).
    """

    id: str = Field(..., description="ID ограничителя")
    card_id: str | None = Field(None, description="ID карты, если ограничитель задан для карты")
    group_id: str | None = Field(
        None, description="ID группы карт, если ограничитель задан для группы"
    )
    contract_id: str = Field(..., description="ID договора")
    productType: str | None = Field(None, description="ID типа продукта (например, '1-CK231')")
    productGroup: str | None = Field(None, description="ID группы продуктов (если применимо)")
    productTypeName: str | None = Field(None, description="Название типа продукта")
    productGroupName: str | None = Field(None, description="Название группы продуктов")
    restriction_type: int = Field(
        ...,
        description="Тип ограничения (1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель)",
    )
    date: str | None = Field(
        None, description="Дата установки ограничителя (в формате MM/DD/YYYY HH:mm:ss)"
    )


class RestrictionList(BaseModel):
    """
    Список товарных ограничителей.
    """

    total_count: int = Field(..., description="Общее количество ограничителей")
    result: list[RestrictionItem] = Field(..., description="Список ограничителей")


class RestrictionGetResponse(APIEnvelope[RestrictionList]):
    """
    Ответ на запрос списка ограничителей (GET /restriction).
    """


class RestrictionSetResponse(APIEnvelope[list[str]]):
    """
    Ответ на установку или изменение ограничителя (POST /setRestriction).
    """


class RestrictionRemoveResponse(APIEnvelope[bool]):
    """
    Ответ на удаление ограничителя (POST /removeRestriction).
    """
