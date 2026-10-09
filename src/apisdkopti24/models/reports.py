from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel

# === Общие модели ===


class ReportParameterMenuValue(BaseModel):
    """Значения меню для параметра отчета."""

    labels: str | None = Field(default=None, description="Отображаемое имя пункта меню")
    values: str | None = Field(default=None, description="Значение пункта меню")


class ReportParameter(BaseModel):
    """Параметр отчета (например, дата, карта, договор)."""

    name: str = Field(..., description="Имя параметра, используемое в запросах")
    value: str | None = Field(default=None, description="Значение параметра")
    label: str | None = Field(
        ...,
        description="Отображаемое название параметра; реальный API может вернуть null",
    )
    default_value: str | None = Field(default=None, description="Значение по умолчанию")
    menu_values: list[ReportParameterMenuValue] | None = Field(
        default=None, description="Список возможных значений для выбора из меню"
    )
    type: str = Field(..., description="Тип параметра (например, date, Contract, Group)")


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
    result: list[ReportItem] | None = Field(default=None, description="Массив отчетов")


class ReportListResponse(APIEnvelope[ReportList]):
    """Полный envelope списка доступных отчётов."""


# === Заказ отчета ===


class ReportOrderParams(BaseModel):
    """Параметры заказа отчета."""

    start_date: str | None = Field(default=None, description="Дата начала периода")
    end_date: str | None = Field(default=None, description="Дата окончания периода")
    id_agreement: list[str] | None = Field(default=None, description="Список ID договоров")
    id_card: list[str] | None = Field(default=None, description="Список карт")
    card_group_code: list[str] | None = Field(default=None, description="Список групп карт")
    id_client: list[str] | None = Field(default=None, description="Список клиентов")
    additional: dict[str, object] | None = Field(
        default=None, description="Дополнительные параметры"
    )


class ReportOrderRequest(StrictRequestModel):
    """Тело запроса для заказа отчета (v2)."""

    id: str = Field(..., description="Идентификатор отчета")
    format: str = Field(..., description="Формат отчета (pdf, xlsx и т.д.)")
    emails: list[str] | None = Field(default=None, description="Email-адреса для отправки отчета")
    params: ReportOrderParams = Field(..., description="Параметры отчета")


class ReportOrderData(BaseModel):
    """Данные созданного задания отчёта (v2)."""

    job_id: list[str] | None = Field(
        default=None, description="Идентификаторы созданных заданий на генерацию отчета"
    )


class ReportOrderResponse(APIEnvelope[ReportOrderData]):
    """Полный envelope заказа отчёта (v2)."""


# === Список заказанных отчетов ===


class ReportJobItem(BaseModel):
    """Элемент списка заказанных отчетов."""

    date: str = Field(..., description="Дата создания заказа отчета")
    client_id: str = Field(..., description="ID клиента")
    user_id: str = Field(..., description="ID пользователя")
    contract_id: str = Field(..., description="ID договора")
    contract_name: str | None = Field(default=None, description="Название договора")
    job_id: str = Field(..., description="Идентификатор задания (Job ID)")
    report_name: str = Field(..., description="Название отчета")
    report_format: str = Field(..., description="Формат отчета (pdf, xlsx и т.д.)")
    available_after: int = Field(..., description="Количество секунд до доступности отчета")


class ReportJobList(BaseModel):
    """Ответ со списком заказанных отчетов (v1/v2)."""

    total_count: int = Field(..., description="Количество найденных отчетов")
    result: list[ReportJobItem] | None = Field(
        default=None, description="Список заказанных отчетов"
    )


class ReportJobListResponse(APIEnvelope[ReportJobList]):
    """Полный envelope списка заданий отчётов (v2)."""


# === v1 методы ===


class ReportV1OrderResponse(APIEnvelope[list[str]]):
    """Полный envelope заказа отчёта (v1)."""


class ReportV1JobItem(BaseModel):
    """Элемент списка ранее заказанных отчетов (v1)."""

    date: str = Field(..., description="Дата создания отчета")
    client_id: str = Field(..., description="ID клиента")
    user_id: str = Field(..., description="ID пользователя")
    contract_id: str = Field(..., description="ID договора")
    job_id: str = Field(..., description="Идентификатор задания (Job ID)")
    report_name: str = Field(..., description="Название отчета")
    report_format: str = Field(..., description="Формат отчета (pdf, xlsx, xml и т.д.)")


class ReportV1JobListResponse(APIEnvelope[list[ReportV1JobItem] | None]):
    """Полный envelope списка заданий отчётов (v1)."""

    data: list[ReportV1JobItem] | None = Field(default=None, description="Массив заданий отчётов")
