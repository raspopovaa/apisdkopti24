# src/apisdkopti24/models/cards.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices

from ..modeling import (
    APIEnvelope,
    BaseModel,
    Field,
    StrictRequestModel,
    field_validator,
)
from .request_parts import Identifier, PositivePage


class CardsV2Query(StrictRequestModel):
    """Параметры GET /vip/v2/cards из спецификации 1.1.60."""

    contract_id: Identifier | None = None
    group_id: Identifier | None = None
    sort: str = Field("-id", min_length=1)
    q: str | None = None
    status: str | None = None
    carrier: str | None = None
    platon: bool | None = None
    avtodor: bool | None = None
    users: bool | None = None
    page: PositivePage | None = None
    onpage: PositivePage | None = None


class BlockCardRequest(StrictRequestModel):
    contract_id: Identifier
    card_id: list[Identifier] = Field(..., min_length=1)
    block: bool = True


class SetCardCommentRequest(StrictRequestModel):
    card_id: Identifier
    contract_id: Identifier
    comment: str = Field(..., min_length=1)


class ResetPinRequest(StrictRequestModel):
    code: str = Field(..., min_length=1)


# ==========================
# ИНФОРМАЦИЯ О КАРТАХ v1
# ==========================


class TransactionTimeout(BaseModel):
    type: int | str = Field(..., description="Тип таймаута ('H', 'N' или числовое значение)")
    value: int | str = Field(..., description="Значение таймаута")


class CardInfo(BaseModel):
    id: str = Field(..., description="Уникальный идентификатор карты")
    contract_id: str = Field(..., description="Идентификатор договора")
    number: str = Field(..., description="Номер топливной карты")
    status: str = Field(..., description="Статус карты (например, Active, Locked(Client))")
    can_work_offline: bool = Field(..., description="Может ли карта работать офлайн")
    card_auth_type: str = Field(..., description="Тип авторизации карты (например, PIN)")
    comment: str | None = Field(None, description="Комментарий к карте")
    date_expired: datetime = Field(..., description="Дата истечения срока действия карты")
    date_last_usage: datetime | None = Field(
        None, description="Дата последнего использования карты"
    )
    date_released: datetime | None = Field(None, description="Дата выпуска карты")
    servicecenter_last_usage_name: str | None = Field(
        None,
        validation_alias=AliasChoices("servicecenter_last_usage_name", "servicecenter_last_usage"),
        description="Название последней АЗС, где использовалась карта",
    )
    transaction_last_detail: str | None = Field(
        None, description="Информация о последней транзакции"
    )
    transaction_timeout: TransactionTimeout | None = Field(
        None, description="Таймаут последней транзакции"
    )
    product: str = Field(..., description="Тип продукта (limit/wallet)")
    payment_of_tolls: str = Field(..., description="Оплата платных дорог ('Y' или 'N')")


class CardsListData(BaseModel):
    total_count: int = Field(..., description="Общее количество найденных карт")
    result: list[CardInfo] | None = Field(None, description="Список найденных карт")


class CardsListResponse(APIEnvelope[CardsListData]):

    @property
    def total_count(self) -> int:
        return self.data.total_count

    @property
    def result(self) -> list[CardInfo]:
        return self.data.result or []


# ==========================
# Информация о группе карт
# ==========================
class CardGroupInfo(BaseModel):
    id: str = Field(..., description="ID карты")
    group: str | None = Field(None, description="ID группы карт")
    contract_id: str = Field(..., description="ID договора")
    number: str = Field(..., description="Номер карты")
    status: str = Field(..., description="Статус карты")
    comment: str | None = Field(None, description="Комментарий")
    product: str = Field(..., description="Тип продукта")
    payment_of_tolls: str = Field(..., description="Оплата платных дорог ('Y' или 'N')")
    sync_group_state: str | None = Field(None, description="Статус синхронизации группы")


class CardGroupData(BaseModel):
    total_count: int = Field(..., description="Количество карт в группе")
    result: list[CardGroupInfo] | None = Field(None, description="Список карт в группе")


class CardGroupResponse(APIEnvelope[CardGroupData]):
    pass


# ==========================
# водители, связанные с картой
# ==========================
class CardDriverInfo(BaseModel):
    id: str = Field(..., description="ID пользователя/водителя")
    login: str = Field(..., description="Логин (обычно телефон)")
    first_name: str = Field(..., description="Имя водителя")
    last_name: str = Field(..., description="Фамилия водителя")
    middle_name: str | None = Field(None, description="Отчество водителя")
    date: str | None = Field(None, description="Дата рождения или дата регистрации")
    position: str | None = Field(None, description="Должность водителя")
    role: str = Field(..., description="Роль пользователя")
    mobile_phone: str = Field(..., description="Номер телефона")
    email: str | None = Field(None, description="Email водителя")


