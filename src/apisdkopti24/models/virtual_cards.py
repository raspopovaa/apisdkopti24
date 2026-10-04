from typing import Literal

from pydantic import field_validator, model_validator

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel
from .request_parts import Identifier


class VirtualCardCreateRequest(StrictRequestModel):
    contract_id: Identifier | None = None
    template_id: Identifier | None = None
    user_id: Identifier | None = None


class VirtualCardReleaseRequest(StrictRequestModel):
    contract_id: Identifier | None = None
    type: Literal["limit", "wallet"] | None = None
    template_id: Identifier | None = None
    user_id: Identifier | None = None

    @model_validator(mode="after")
    def exactly_one_card_source(self) -> "VirtualCardReleaseRequest":
        if (self.type is None) == (self.template_id is None):
            raise ValueError("Необходимо указать ровно один параметр: type или template_id")
        return self


class MPCResetRequest(StrictRequestModel):
    type: Literal["ResetCounterCode", "ResetCounterMPC"] = "ResetCounterCode"


class PaymentQRRequest(StrictRequestModel):
    pin: str = Field(..., pattern=r"^[0-9]{4,8}$")

    @field_validator("pin", mode="before")
    @classmethod
    def validate_pin(cls, value: object) -> object:
        if not isinstance(value, str) or not value.isdigit() or not 4 <= len(value) <= 8:
            raise ValueError("pin должен содержать от 4 до 8 цифр")
        return value


class MPCInitRequest(PaymentQRRequest):
    user_id: Identifier
    device_id: str = Field(..., min_length=1, max_length=255)
    device_name: str = Field(..., min_length=11, max_length=17)


class MPCConfirmRequest(StrictRequestModel):
    code: str = Field(..., min_length=1)


class MPCUpdateRequest(PaymentQRRequest):
    new_pin: str | None = Field(None, pattern=r"^[0-9]{4,8}$")


# ======== Общие структуры ========


class StatusModel(BaseModel):
    code: int = Field(..., description="Код статуса ответа (200 — успешно, иное — ошибка)")
    errors: list[dict[str, object]] | None = Field(None, description="Массив ошибок операции")


# ======== Модели данных виртуальной карты ========


class VirtualCardData(BaseModel):
    id: str = Field(..., description="ID виртуальной карты")
    number: str | None = Field(None, description="Номер виртуальной карты")
    carrier: str | None = Field(None, description="Тип носителя, обычно 'Virtual Card'")
    product: str | None = Field(None, description="Тип продукта карты ('wallet' или 'limit')")
    status: str | None = Field(
        None, description="Статус карты (например, 'Active', 'Blocked', 'Pending')"
    )


class VirtualCardResponse(APIEnvelope[VirtualCardData]):
    """Ответ выпуска виртуальной карты: объект новой карты в ``data``."""


# ======== Упрощённый ответ с булевым результатом ========


class SimpleActionResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус выполнения операции")
    data: bool = Field(..., description="Результат операции (True — успешно)")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Сброс МПК ========


class ResetMPCResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус выполнения операции сброса")
    data: bool = Field(..., description="Результат операции (True — успешно)")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Общая модель успешного действия ========


class MPCActionResponse(APIEnvelope[bool]):
    """Ответ операции управления мобильным профилем карты."""


class MPCItem(BaseModel):
    """Выпущенный мобильный профиль карты."""

    id: str = Field(..., alias="_id", description="ID записи МПК")
    client_id: str = Field(..., description="ID клиента")
    user_id: str = Field(..., description="ID пользователя")
    login: str = Field(..., description="Логин пользователя")
    role: str = Field(..., description="Роль пользователя")
    contract_id: str = Field(..., description="ID договора")
    card_id: str = Field(..., description="ID топливной карты")
    card_number: str = Field(..., description="Номер топливной карты")
    device_id: str = Field(..., description="ID устройства")
    device_name: str = Field(..., description="Название устройства")
    tries: int = Field(..., ge=0, description="Максимальное число попыток оплаты")
    transaction_count: int = Field(..., ge=0, description="Число проведённых транзакций")
    use_mpc: bool = Field(..., description="Признак работоспособности МПК")
    updated_at: str | None = Field(None, description="Время обновления записи")
    created_at: str = Field(..., description="Время создания записи")


class MPCListData(BaseModel):
    total_count: int = Field(..., ge=0, description="Количество найденных МПК")
    result: list[MPCItem] = Field(..., description="Список выпущенных МПК")


class MPCListResponse(APIEnvelope[MPCListData]):
    """Ответ со списком выпущенных мобильных профилей."""

    @property
    def total_count(self) -> int:
        return self.data.total_count

    @property
    def result(self) -> list[MPCItem]:
        return self.data.result


class PaymentQRData(BaseModel):
    """Платёжная строка и параметры её использования."""

    code: str = Field(..., description="Платёжная строка в формате BER-TLV")
    end_date: int = Field(..., ge=0, description="Unix-время окончания действия строки")
    transaction_count: int = Field(..., ge=0, description="Число проведённых транзакций")
    tries: int = Field(..., ge=0, description="Максимальное число попыток оплаты")


class PaymentQRResponse(APIEnvelope[PaymentQRData]):
    """Ответ генерации платёжной строки для отображения как QR-код."""

    @property
    def code(self) -> str:
        return self.data.code

    @property
    def end_date(self) -> int:
        return self.data.end_date
