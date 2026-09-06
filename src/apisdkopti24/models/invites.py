from pydantic import AliasChoices, model_validator

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel


class _InviteContractRequest(StrictRequestModel):
    id: str = Field(
        ...,
        validation_alias=AliasChoices("id", "sid"),
        description="ID договора",
    )
    template_id: str | None = Field(None, description="ID шаблона виртуальной карты")


class InviteCreateRequest(StrictRequestModel):
    """Данные для создания приглашения."""

    role: str = Field(..., description="ID роли")
    mobile: str | None = Field(None, description="Номер телефона")
    email: str | None = Field(None, description="Email")
    cards: list[str] = Field(default_factory=list, description="ID прикрепляемых карт")
    contracts: list[_InviteContractRequest] = Field(
        default_factory=list,
        description="Договоры, прикрепляемые после регистрации",
    )

    @model_validator(mode="after")
    def require_recipient(self) -> "InviteCreateRequest":
        if self.mobile is None and self.email is None:
            raise ValueError("mobile or email is required")
        return self


class InviteCard(BaseModel):
    """Информация о карте, привязанной к приглашению"""

    sid: str = Field(..., description="ID карты (SID)")
    number: str = Field(..., description="Номер карты")
    product: str = Field(..., description="Тип продукта ('wallet' и т.п.)")
    comment: str | None = Field(None, description="Комментарий к карте (например, имя водителя)")
    status: str = Field(..., description="Технический статус карты")
    status_name: str = Field(..., description="Отображаемое название статуса")
    contract_id: str = Field(..., description="ID договора, к которому относится карта")
    contract_name: str = Field(..., description="Номер договора")


class InviteContract(BaseModel):
    """Информация о договоре, привязанном к приглашению"""

    sid: str = Field(..., description="ID договора")
    number: str = Field(..., description="Номер договора")
    status: str = Field(..., description="Технический статус договора")
    status_name: str = Field(..., description="Название статуса")
    template_id: str | None = Field(None, description="ID шаблона виртуальной карты, если есть")
    cards_count: int = Field(..., description="Количество карт по договору")


class InviteItem(BaseModel):
    """Элемент списка приглашений"""

    id: str = Field(..., description="ID приглашения")
    user_id: str | None = Field(None, description="ID пользователя, если уже создан")
    url: str = Field(..., description="Ссылка на регистрацию (уникальная, активна 3 дня)")
    status: str = Field(..., description="Технический статус приглашения (Active, Finished и т.п.)")
    status_name: str = Field(..., description="Отображаемое название статуса")
    role: str = Field(..., description="Роль пользователя ('Driver', 'Admin' и т.п.)")
    role_name: str = Field(..., description="Название роли")
    attempts: int = Field(..., description="Количество отправок приглашения")
    cards: list[InviteCard] = Field(..., description="Список карт, связанных с приглашением")
    initiator: str = Field(..., description="Пользователь, создавший приглашение")
    contracts: list[InviteContract] = Field(
        ..., description="Список договоров, привязанных к приглашению"
    )
    mobile: str | None = Field(None, description="Номер телефона приглашенного")
    email: str | None = Field(None, description="Email приглашенного")
    communication_type: str = Field(..., description="Тип отправки ('sms', 'email' и т.п.)")
    sended_at: int | None = Field(None, description="Время отправки (timestamp)")
    expired_at: int = Field(..., description="Время истечения срока действия ссылки (timestamp)")


class InviteList(BaseModel):
    """Ответ на запрос списка приглашений"""

    total_count: int = Field(..., description="Общее количество приглашений")
    result: list[InviteItem] | None = Field(None, description="Список приглашений")


class InviteListResponse(APIEnvelope[InviteList]):
    """Полный envelope списка приглашений."""


class InviteActionResult(BaseModel):
    """Результат действий с приглашениями (создание, продление, повторная отправка)"""

    id: str = Field(..., description="ID приглашения")
    url: str = Field(..., description="Ссылка на приглашение")
    attempts: int = Field(..., description="Количество попыток отправки")
    expired_at: int = Field(..., description="Дата истечения срока действия ссылки (timestamp)")


class InviteResponse(APIEnvelope[InviteActionResult]):
    """Полный envelope действия с приглашением."""


class InviteBoolResponse(APIEnvelope[bool]):
    """Полный envelope простого действия с приглашением."""
