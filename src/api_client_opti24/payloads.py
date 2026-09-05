from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, overload


@overload
def with_method_override(payload: Mapping[str, Any], method: str) -> dict[str, Any]: ...


@overload
def with_method_override(
    payload: Sequence[Mapping[str, Any]],
    method: str,
) -> list[dict[str, Any]]: ...


@overload
def with_method_override(payload: None, method: str) -> dict[str, Any]: ...


def with_method_override(
    payload: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
    method: str,
) -> dict[str, Any] | list[dict[str, Any]]:
    override = method.upper()
    if payload is None:
        return {"_method": override}
    if isinstance(payload, Mapping):
        return {**payload, "_method": override}
    return [{**item, "_method": override} for item in payload]
