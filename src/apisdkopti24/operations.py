from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

ResponseT = TypeVar("ResponseT")
ResponseKind = Literal["json", "bytes"]


@dataclass(frozen=True, slots=True)
class Operation(Generic[ResponseT]):
    name: str
    response_type: type[ResponseT] | None
    response_kind: ResponseKind = "json"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("operation name cannot be empty")
        if self.response_kind == "json" and self.response_type is None:
            raise ValueError("JSON operation requires a response type")


def operation(name: str, response_type: type[ResponseT]) -> Operation[ResponseT]:
    return Operation(name=name, response_type=response_type)


def binary_operation(name: str) -> Operation[bytes]:
    return Operation(name=name, response_type=None, response_kind="bytes")


__all__ = ["Operation", "ResponseKind", "binary_operation", "operation"]
