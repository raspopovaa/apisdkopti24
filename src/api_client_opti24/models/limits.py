from __future__ import annotations

from typing import Literal

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel

# === Базовые структуры ===


class LimitAmount(BaseModel):
    """Объёмный лимит (например, литры)."""

    value: float = Field(..., description="Установленное значение лимита")
    used: float | None = Field(None, description="Использованное значение лимита")
    unit: str = Field(..., description="Единица измерения (например, 'LIT' или 'RUB')")


class LimitSum(BaseModel):
    """Денежный лимит."""

    currency: str = Field(..., description="Код валюты (например, 810)")
    value: float = Field(..., description="Сумма лимита")


class LimitTermTime(BaseModel):
    """Временной диапазон действия лимита."""

    from_: str = Field(..., alias="from", description="Время начала действия лимита (HH:MM)")
    to: str = Field(..., description="Время окончания действия лимита (HH:MM)")


class LimitTerm(BaseModel):
    """Периодичность и временные ограничения."""

    days: str | None = Field(None, description="Дни недели (например, '1111100' для Пн–Пт)")
    type: int | None = Field(None, description="Тип периода (1 — будни, 2 — ежедневно и т.д.)")
    time: LimitTermTime | None = Field(None, description="Временной диапазон действия")


class LimitTransactions(BaseModel):
    """Ограничения по количеству транзакций."""

    count: int | None = Field(None, description="Максимальное количество транзакций")
    occured: int | None = Field(None, description="Фактическое количество транзакций")


class LimitTime(BaseModel):
    """Периодичность сброса лимита."""

    number: int | None = Field(None, description="Период в числовом виде (например, 3)")
    type: int | None = Field(None, description="Тип периода (например, 7 — неделя)")


class LimitAmountRequest(StrictRequestModel):
    unit: str = Field(..., min_length=1, description="Единица измерения")
    value: float = Field(..., gt=0, description="Размер объёмного лимита")


class LimitSumRequest(StrictRequestModel):
    currency: str = Field(..., min_length=1, description="Код валюты")
    value: float = Field(..., gt=0, description="Размер денежного лимита")


class LimitTimeRequest(StrictRequestModel):
    number: int = Field(..., gt=0, description="Количество периодов")
    type: Literal[2, 3, 4, 5, 6, 7] = Field(..., description="Тип периода")


class LimitTermTimeRequest(StrictRequestModel):
    from_: str = Field(..., alias="from", min_length=1, description="Начало интервала")
    to: str = Field(..., min_length=1, description="Окончание интервала")


class LimitTermRequest(StrictRequestModel):
    days: str | None = Field(None, pattern=r"^[01]{7}$", description="Маска дней недели")
    type: Literal[1, 2, 3] = Field(..., description="Тип применения ограничения")
    time: LimitTermTimeRequest | None = Field(None, description="Интервал обслуживания")


class LimitTransactionsRequest(StrictRequestModel):
    count: int = Field(..., gt=0, description="Количество транзакций")


class LimitRequestItem(StrictRequestModel):
    """Строгий элемент запроса установки продуктового лимита."""

    id: str | None = Field(None, min_length=1, description="ID изменяемого лимита")
    contract_id: str | None = Field(None, min_length=1, description="ID договора")
    card_id: str | None = Field(None, min_length=1, description="ID карты")
    group_id: str | None = Field(None, min_length=1, description="ID группы карт")
    product_type: str | None = Field(None, alias="productType", min_length=1)
    product_group: str | None = Field(None, alias="productGroup", min_length=1)
    amount: LimitAmountRequest | None = None
    sum: LimitSumRequest | None = None
    term: LimitTermRequest | None = None
    transactions: LimitTransactionsRequest | None = None
    time: LimitTimeRequest = Field(..., description="Период действия лимита")


# === Основная модель лимита ===


class LimitItem(BaseModel):
    """Продуктовый лимит (карта, группа или договор)."""

    id: str | None = Field(None, description="ID лимита (для изменения — обязателен)")
    card_id: str | None = Field(None, description="ID карты, если лимит задан для карты")
    group_id: str | None = Field(None, description="ID группы карт, если лимит задан для группы")
    contract_id: str = Field(..., description="ID договора, к которому относится лимит")

    productGroup: str | None = Field(None, description="ID группы продуктов")
    productType: str | None = Field(None, description="ID типа продукта")

    amount: LimitAmount | None = Field(None, description="Ограничение по объёму (литры и т.д.)")
    sum: LimitSum | None = Field(None, description="Ограничение по сумме в валюте договора")

    term: LimitTerm | None = Field(None, description="Периодичность и временные ограничения")
    transactions: LimitTransactions | None = Field(
        None, description="Ограничения по количеству транзакций"
    )
    time: LimitTime | None = Field(None, description="Периодичность сброса лимита")

    date: str | None = Field(None, description="Дата создания лимита (формат dd/mm/yyyy hh:mm:ss)")


# === Ответ на GET /limit ===


class LimitsData(BaseModel):
    """Данные по лимитам."""

    total_count: int = Field(..., description="Общее количество лимитов")
    result: list[LimitItem] = Field(..., description="Список лимитов")


class LimitsResponse(APIEnvelope[LimitsData]):
    """Ответ на запрос списка лимитов."""


# === Ответ на POST /removeLimit ===


class RemoveLimitResponse(APIEnvelope[bool]):
    """Ответ на удаление продуктового лимита."""


# === Ответ на POST /setLimit ===


class SetLimitResponse(APIEnvelope[list[str]]):
    """Ответ на установку/изменение продуктового лимита."""
