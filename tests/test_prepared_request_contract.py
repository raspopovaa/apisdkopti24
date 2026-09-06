from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import pytest

from apisdkopti24.config import TimeoutPolicy
from apisdkopti24.credentials import StaticAPIKeyProvider
from apisdkopti24.executor import OperationExecutor
from apisdkopti24.registry import build_default_registry
from apisdkopti24.requests import RequestOptions
from apisdkopti24.session import SessionManager

MATRIX_PATH = Path(__file__).parents[1] / "specifications" / "request-matrix-v1.1.60.json"
MATRIX = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def test_request_matrix_covers_every_operation_once() -> None:
    operations = [str(row["operation"]) for row in MATRIX]
    assert len(operations) == 89
    assert len(operations) == len(set(operations))
    assert set(operations) == {spec.name for spec in build_default_registry().list_all()}


def test_request_contract_exposes_dto_metadata() -> None:
    registry = build_default_registry()
    assert registry.get("get_cards_v2").request.request_models == ("CardsV2Query",)
    assert registry.get("set_limit").request.request_models == (
        "SetLimitRequest",
        "LimitRequestItem",
    )
    assert registry.get("logoff").request.request_models == ()


class FrozenClock:
    def now(self) -> datetime:
        return datetime(2026, 9, 6, 12, 0, 0)

    def monotonic(self) -> float:
        return 0.0

    async def sleep(self, seconds: float) -> None:
        del seconds


class UnusedTransport:
    async def request(self, request: object) -> dict[str, object]:
        raise AssertionError(f"Unexpected transport request: {request}")

    async def request_stream(self, request: object) -> bytes:
        raise AssertionError(f"Unexpected transport request: {request}")

    async def request_stream_to_file(self, request: object, target: object) -> Path:
        raise AssertionError(f"Unexpected transport request: {request} {target}")

    async def aclose(self) -> None:
        return None


@pytest.mark.parametrize("expected", MATRIX, ids=lambda item: item["operation"])
def test_operation_builds_contractual_prepared_request(expected: dict[str, object]) -> None:
    registry = build_default_registry()
    operation = registry.get(str(expected["operation"]))
    session = SessionManager()
    session.mark_authenticated("session-1", "contract-1")
    executor = OperationExecutor(
        api_key_provider=StaticAPIKeyProvider("api-key"),
        transport=UnusedTransport(),
        session_context=session,
        timeouts=TimeoutPolicy(),
        logger=logging.getLogger("prepared-request-contract"),
        clock=FrozenClock(),
    )
    prepared = executor.prepare(
        operation,
        RequestOptions(
            path_params=expected["path_params"],
            contract_id=expected["contract_header"],
            query=expected["query"],
            form=expected["form"],
            json_body=expected["json_body"],
        ),
        executor.create_budget(operation),
    )

    assert prepared.method == expected["method"]
    assert prepared.api_version == expected["api_version"]
    assert prepared.endpoint == expected["endpoint"]
    assert prepared.query == expected["query"]
    assert prepared.form == expected["form"]
    assert prepared.json_body == expected["json_body"]
    assert prepared.headers.get("contract_id") == expected["contract_header"]
    assert prepared.headers.get("Content-Type") == expected["content_type"]
