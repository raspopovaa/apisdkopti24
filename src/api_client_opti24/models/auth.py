from datetime import datetime

from ..modeling import APIEnvelope, BaseModel, Field

# -------------------------
# Базовые классы и служебные структуры
# -------------------------


class StatusResponse(BaseModel):
    code: int = Field(
        ...,
        description="Код состояния ответа (например, 200 — OK, 400 — ошибка запроса)",
    )


class AccessRights(BaseModel):
    web: bool = Field(..., description="Доступ к ЛК")
    api: bool = Field(..., description="Доступ к API")
    mobile: bool = Field(..., description="Доступ к МП")


# -------------------------
# Авторизация пользователя (authUser)
# -------------------------


class ContractInfo(BaseModel):
    id: str = Field(..., description="ID договора")
    number: str = Field(..., description="Номер договора")
    mpc: bool = Field(..., description="Возможность выпуска МПК")
    template_id: str | None = Field(None, description="ID шаблона ВК")
    cards_count: int = Field(default=0, description="Количество карт на договоре")
    one_price: bool = Field(default=False, description="Признак единой цены")


class AuthUserData(BaseModel):
    client_id: str = Field(..., description="ID клиента в системе")
    client_status: str = Field(..., description="Статус клиента (Active, Blocked, и т.п.)")
    org_name: str = Field(..., description="Наименование организации")
    session_id: str = Field(..., description="JWT токен активной сессии")
    user_id: str = Field(..., description="ID пользователя")
    contracts: list[ContractInfo] = Field(
        default_factory=list, description="Список доступных договоров"
    )
    role_id: str = Field(..., description="Код роли (например, Supervisor)")
    role_name: str = Field(..., description="Название роли (например, Администратор)")
    read_only: bool = Field(default=False, description="Флаг режима только чтение")
    user_name: str | None = Field(None, description="Имя пользователя")
    user_patronymic: str | None = Field(None, description="Отчество пользователя")
    user_surname: str | None = Field(None, description="Фамилия пользователя")
    last_contract: str | None = Field(None, description="SID последнего договора")
    access: AccessRights = Field(..., description="Права доступа (ЛК/МП/API)")
    email: str = Field(..., description="Электронная почта")
    phone: str | None = Field(None, description="Телефон")


class AuthUserResponse(APIEnvelope[AuthUserData]):
    pass


# -------------------------
# Деавторизация пользователя (logoff)
# -------------------------


class LogoffResponse(APIEnvelope[bool]):
    pass


# -------------------------
# Ошибки авторизации
# -------------------------


class AuthError(BaseModel):
    code: str = Field(..., description="Код ошибки (например, INVALID_CREDENTIALS)")
    message: str = Field(..., description="Текст ошибки")


class AuthErrorResponse(BaseModel):
    error: AuthError = Field(..., description="Описание ошибки авторизации")


# -------------------------
# Статистика использования API (метод info)
# -------------------------


class ClientInfo(BaseModel):
    Client: str = Field(..., description="ID клиента")
    ClientType: str = Field(..., description="Тип клиента (например, D)")
    Contract: str = Field(..., description="ID контракта")
    ContractName: str = Field(..., description="Название контракта")
    PricePlan: str | None = Field(None, description="Тарифный план")
    Cost: float | None = Field(None, description="Стоимость запросов")
    Queries: int | None = Field(None, description="Количество запросов")
    Additional: int | None = Field(None, description="Дополнительное значение")


class MethodsCount(BaseModel):
    all: int = Field(0, description="Общее количество методов")
    cards: int | None = Field(0, description="Методы, связанные с картами")
    cardgroups: int | None = Field(0, description="Методы, связанные с группами карт")
    card: int | None = Field(0, description="Методы, связанные с одной картой")


class MethodsInfo(BaseModel):
    actions_bill: dict[str, str] = Field(
        ..., description="Платные методы API (влияют на статистику)"
    )
    actions_not_bill: dict[str, str] = Field(
        ..., description="Бесплатные методы API (не влияют на статистику)"
    )


class InfoData(BaseModel):
    from_: datetime = Field(..., alias="from", description="Начало периода статистики")
    to: datetime = Field(..., description="Конец периода статистики")
    client_info: ClientInfo = Field(..., description="Информация о клиенте")
    methods: MethodsCount = Field(..., description="Количество вызовов по категориям")
    methods_info: MethodsInfo = Field(..., description="Описание доступных методов API")


class GetInfoResponse(APIEnvelope[InfoData]):
    pass