class CardDriversData(BaseModel):
    total_count: int = Field(..., description="Количество водителей, связанных с картой")
    result: list[CardDriverInfo] | None = Field(None, description="Список водителей")


class CardDriversResponse(APIEnvelope[CardDriversData]):

    @property
    def total_count(self) -> int:
        return self.data.total_count

    @property
    def result(self) -> list[CardDriverInfo]:
        return self.data.result or []


# ==========================
# детальные данные по карте
# ==========================
class CardDetail(BaseModel):
    id: str = Field(..., description="Идентификатор карты")
    contract_id: str = Field(..., description="ID договора")
    number: str = Field(..., description="Номер карты")
    status: str = Field(..., description="Статус карты")
    can_work_offline: bool = Field(..., description="Может работать офлайн")
    card_auth_type: str = Field(..., description="Тип аутентификации карты")
    comment: str | None = Field(None, description="Комментарий к карте")
    date_last_usage: datetime | str | None | None = Field(
        None, description="Дата последнего использования (может быть пустой строкой)"
    )
    date_released: datetime | str | None | None = Field(None, description="Дата выпуска карты")
    servicecenter_last_usage_name: str | None = Field(
        None,
        validation_alias=AliasChoices("servicecenter_last_usage_name", "servicecenter_last_usage"),
        description="Название АЗС последнего использования",
    )
    transaction_timeout: TransactionTimeout | None = Field(None, description="Таймаут транзакции")
    product: str = Field(..., description="Тип продукта (limit/wallet)")
    carrier: str = Field(..., description="Тип карты (Plastic/Virtual)")
    available: str = Field(..., description="Доступный лимит или баланс")
    currency: str = Field(..., description="Валюта")
    payment_of_tolls: str = Field(..., description="Признак оплаты дорожных сборов")
    mpc: bool = Field(..., description="Признак доступности мобильного профиля карты")
    pin_reset: int = Field(..., description="Количество доступных попыток сброса PIN")
    pin_counter: int = Field(..., description="Счётчик попыток ввода PIN")
    previous: str | None = Field(None, description="ID предыдущей карты")
    next: str | None = Field(None, description="ID следующей карты")

    @field_validator("date_last_usage", "date_released", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any) -> Any:
        if v in ("", None):
            return None
        return v


class CardDetailData(BaseModel):
    total_count: int = Field(..., description="Количество записей")
    result: list[CardDetail] | None = Field(None, description="Список карт")


class CardDetailResponse(APIEnvelope[CardDetailData]):
    pass


# ==========================
# блокировка/разблокировка карт и ресет пин кода
# ==========================
class BoolResponse(APIEnvelope[bool]):
    pass


class IDListResponse(APIEnvelope[list[str] | None]):
    data: list[str] | None = Field(None, description="Список идентификаторов обработанных карт")
    pass


# ==========================
# список карт (v2)
# ==========================


class CardV2Item(BaseModel):
    """Информация об одной топливной карте договора."""

    id: str = Field(..., description="Уникальный идентификатор карты")
    group_id: str | None = Field(None, description="ID группы карт, если назначена")
    group_name: str | None = Field(None, description="Название группы карт")
    contract_id: str = Field(..., description="ID договора, к которому принадлежит карта")
    contract_name: str = Field(..., description="Название договора")
    number: str = Field(..., description="Номер топливной карты")
    status: str = Field(..., description="Системное значение статуса карты")
    status_name: str | None = Field(
        None, description="Отображаемое имя статуса (например 'Активна')"
    )
    comment: str | None = Field(None, description="Комментарий, установленный пользователем")
    product: str = Field(..., description="Тип продукта, например 'limit' или 'wallet'")
    product_name: str | None = Field(None, description="Отображаемое имя продукта")
    carrier: str = Field(..., description="Тип носителя карты ('Plastic' или 'Virtual Card')")
    carrier_name: str | None = Field(None, description="Название типа носителя карты")
    platon: bool = Field(..., description="Признак наличия поддержки Platon (оплата проезда)")
    avtodor: bool = Field(..., description="Признак наличия поддержки Автодора")
    sync_group_state: str | None = Field(None, description="Состояние синхронизации группы карт")
    users: list[str] | None = Field(
        default_factory=list, description="Список ID пользователей, привязанных к карте"
    )
    mpc: bool | None = Field(None, description="Признак наличия мультипроцессингового центра (mpc)")


class CardsV2Data(BaseModel):
    """Основной объект данных для списка карт (v2)."""

    total_count: int = Field(..., description="Общее количество найденных карт")
    result: list[CardV2Item] | None = Field(None, description="Список карт договора")


class CardsV2Response(APIEnvelope[CardsV2Data]):
    """Ответ API метода GET /v2/cards."""

    @property
    def total_count(self) -> int:
        return self.data.total_count

    @property
    def result(self) -> list[CardV2Item]:
        return self.data.result or []


CardsV1Response = CardsListResponse
