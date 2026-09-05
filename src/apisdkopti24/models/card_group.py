from typing import Literal

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel


class CardGroupAssignmentRequest(StrictRequestModel):
    """Карта и действие при изменении состава группы."""

    id: str = Field(..., description="ID карты")
    type: Literal["Attach", "Detach"] = Field(..., description="Действие с картой")


class CardGroupItem(BaseModel):
    """Информация о группе карт."""

    id: str = Field(..., description="Идентификатор группы карт")
    name: str = Field(..., description="Название группы карт")
    cards_count: int = Field(..., description="Количество карт в группе")
    status: str = Field(..., description="Статус группы (например, Synchronize)")
    contract_id: str = Field(..., description="Идентификатор договора")


class CardGroupListData(BaseModel):
    """Контейнер данных со списком групп карт."""

    total_count: int = Field(..., description="Общее количество групп")
    result: list[CardGroupItem] = Field(..., description="Список групп карт")


class CardGroupListResponse(APIEnvelope[CardGroupListData]):
    """Ответ метода получения списка групп карт."""


class SetCardsToGroupResponse(APIEnvelope[bool]):
    """Ответ метода добавления карт в группу."""


class RemoveCardGroupResponse(APIEnvelope[bool]):
    """Ответ метода удаления группы карт."""


class SetCardGroupData(BaseModel):
    """Информация о созданной или изменённой группе."""

    id: str = Field(..., description="Идентификатор созданной или изменённой группы")


class SetCardGroupResponse(APIEnvelope[SetCardGroupData]):
    """Ответ метода установки/изменения группы карт."""
