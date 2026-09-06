from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel

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


class VirtualCardResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус ответа от сервера")
    data: VirtualCardData = Field(..., description="Информация о выпущенной виртуальной карте")
    timestamp: int | None = Field(None, description="Время ответа сервера в формате Unix Timestamp")


# ======== Упрощённый ответ с булевым результатом ========


class SimpleActionResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус выполнения операции")
    data: bool = Field(..., description="Результат операции (True — успешно)")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Подтверждение выпуска ВК (через СМС) ========


class ConfirmVirtualCardRequest(StrictRequestModel):
    card_id: str = Field(..., description="ID виртуальной карты для подтверждения выпуска")
    code: str = Field(..., description="Код подтверждения из СМС")


class ConfirmVirtualCardResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус подтверждения выпуска")
    data: bool = Field(..., description="Результат подтверждения (True — успешно)")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Повторная отправка СМС-кода ========


class ResendSMSRequest(StrictRequestModel):
    card_id: str = Field(
        ...,
        description="ID виртуальной карты, для которой нужно повторно отправить СМС-код",
    )


class ResendSMSResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус запроса на повторную отправку СМС-кода")
    data: bool = Field(..., description="Результат операции (True — СМС отправлено успешно)")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Удаление МПК ========


class DeleteMPCResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус удаления мобильного профиля карты (МПК)")
    data: bool = Field(..., description="Результат удаления (True — успешно)")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Сброс МПК ========


class ResetMPCRequest(StrictRequestModel):
    type: str = Field(..., description="Тип операции сброса ('ResetCounterCode' и т.п.)")


class ResetMPCResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус выполнения операции сброса")
    data: bool = Field(..., description="Результат операции (True — успешно)")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Перезапуск выпуска (повторная генерация ВК) ========


class RerunVirtualCardReleaseRequest(StrictRequestModel):
    card_id: str = Field(..., description="ID виртуальной карты для перезапуска выпуска")
    reason: str | None = Field(None, description="Причина перезапуска выпуска (опционально)")


class RerunVirtualCardReleaseResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус перезапуска выпуска карты")
    data: VirtualCardData = Field(..., description="Обновлённая информация о виртуальной карте")
    timestamp: int = Field(..., description="Время выполнения запроса (Unix Timestamp)")


# ======== Удаление виртуальной карты ========


class DeleteVirtualCardResponse(BaseModel):
    status: StatusModel = Field(..., description="Статус удаления виртуальной карты")
    data: bool = Field(..., description="Результат удаления карты (True — успешно)")
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
