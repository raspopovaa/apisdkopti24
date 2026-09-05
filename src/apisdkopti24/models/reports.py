from typing import Any

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel

# === Общие модели ===


class ReportParameterMenuValue(BaseModel):
    """Значения меню для параметра отчета."""

    labels: str | None = Field(None, description="Отображаемое имя пункта меню")
    values: str | None = Field(None, description="Значение пункта меню")


class ReportParameter(BaseModel):
    """Параметр отчета (например, дата, карта, договор)."""

    name: str = Field(..., description="Имя параметра, используемое в запросах")
    value: Any | None = Field(None, description="Значение параметра")
    label: str | None = Field(None, description="Отображаемое название параметра")
    default_value: str | None = Field(None, description="Значение по умолчанию")
    menu_values: list[ReportParameterMenuValue] | None = Field(
        None, description="Список возможных значений для выбора из меню"
    )
    type: str | None = Field(None, description="Тип параметра (например, date, Contract, Group)")


class ReportItem(BaseModel):
    """Описание доступного отчета (v2)."""

    id: str = Field(..., description="Идентификатор отчета")
    name: str = Field(..., description="Название отчета")
    formats: list[str] = Field(
        ..., description="Список поддерживаемых форматов (pdf, xlsx, csv и т.д.)"
    )
    parameters: list[ReportParameter] = Field(..., description="Список параметров отчета")


class ReportList(BaseModel):
    """Ответ метода /v2/reports — список доступных отчетов."""

    total_count: int = Field(..., description="Количество доступных отчетов")
    result: list[ReportItem] = Field(..., description="Массив отчетов")


class ReportListResponse(APIEnvelope[ReportList]):
    """Полный envelope списка доступных отчётов."""


# === Заказ отчета ===


class ReportOrderParams(BaseModel):
    """Параметры заказа отчета."""

    start_date: str | None = Field(None, description="Дата начала периода")
    end_date: str | None = Field(None, description="Дата окончания периода")
    id_agreement: str | None = Field(None, description="Список ID договоров")
    id_card: list[str] | None = Field(None, description="Список карт")
    card_group_code: list[str] | None = Field(None, description="Список групп карт")
    id_client: list[str] | None = Field(None, description="Список клиентов")
    additional: dict[str, Any] | None = Field(None, description="Дополнительные параметры")


class ReportOrderRequest(StrictRequestModel):
    """Тело запроса для заказа отчета (v2)."""

    id: str = Field(..., description="Идентификатор отчета")
    format: str = Field(..., description="Формат отчета (pdf, xlsx и т.д.)")
    emails: str | None = Field(None, description="Email-адреса для отправки отчета")
    params: ReportOrderParams = Field(..., description="Параметры отчета")


class ReportOrderData(BaseModel):
    """Данные созданного задания отчёта (v2)."""

    job_id: list[str] = Field(
        ..., description="Идентификаторы созданных заданий на генерацию отчета"
    )


class ReportOrderResponse(APIEnvelope[ReportOrderData]):
    """Полный envelope заказа отчёта (v2)."""


# === Список заказанных отчетов ===


class ReportJobItem(BaseModel):
    """Элемент списка заказанных отчетов."""

    date: str = Field(..., description="Дата создания заказа отчета")
    client_id: str | None = Field(None, description="ID клиента")
    user_id: str | None = Field(None, description="ID пользователя")
    contract_id: str | None = Field(None, description="ID договора")
    contract_name: str | None = Field(None, description="Название договора")
    job_id: str = Field(..., description="Идентификатор задания (Job ID)")
    report_name: str = Field(..., description="Название отчета")
    report_format: str = Field(..., description="Формат отчета (pdf, xlsx и т.д.)")
    available_after: int | None = Field(None, description="Количество секунд до доступности отчета")


class ReportJobList(BaseModel):
    """Ответ со списком заказанных отчетов (v1/v2)."""

    total_count: int | None = Field(None, description="Количество найденных отчетов")
    result: list[ReportJobItem] = Field(..., description="Список заказанных отчетов")


class ReportJobListResponse(APIEnvelope[ReportJobList]):
    """Полный envelope списка заданий отчётов (v2)."""


# === Генерация отчета ===


class ReportFileResponse(BaseModel):
    """Ответ при генерации файла отчета."""

    content: bytes | None = Field(
        None, description="Бинарное содержимое файла (application/octet-stream)"
    )
    format: str | None = Field(None, description="Формат файла (pdf, xlsx, csv и т.д.)")
    filename: str | None = Field(None, description="Имя файла отчета")
    size: int | None = Field(None, description="Размер файла в байтах")


# === v1 методы ===


class ReportV1OrderResponse(APIEnvelope[list[str]]):
    """Полный envelope заказа отчёта (v1)."""


class ReportV1JobItem(BaseModel):
    """Элемент списка ранее заказанных отчетов (v1)."""

    date: str = Field(..., description="Дата создания отчета")
    client_id: str | None = Field(None, description="ID клиента")
    user_id: str | None = Field(None, description="ID пользователя")
    contract_id: str | None = Field(None, description="ID договора")
    job_id: str = Field(..., description="Идентификатор задания (Job ID)")
    report_name: str = Field(..., description="Название отчета")
    report_format: str = Field(..., description="Формат отчета (pdf, xlsx, xml и т.д.)")


class ReportV1JobListResponse(APIEnvelope[list[ReportV1JobItem]]):
    """Полный envelope списка заданий отчётов (v1)."""
