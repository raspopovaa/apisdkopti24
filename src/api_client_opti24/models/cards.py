# src/api_client_opti24/models/cards.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from ..modeling import APIEnvelope, BaseModel, Field, field_validator

# ==========================
# ИНФОРМАЦИЯ О КАРТАХ v1
# ==========================


class TransactionTimeout(BaseModel):
    type: str | int = Field(..., description="Тип таймаута ('H', 'N' или числовое значение)")
    value: str | int = Field(..., description="Значение таймаута")


class CardInfo(BaseModel):
    id: str = Field(..., description="Уникальный идентификатор карты")
    contract_id: str = Field(..., description="Идентификатор договора")
    number: str = Field(..., description="Номер топливной карты")
    status: str = Field(..., description="Статус карты (например, Active, Locked(Client))")
    can_work_offline: bool | None = Field(None, description="Может ли карта работать офлайн")
    card_auth_type: str | None = Field(None, description="Тип авторизации карты (например, PIN)")
    comment: str | None = Field(None, description="Комментарий к карте")
    date_expired: datetime | None = Field(None, description="Дата истечения срока действия карты")
    date_last_usage: datetime | None = Field(
        None, description="Дата последнего использования карты"
    )
    date_released: datetime | None = Field(None, description="Дата выпуска карты")
    servicecenter_last_usage_name: str | None = Field(
        None, description="Название последней АЗС, где использовалась карта"
    )
    transaction_last_detail: str | None = Field(
        None, description="Информация о последней транзакции"
    )
    transaction_timeout: TransactionTimeout | None = Field(
        None, description="Таймаут последней транзакции"
    )
    product: str | None = Field(None, description="Тип продукта (limit/wallet)")
    payment_of_tolls: str | None = Field(None, description="Оплата платных дорог ('Y' или 'N')")


class CardsListData(BaseModel):
    total_count: int = Field(..., description="Общее количество найденных карт")
    result: list[CardInfo] = Field(..., description="Список найденных карт")


class CardsListResponse(APIEnvelope[CardsListData]):

    @property
    def total_count(self) -> int:
        return self.data.total_count

    @property
    def result(self) -> list[CardInfo]:
        return self.data.result


# ==========================
# Информация о группе карт
# ==========================
class CardGroupInfo(BaseModel):
    id: str = Field(..., description="ID карты")
    group: str = Field(..., description="ID группы карт")
    contract_id: str = Field(..., description="ID договора")
    number: str = Field(..., description="Номер карты")
    status: str = Field(..., description="Статус карты")
    comment: str | None = Field(None, description="Комментарий")
    product: str | None = Field(None, description="Тип продукта")
    payment_of_tolls: str | None = Field(None, description="Оплата платных дорог ('Y' или 'N')")
    sync_group_state: str | None = Field(None, description="Статус синхронизации группы")


class CardGroupData(BaseModel):
    total_count: int = Field(..., description="Количество карт в группе")
    result: list[CardGroupInfo] = Field(..., description="Список карт в группе")


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
    role: str | None = Field(None, description="Роль пользователя")
    mobile_phone: str = Field(..., description="Номер телефона")
    email: str | None = Field(None, description="Email водителя")


class CardDriversData(BaseModel):
    total_count: int = Field(..., description="Количество водителей, связанных с картой")
    result: list[CardDriverInfo] = Field(..., description="Список водителей")


class CardDriversResponse(APIEnvelope[CardDriversData]):

    @property
    def total_count(self) -> int:
        return self.data.total_count

    @property
    def result(self) -> list[CardDriverInfo]:
        return self.data.result


# ==========================
# детальные данные по карте
# ==========================
class CardDetail(BaseModel):
    id: str = Field(..., description="Идентификатор карты")
    contract_id: str = Field(..., description="ID договора")
    number: str = Field(..., description="Номер карты")
    status: str = Field(..., description="Статус карты")
    can_work_offline: bool | None = Field(None, description="Может работать офлайн")
    card_auth_type: str | None = Field(None, description="Тип аутентификации карты")
    comment: str | None = Field(None, description="Комментарий к карте")
    date_last_usage: datetime | str | None | None = Field(
        None, description="Дата последнего использования (может быть пустой строкой)"
    )
    date_released: datetime | str | None | None = Field(None, description="Дата выпуска карты")
    servicecenter_last_usage_name: str | None = Field(
        None, description="Название АЗС последнего использования"
    )
    transaction_timeout: TransactionTimeout | None = Field(None, description="Таймаут транзакции")
    product: str | None = Field(None, description="Тип продукта (limit/wallet)")
    carrier: str | None = Field(None, description="Тип карты (Plastic/Virtual)")
    available: str | None = Field(None, description="Доступный лимит или баланс")
    currency: str | None = Field(None, description="Валюта")
    payment_of_tolls: str | None = Field(None, description="Признак оплаты дорожных сборов")
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
    result: list[CardDetail] = Field(..., description="Список карт")


class CardDetailResponse(APIEnvelope[CardDetailData]):
    pass


# ==========================
# блокировка/разблокировка карт и ресет пин кода
# ==========================
class BoolResponse(APIEnvelope[bool]):
    pass


class IDListResponse(APIEnvelope[list[str]]):
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
    result: list[CardV2Item] = Field(..., description="Список карт договора")


class CardsV2Response(APIEnvelope[CardsV2Data]):
    """Ответ API метода GET /v2/cards."""

    @property
    def total_count(self) -> int:
        return self.data.total_count

    @property
    def result(self) -> list[CardV2Item]:
        return self.data.result


CardsV1Response = CardsListResponse
