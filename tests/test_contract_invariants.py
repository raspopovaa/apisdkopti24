"""Отказы проверок контракта: ошибки описания операций и запросов видны сразу."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal  # noqa: UP035

import pytest

from apisdkopti24.config import TimeoutPolicy
from apisdkopti24.credentials import StaticAPIKeyProvider
from apisdkopti24.endpoints import RouteVariant
from apisdkopti24.errors import RequestPreparationError
from apisdkopti24.executor import OperationExecutor
from apisdkopti24.modeling import ResponseModel, validator
from apisdkopti24.operations import OperationSpec
from apisdkopti24.requests import FileTarget, RequestContract, RequestOptions
from apisdkopti24.session import SessionManager
from tests.service_support import FrozenClock


def make_operation(**overrides: Any) -> OperationSpec[object]:
    fields: dict[str, Any] = {
        "name": "custom",
        "response_type": dict,
        "domain": "custom",
        "http_method": "GET",
        "endpoint": "custom",
        "supported_versions": ("v1",),
        "default_version": "v1",
        "demo_available": False,
        "idempotent": True,
    }
    fields.update(overrides)
    return OperationSpec(**fields)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"name": ""}, "Имя операции"),
        ({"response_type": None}, "тип ответа"),
        ({"external_code": "X1"}, "billable"),
        (
            {
                "route_variants": (
                    RouteVariant("GET", "a", "v1", False, name="extra"),
                    RouteVariant("GET", "b", "v1", False, name="extra"),
                )
            },
            "повторяющиеся",
        ),
        ({"default_version": "v2"}, "версию по умолчанию"),
        ({"endpoint": "custom/{card_id}"}, "параметров пути"),
    ],
)
def test_operation_spec_rejects_inconsistent_contract(
    overrides: dict[str, Any], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        make_operation(**overrides)


@pytest.mark.parametrize(
    ("contract", "message"),
    [
        (
            {"body_kind": "json", "contract_locations": frozenset({"form", "json"})},
            "одновременно",
        ),
        ({"contract_locations": frozenset({"query"})}, "строке запроса"),
        ({"contract_locations": frozenset({"form"})}, "форме"),
        ({"contract_locations": frozenset({"json"})}, "JSON"),
    ],
)
def test_request_contract_rejects_impossible_contract_placement(
    contract: dict[str, Any], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        RequestContract(**contract)


def test_request_options_reject_form_and_json_together() -> None:
    with pytest.raises(ValueError, match="одновременно"):
        RequestOptions(form={"a": "1"}, json_body={"a": 1})


@pytest.mark.parametrize(
    ("chunk_size", "write_buffer_size", "message"),
    [(0, 1, "chunk_size"), (1, 0, "write_buffer_size")],
)
def test_file_target_rejects_non_positive_sizes(
    tmp_path: Any, chunk_size: int, write_buffer_size: int, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        FileTarget(tmp_path / "report.bin", chunk_size, write_buffer_size)


class UnusedTransport:
    async def request(self, request: object) -> dict[str, object]:
        raise AssertionError(f"Неожиданный запрос транспорта: {request}")

    async def request_stream(self, request: object) -> bytes:
        raise AssertionError(f"Неожиданный запрос транспорта: {request}")

    async def request_stream_to_file(self, request: object, target: object) -> Path:
        raise AssertionError(f"Неожиданный запрос транспорта: {request} {target}")

    async def aclose(self) -> None:
        return None


class EmptyAPIKeyProvider:
    def get_api_key(self) -> str:
        return ""


def build_operation_executor(
    api_key_provider: Any = None,
) -> OperationExecutor:
    session = SessionManager()
    session.mark_authenticated("session-1", "contract-1")
    return OperationExecutor(
        api_key_provider=api_key_provider or StaticAPIKeyProvider("api-key"),
        transport=UnusedTransport(),
        session_context=session,
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("contract-invariants"),
        clock=FrozenClock(datetime(2026, 9, 6, 12, 0, 0)),
    )


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (RequestOptions(query={"page": 1}), "строки запроса"),
        (RequestOptions(form={"a": "1"}), "формы"),
        (RequestOptions(json_body={"a": 1}), "тело JSON"),
        (RequestOptions(contract_id="contract-2"), "contract_id"),
    ],
)
def test_prepare_rejects_parameters_the_operation_does_not_accept(
    options: RequestOptions, message: str
) -> None:
    executor = build_operation_executor()
    operation = make_operation()

    with pytest.raises(RequestPreparationError, match=message):
        executor.prepare(operation, options, executor.create_budget(operation))


def test_build_headers_rejects_empty_api_key() -> None:
    with pytest.raises(RequestPreparationError, match="пустое значение"):
        build_operation_executor(EmptyAPIKeyProvider()).build_headers(
            make_operation(), RequestOptions()
        )


class Described(ResponseModel):
    plain: int
    anything: Any = None
    nothing: None = None
    optional: str | None = None
    items: list[int] = []
    bare_items: List = []  # noqa: UP006  # type: ignore[type-arg]
    mapping: dict[str, int] = {}
    bare_mapping: Dict = {}  # noqa: UP006  # type: ignore[type-arg]
    pair: tuple[int, str] = (0, "")
    many: tuple[int, ...] = ()
    union: list[int] | None = None
    choice: Literal["a"] = "a"


def test_describe_formats_every_annotation_kind() -> None:
    types = {name: info["type"] for name, info in Described.describe().items()}

    assert types == {
        "plain": "int",
        "anything": "Any",
        "nothing": "None",
        "optional": "str | None",
        "items": "list[int]",
        "bare_items": "list[Any]",
        "mapping": "dict[str, int]",
        "bare_mapping": "dict[Any, Any]",
        "pair": "tuple[int, str]",
        "many": "tuple[int, ...]",
        "union": "list[int] | None",
        "choice": "Literal['a']",
    }


@pytest.mark.parametrize("pre", [True, False])
def test_validator_registers_field_validator_in_requested_mode(pre: bool) -> None:
    calls: list[object] = []

    class Normalized(ResponseModel):
        value: int

        @validator("value", pre=pre)
        @classmethod
        def record(cls, value: object) -> object:
            calls.append(value)
            return value

    Normalized(value="5" if pre else 5)  # type: ignore[arg-type]

    assert calls == (["5"] if pre else [5])
