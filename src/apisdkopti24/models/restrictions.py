from typing import Any, Literal

from pydantic import field_validator

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel


class RestrictionRequestItem(StrictRequestModel):
    """Строгий элемент запроса установки товарного ограничителя."""

    id: str | None = Field(None, min_length=1, description="ID изменяемого ограничителя")
    contract_id: str | None = Field(None, min_length=1, description="ID договора")
    card_id: str | None = Field(None, min_length=1, description="ID карты")
    group_id: str | None = Field(None, min_length=1, description="ID группы карт")
    product_type: str = Field(
        ..., alias="productType", min_length=1, description="ID типа продукта"
    )
    product_group: str | None = Field(
        None, alias="productGroup", min_length=1, description="ID группы продуктов"
    )
    restriction_type: Literal[1, 2] = Field(
        ..., description="Тип ограничителя: 1 — разрешающий, 2 — запрещающий"
    )


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
    restriction_type: int | None = Field(
        None,
        description="Тип ограничения (1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель)",
    )
    date: str = Field(
        ..., description="Дата установки ограничителя (в формате MM/DD/YYYY HH:mm:ss)"
    )


class RestrictionList(BaseModel):
    """
    Список товарных ограничителей.
    """

    total_count: int = Field(..., description="Общее количество ограничителей")
    result: list[RestrictionItem] | None = Field(None, description="Список ограничителей")


class RestrictionGetResponse(APIEnvelope[RestrictionList]):
    """
    Ответ на запрос списка ограничителей (GET /restriction).
    """


class RestrictionSetResponse(APIEnvelope[list[str]]):
    """
    Ответ на установку или изменение ограничителя (POST /setRestriction).

    API возвращает ID созданных ограничителей числами; SDK приводит их к строкам,
    как в ``get_restrictions``.
    """

    @field_validator("data", mode="before")
    @classmethod
    def numeric_ids_to_str(cls, value: Any) -> Any:
        if not isinstance(value, list):
            return value
        return [
            (
                str(restriction_id)
                if isinstance(restriction_id, int) and not isinstance(restriction_id, bool)
                else restriction_id
            )
            for restriction_id in value
        ]


class RestrictionRemoveResponse(APIEnvelope[bool]):
    """
    Ответ на удаление ограничителя (POST /removeRestriction).
    """
