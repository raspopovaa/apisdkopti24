from datetime import datetime

from pydantic import AliasChoices

from ..modeling import APIEnvelope, BaseModel, Field

# ============================================================
# Общие структуры
# ============================================================


class TransactionItem(BaseModel):
    """Позиция (товар) внутри транзакции."""

    id: str = Field(..., description="ID позиции транзакции")
    rrn: str = Field(..., description="Уникальный номер RRN")
    product: str = Field(..., description="Наименование продукта (топлива)")
    amount: str = Field(..., description="Количество продукта")
    price: str = Field(..., description="Цена за единицу")
    base_cost: str = Field(..., description="Базовая стоимость")
    cost: str = Field(..., description="Итоговая стоимость с учетом скидки")
    discount: str = Field(..., description="Скидка по позиции")
    discount_cost: str = Field(..., description="Стоимость с учётом скидки")
    transaction: str = Field(..., description="ID транзакции")
    currency: str = Field(..., description="Валюта")
    unit: str = Field(..., description="Единица измерения")


class RequestInfo(BaseModel):
    """Информация о типе и названии запроса."""

    type: str = Field(..., description="Тип операции (например, Advice)")
    name: str = Field(..., description="Название операции (например, Покупка)")


class TransactionV1(BaseModel):
    """Транзакция для версии v1."""

    id: str = Field(..., description="ID транзакции")
    time: datetime = Field(..., description="Дата и время транзакции")
    host_date: datetime = Field(..., description="Дата и время на хосте")
    currency: str = Field(..., description="Код валюты (например, 810)")
    card_id: str = Field(..., description="ID карты")
    service_center: str | None = Field(None, description="ID сервисного центра (АЗС)")
    card_number: str = Field(..., description="Номер карты")
    base_cost: str = Field(..., description="Базовая стоимость транзакции")
    cost: str = Field(..., description="Фактическая стоимость с учётом скидок")
    discount: str = Field(..., description="Размер скидки")
    discount_cost: str = Field(..., description="Стоимость после применения скидки")
    incoming: bool = Field(..., description="Признак входящей транзакции")
    request: RequestInfo = Field(..., description="Информация о типе операции")
    transaction_items: list[TransactionItem] | None = Field(
        None, description="Список товаров в транзакции"
    )


class TransactionItemV2(BaseModel):
    """Позиция в транзакции (v2).

    Для спорных полей здесь сознательно приоритет отдан примерам из спецификации
    и реальным ответам DEMO-стенда, а не табличным типам, которые местами
    противоречат самим же payload-примерам.
    """

    id: int | str = Field(..., description="ID транзакции")
    timestamp: datetime = Field(..., description="Время транзакции (локальное)")
    utc_time: datetime = Field(..., description="Время транзакции в UTC")
    card_id: str = Field(..., description="ID карты")
    poi_id: str = Field(..., description="ID точки продаж (АЗС)")
    terminal_id: str = Field(..., description="ID терминала")
    type: str = Field(..., description="Тип операции (P — покупка, R — возврат)")
    product_id: str = Field(..., description="ID продукта")
    product_name: str = Field(..., description="Наименование продукта")
    product_category_id: str = Field(..., description="Категория продукта (например, НП)")
    currency: str = Field(..., description="Код валюты (например, RUR)")
    check_id: int | str = Field(..., description="Номер чека")
    stor_transaction_id: int | str = Field(..., description="ID сторнируемой транзакции")
    is_storno: bool = Field(..., description="Признак сторно")
    is_manual_correction: bool = Field(
        ...,
        validation_alias=AliasChoices("is_manual_correction", "is_manual_corrention"),
        description="Признак ручной корректировки",
    )
    qty: int | float = Field(..., description="Количество")
    price: float | str = Field(..., description="Цена за единицу")
    price_no_discount: float | str = Field(..., description="Цена без скидки")
    sum: float | str = Field(..., description="Сумма с учетом скидки")
    sum_no_discount: float | str = Field(..., description="Сумма без скидки")
    discount: float | str = Field(..., description="Размер скидки")
    exchange_rate: float | str = Field(..., description="Курс обмена")
    card_number: str = Field(..., description="Номер карты")
    payment_type: str = Field(..., description="Тип оплаты (например, Карта)")

    @property
    def is_manual_corrention(self) -> bool:
        """Совместимый alias для ошибочного имени поля из спецификации 1.1.59."""
        return self.is_manual_correction


# ============================================================
# Ответы API
# ============================================================


class TransactionsV1Data(BaseModel):
    total_count: int = Field(..., description="Общее количество транзакций")
    result: list[TransactionV1] | None = Field(None, description="Список транзакций")


class TransactionsV1Response(APIEnvelope[TransactionsV1Data]):
    pass


class TransactionsV2Data(BaseModel):
    total_count: int = Field(..., description="Общее количество транзакций")
    result: list[TransactionItemV2] | None = Field(None, description="Список транзакций (v2)")


class TransactionsV2Response(APIEnvelope[TransactionsV2Data]):
    pass


class TransactionDetailItem(TransactionItemV2):
    date: str = Field(..., description="Дата транзакции")


class TransactionDetailData(BaseModel):
    total_count: int = Field(..., description="Общее количество транзакций")
    result: list[TransactionDetailItem] | None = Field(None, description="Детали транзакции")


class TransactionDetailResponse(APIEnvelope[TransactionDetailData]):
    """Ответ метода получения детальной информации по транзакции (v2)."""
