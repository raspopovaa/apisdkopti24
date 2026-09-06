from typing import Literal

from pydantic import AliasChoices

from ..modeling import APIEnvelope, BaseModel, Field, StrictRequestModel


class RegionLimitRequestItem(StrictRequestModel):
    """Строгий элемент запроса установки регионального лимита."""

    id: str | None = Field(
        None,
        validation_alias=AliasChoices("id", "regionlimit_id"),
        serialization_alias="id",
        min_length=1,
        description="ID регионального лимита при изменении существующей записи",
    )
    contract_id: str | None = Field(None, min_length=1, description="ID договора")
    card_id: str | None = Field(None, min_length=1, description="ID карты")
    group_id: str | None = Field(None, min_length=1, description="ID группы карт")
    country: str = Field(..., min_length=1, description="Код страны обслуживания")
    region: str | None = Field(None, min_length=1, description="Код региона обслуживания")
    service_center: str | None = Field(None, min_length=1, description="ID точки обслуживания")
    partner: str | None = Field(None, min_length=1, description="ID партнёра")
    limit_type: Literal[1, 2] = Field(
        ..., description="Тип лимита: 1 — разрешающий, 2 — запрещающий"
    )


class RegionLimit(BaseModel):
    """Региональный лимит по договору, карте или группе карт."""

    id: str | None = Field(..., description="ID регионального лимита")
    contract_id: str = Field(..., description="ID договора, к которому относится лимит")
    card_id: str | None = Field(None, description="ID карты, если лимит задан для карты")
    group_id: str | None = Field(None, description="ID группы карт, если лимит задан для группы")
    country: str = Field(..., description="Код страны обслуживания, пример - RUS")
    region: str | None = Field(None, description="Код регион обслуживания")
    service_center: str | None = Field(None, description="ID АЗС")
    date: str = Field(..., description="Дата последнего изменения")
    limit_type: int = Field(
        ..., description="Тип лимита"
    )  # 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель


class RegionLimitList(BaseModel):
    """Коллекция региональных лимитов."""

    total_count: int = Field(..., description="Общее количество лимитов")
    result: list[RegionLimit] | None = Field(None, description="Данные с лимитами")


class RegionLimitResponse(APIEnvelope[RegionLimitList]):
    """Коллекция региональных лимитов."""


class RegionLimitSetResponse(APIEnvelope[list[str] | None]):
    """Полный envelope установки или изменения региональных лимитов."""

    data: list[str] | None = Field(None, description="ID сохранённых региональных лимитов")


class RemoveRegionLimit(APIEnvelope[bool]):
    """Удаление регионального лимита."""
