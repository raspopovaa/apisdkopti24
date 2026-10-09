from typing import Literal, Self

from pydantic import model_validator

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel
from .limits import LimitAmountRequest, LimitSumRequest, LimitTermRequest, LimitTimeRequest

# ====== ОСНОВНОЙ ШАБЛОН ВК ======


class TemplateItem(BaseModel):
    id: str = Field(..., description="Идентификатор шаблона ВК")
    name: str = Field(..., description="Название шаблона ВК")
    type: str = Field(..., description="Тип шаблона (Limit — лимитная, Wallet — электронная карта)")
    contract_id: str = Field(..., description="Идентификатор договора, к которому относится шаблон")


class TemplatesListData(BaseModel):
    total_count: int = Field(..., description="Общее количество найденных шаблонов")
    result: list[TemplateItem] | None = Field(
        default=None, description="Список найденных шаблонов ВК"
    )


class TemplatesListResponse(APIEnvelope[TemplatesListData]):
    pass


class TemplateCreateRequest(StrictRequestModel):
    contract_id: str | None = Field(
        default=None, min_length=1, description="Идентификатор договора"
    )
    type: Literal["Limit", "Wallet"] = Field(..., description="Тип создаваемого шаблона")
    # Сервер принимает имя не длиннее 30 символов.
    name: str = Field(
        ..., min_length=1, max_length=30, description="Имя (название) нового шаблона ВК"
    )


class TemplateCreateResponse(APIEnvelope[str]):
    pass


class TemplateDeleteResponse(APIEnvelope[bool]):
    pass


# ====== ЛИМИТЫ ШАБЛОНОВ ======


class LimitSum(BaseModel):
    currency: str = Field(..., description="Код валюты (например, '810')")
    currencyName: str | None = Field(default=None, description="Название валюты (например, 'р.')")
    value: float = Field(..., description="Сумма лимита в указанной валюте")


class LimitAmount(BaseModel):
    unit: str = Field(..., description="Единица измерения (например, 'LIT')")
    value: float = Field(..., description="Количество или объем в единицах измерения")


class LimitTime(BaseModel):
    type: int = Field(..., description="Тип периода лимита (например, 3 — день, 5 — месяц)")
    number: int = Field(
        ..., description="Количество единиц периода; API присылает строку, SDK приводит её к int"
    )


class LimitTermTime(BaseModel):
    from_: str | None = Field(
        default=None,
        alias="from",
        description="Начало временного диапазона (например, '03:00')",
    )
    to: str | None = Field(
        default=None, description="Конец временного диапазона (например, '08:00')"
    )


class LimitTerm(BaseModel):
    days: str | None = Field(
        default=None, description="Маска дней действия лимита (например, '1111100')"
    )
    type: int = Field(..., description="Тип временного ограничения")
    time: LimitTermTime | None = Field(default=None, description="Временные границы лимита")


class LimitTransactions(BaseModel):
    count: int = Field(..., description="Количество транзакций, на которое распространяется лимит")


class TemplateLimit(BaseModel):
    id: str = Field(..., description="Идентификатор лимита шаблона")
    template_id: str = Field(..., description="Идентификатор шаблона, которому принадлежит лимит")
    contract_id: str = Field(
        ..., description="Идентификатор договора, на который распространяется лимит"
    )
    amount: LimitAmount | None = Field(default=None, description="Объемный лимит (в литрах и т.д.)")
    sum: LimitSum | None = Field(default=None, description="Суммовой лимит (в рублях и т.д.)")
    time: LimitTime = Field(..., description="Период действия лимита")
    term: LimitTerm = Field(..., description="Дополнительные временные ограничения")
    transactions: LimitTransactions = Field(..., description="Информация по транзакциям лимита")
    date: str = Field(..., description="Дата создания лимита (MM/DD/YYYY HH:MM:SS)")
    productType: str = Field(..., description="Тип продукта (топливо, услуга и т.д.)")
    productGroup: str | None = Field(default=None, description="Группа продукта (например, G-95)")
    productTypeName: str = Field(..., description="Название типа продукта")
    productGroupName: str | None = Field(default=None, description="Название группы продукта")


class TemplateLimitListData(BaseModel):
    total_count: int = Field(..., description="Количество найденных лимитов")
    result: list[TemplateLimit] | None = Field(default=None, description="Список лимитов шаблона")


class TemplateLimitListResponse(APIEnvelope[TemplateLimitListData]):
    pass


