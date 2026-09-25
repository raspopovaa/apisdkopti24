from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias

from .execution_budget import OperationBudget
from .session import RequestContext

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = object
QueryValue: TypeAlias = JsonScalar | list[JsonScalar] | tuple[JsonScalar, ...]
QueryParams: TypeAlias = Mapping[str, object]
FormData: TypeAlias = Mapping[str, object]
Headers: TypeAlias = Mapping[str, str]
PathParams: TypeAlias = Mapping[str, str | int]
BodyKind: TypeAlias = Literal["none", "form", "json"]
ContractLocation: TypeAlias = Literal["header", "query", "form", "json"]


@dataclass(frozen=True, slots=True)
class RequestContract:
    """Допустимое размещение параметров операции в HTTP-запросе."""

    has_path: bool = False
    has_query: bool = False
    body_kind: BodyKind = "none"
    contract_locations: frozenset[ContractLocation] = frozenset()
    request_models: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.contract_locations & {"form", "json"}) > 1:
            raise ValueError("contract_id нельзя задавать одновременно в форме и JSON")
        if "query" in self.contract_locations and not self.has_query:
            raise ValueError(
                "Для contract_id в строке запроса необходимо разрешить параметры строки запроса"
            )
        if "form" in self.contract_locations and self.body_kind != "form":
            raise ValueError("Для contract_id в форме необходимо тело запроса в формате формы")
        if "json" in self.contract_locations and self.body_kind != "json":
            raise ValueError("Для contract_id в JSON необходимо тело запроса в формате JSON")


# Сохраняем прежнее имя для существующих импортов.
RequestSpec = RequestContract


@dataclass(frozen=True, slots=True)
class RequestOptions:
    """Типизированные входные данные сервиса для исполнителя запросов."""

    api_version: str | None = None
    route_name: str = "default"
    path_params: PathParams = field(default_factory=dict)
    contract_id: str | None = None
    query: QueryParams = field(default_factory=dict)
    form: FormData | None = None
    json_body: JsonValue = None
    headers: Headers = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.form is not None and self.json_body is not None:
            raise ValueError("form и json_body нельзя задавать одновременно")


@dataclass(frozen=True, slots=True)
class PreparedRequest:
    """Полностью подготовленный запрос, независимый от реализации транспорта."""

    method: str
    endpoint: str
    api_version: str
    headers: Headers
    query: QueryParams
    form: FormData | None
    json_body: JsonValue
    timeout: float
    method_name: str
    retry_class: str
    idempotent: bool
    request_context: RequestContext
    operation_budget: OperationBudget
    limit_response_size: bool = True
    connect_timeout: float | None = None


@dataclass(frozen=True, slots=True)
class FileTarget:
    destination: Path
    chunk_size: int = 64 * 1024
    write_buffer_size: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size должен быть больше нуля")
        if self.write_buffer_size <= 0:
            raise ValueError("write_buffer_size должен быть больше нуля")


__all__ = [
    "FileTarget",
    "FormData",
    "Headers",
    "JsonScalar",
    "JsonValue",
    "PathParams",
    "PreparedRequest",
    "QueryParams",
    "QueryValue",
    "RequestOptions",
    "RequestContract",
    "RequestSpec",
]
