# apisdkopti24/models/users.py
from typing import Annotated

from pydantic import StringConstraints

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel
from .request_parts import Identifier, PositivePage


class UserFilter(StrictRequestModel):
    role: str | None = None
    active: bool | None = None


class UsersQuery(StrictRequestModel):
    sort: str | None = Field(None, min_length=1)
    filter: UserFilter | None = None
    q: str | None = None
    page: PositivePage | None = None
    on_page: PositivePage | None = None
    contract_id: Identifier | None = None


Mobile = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class UserCreateRequest(StrictRequestModel):
    uuid: Identifier
    mobile: Mobile


class UserCardRequest(StrictRequestModel):
    card_id: Identifier


class UserContractsRequest(StrictRequestModel):
    contracts: list[Identifier] = Field(..., min_length=1)


# ---------- Общие подмодели ----------


class UserAttachContractRequest(StrictRequestModel):
    """Договор, прикрепляемый к пользователю."""

    sid: str = Field(..., description="ID договора")
    template_id: str | None = Field(None, description="ID шаблона виртуальной карты")
    use_mpc: bool | None = Field(None, description="Разрешён ли выпуск МПК")


class UserStatus(BaseModel):
    id: str = Field(..., description="ID статуса договора, например Active")
    name: str = Field(..., description="Название статуса договора, например Активен")


class UserContractItem(BaseModel):
    sid: str = Field(..., description="ID договора")
    number: str = Field(..., description="Номер договора")
    available: bool | str = Field(..., description="Доступен ли договор пользователю")
    template_id: str | None = Field(None, description="ID шаблона договора, если есть")
    cards_count: int = Field(..., description="Количество карт по договору")
    status: UserStatus = Field(..., description="Статус договора")


class UserCardItem(BaseModel):
    sid: str = Field(..., description="SID карты")
    number: str = Field(..., description="Номер карты")
    mpc: bool = Field(..., description="Признак мультикарты")
    product: str = Field(..., description="Тип продукта карты (wallet, limit и т.д.)")
    comment: str | None = Field(None, description="Комментарий к карте")
    status: str = Field(..., description="Статус карты (Active, Blocked и т.п.)")
    contract_id: str = Field(..., description="ID договора, к которому привязана карта")
    contract_name: str = Field(..., description="Название договора")
    available: bool | str = Field(..., description="Доступна ли карта пользователю")


class UserRole(BaseModel):
    id: str = Field(..., description="ID роли пользователя (Driver, Manager и т.д.)")
    name: str = Field(..., description="Название роли пользователя")


class UserAccess(BaseModel):
    web: bool = Field(..., description="Доступ через веб-интерфейс")
    api: bool = Field(..., description="Доступ через API")
    mobile: bool = Field(..., description="Доступ через мобильное приложение")


# ---------- Основная модель пользователя ----------


class UserItem(BaseModel):
    id: str = Field(..., description="ID пользователя в системе")
    login: str = Field(..., description="Логин пользователя (обычно номер телефона)")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    middle_name: str = Field(..., description="Отчество пользователя")
    date: str = Field(..., description="Дата рождения")
    position: str = Field(..., description="Должность или UUID должности")
    role: UserRole = Field(..., description="Роль пользователя")
    active: bool | None = Field(None, description="Активен ли пользователь")
    access: UserAccess = Field(..., description="Информация о доступах пользователя")
    mobile_phone: str | None = Field(None, description="Мобильный телефон пользователя")
    email: str | None = Field(None, description="Email пользователя")

    contracts: list[UserContractItem] = Field(
        default_factory=list, description="Список договоров пользователя"
    )
    cards: list[UserCardItem] = Field(default_factory=list, description="Список карт пользователя")


# ---------- Ответы API ----------


class UserList(BaseModel):
    total_count: int = Field(..., description="Общее количество пользователей")
    result: list[UserItem] | None = Field(None, description="Список пользователей")


class UserListResponse(APIEnvelope[UserList | None]):

    @property
    def total_count(self) -> int:
        return self.data.total_count if self.data else 0

    @property
    def result(self) -> list[UserItem]:
        return (self.data.result or []) if self.data else []


class UserCreateResponse(APIEnvelope[str]):
    pass


class UserBoolResponse(APIEnvelope[bool]):
    pass


UsersListResponse = UserListResponse