class TemplateLimitCreateRequest(StrictRequestModel):
    contract_id: str | None = Field(
        default=None, min_length=1, description="Идентификатор договора"
    )
    product_type: str = Field(..., description="Тип продукта (например, '1-276PF01')")
    product_group: str | None = Field(
        default=None, description="Группа продукта (например, '1-276PF0E')"
    )
    # Поля sum, amount, time и term описаны в спецификации так же, как у лимитов карт.
    sum: LimitSumRequest | None = Field(default=None, description="Суммовой лимит")
    amount: LimitAmountRequest | None = Field(default=None, description="Объемный лимит")
    time: LimitTimeRequest = Field(..., description="Период лимита")
    term: LimitTermRequest | None = Field(
        default=None, description="Дополнительные временные ограничения"
    )
    create_restriction: bool | None = Field(
        default=None, description="Создать ограничитель автоматически"
    )

    @model_validator(mode="after")
    def require_amount_or_sum(self) -> Self:
        if self.amount is None and self.sum is None:
            raise ValueError("Необходимо указать amount или sum")
        return self


class TemplateLimitCreateResponse(APIEnvelope[str]):
    pass


class TemplateLimitDeleteResponse(APIEnvelope[bool]):
    pass


# ====== ОГРАНИЧИТЕЛИ ШАБЛОНА ======


class TemplateRestriction(BaseModel):
    id: str = Field(..., description="Идентификатор ограничителя шаблона")
    template_id: str = Field(..., description="Идентификатор шаблона")
    contract_id: str = Field(..., description="Идентификатор договора")
    date: str = Field(..., description="Дата создания ограничителя (MM/DD/YYYY HH:MM:SS)")
    productType: str = Field(..., description="Тип продукта")
    productGroup: str | None = Field(default=None, description="Группа продукта")
    productTypeName: str = Field(..., description="Название типа продукта")
    productGroupName: str | None = Field(default=None, description="Название группы продукта")
    restriction_type: int = Field(..., description="Тип ограничителя (1 — разрешение, 2 — запрет)")


class TemplateRestrictionListData(BaseModel):
    total_count: int = Field(..., description="Количество найденных ограничителей")
    result: list[TemplateRestriction] | None = Field(
        default=None, description="Список ограничителей шаблона"
    )


class TemplateRestrictionListResponse(APIEnvelope[TemplateRestrictionListData]):
    pass


class TemplateRestrictionCreateRequest(StrictRequestModel):
    contract_id: str | None = Field(
        default=None, min_length=1, description="Идентификатор договора"
    )
    product_type: str = Field(..., description="Тип продукта (например, '1-276PF01')")
    product_group: str | None = Field(
        default=None, description="Группа продукта (например, '1-276PF0E')"
    )
    restriction_type: Literal[1, 2] = Field(..., description="Тип ограничителя")


class TemplateRestrictionCreateResponse(APIEnvelope[str]):
    pass


class TemplateRestrictionDeleteResponse(APIEnvelope[bool]):
    pass


# ====== ГЕООГРАНИЧИТЕЛИ ШАБЛОНА ======


class TemplateGeoRestriction(BaseModel):
    id: str = Field(..., description="Идентификатор геоограничителя шаблона")
    template_id: str = Field(..., description="Идентификатор шаблона")
    contract_id: str = Field(..., description="Идентификатор договора")
    date: str = Field(..., description="Дата создания записи (MM/DD/YYYY HH:MM:SS)")
    country: str = Field(..., description="Код страны (например, 'RUS')")
    countryName: str = Field(..., description="Название страны")
    region: str | None = Field(default=None, description="Код региона")
    regionName: str | None = Field(default=None, description="Название региона")
    partner: str | None = Field(default=None, description="Код партнера (АЗС)")
    partnerName: str | None = Field(default=None, description="Название партнера (АЗС)")
    service_center: str | None = Field(default=None, description="Код сервисного центра")
    service_centerName: str | None = Field(default=None, description="Название сервисного центра")
    restriction_type: int = Field(
        ..., description="Тип геоограничителя (1 — разрешение, 2 — запрет)"
    )


class TemplateGeoRestrictionListData(BaseModel):
    total_count: int = Field(..., description="Количество найденных геоограничителей")
    result: list[TemplateGeoRestriction] | None = Field(
        default=None, description="Список геоограничителей шаблона"
    )


class TemplateGeoRestrictionListResponse(APIEnvelope[TemplateGeoRestrictionListData]):
    pass


class TemplateGeoRestrictionCreateRequest(StrictRequestModel):
    contract_id: str | None = Field(
        default=None, min_length=1, description="Идентификатор договора"
    )
    country: str = Field(..., description="Код страны (например, 'RUS')")
    region: str | None = Field(default=None, description="Код региона (например, '45')")
    partner: str | None = Field(default=None, description="Код партнера (АЗС)")
    service_center: str | None = Field(default=None, description="Код сервисного центра")
    restriction_type: Literal[1, 2] = Field(..., description="Тип геоограничителя")


class TemplateGeoRestrictionCreateResponse(APIEnvelope[str]):
    pass


class TemplateGeoRestrictionDeleteResponse(APIEnvelope[bool]):
    pass
