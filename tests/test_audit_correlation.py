"""Аудит для приложений-оркестраторов (ИИ-агентов): correlation_id и признак тарификации."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import httpx
import pytest

from apisdkopti24 import (
    APIClient,
    AsyncTransport,
    ConnectionSettings,
    SDKConfigurationError,
    StaticCredentialsProvider,
    correlation_scope,
)
from apisdkopti24.audit_context import current_correlation_id
from apisdkopti24.error_reporting import OperationAudit
from apisdkopti24.logger import RequestAuditFormatter
from apisdkopti24.operations import OperationSpec
from apisdkopti24.registry import build_default_registry
from tests.service_support import UNTHROTTLED
from tests.test_audit_metrics import fake_api

UUID_CORRELATION_ID = "550e8400-e29b-41d4-a716-446655440000"


class _Clock:
    def monotonic(self) -> float:
        return 0.0


class _CapturingLogger:
    def __init__(self) -> None:
        self.records: list[dict[str, object]] = []

    def log(
        self,
        level: int,
        msg: object,
        *args: object,
        extra: dict[str, object] | None = None,
    ) -> None:
        del level, msg, args
        self.records.append(dict(extra or {}))


def _operation(name: str) -> OperationSpec[object]:
    return next(spec for spec in build_default_registry().list_all() if spec.name == name)


def _formatted(fields: dict[str, object]) -> dict[str, object]:
    record = logging.LogRecord("apisdkopti24.test", logging.INFO, __file__, 1, "audit", (), None)
    for key, value in fields.items():
        setattr(record, key, value)
    return json.loads(RequestAuditFormatter().format(record))


def test_correlation_scope_sets_and_restores_value() -> None:
    assert current_correlation_id() is None
    with correlation_scope("turn-1"):
        assert current_correlation_id() == "turn-1"
        with correlation_scope("turn-1:tool-2"):
            assert current_correlation_id() == "turn-1:tool-2"
        assert current_correlation_id() == "turn-1"
    assert current_correlation_id() is None


@pytest.mark.parametrize("value", ["", "x" * 129, "turn 1", "id=5\nforged", "водитель"])
def test_correlation_scope_rejects_unsafe_values(value: str) -> None:
    with pytest.raises(SDKConfigurationError), correlation_scope(value):
        pass
    assert current_correlation_id() is None


@pytest.mark.asyncio
async def test_correlation_id_reaches_tasks_created_inside_scope() -> None:
    async def read() -> str | None:
        await asyncio.sleep(0)
        return current_correlation_id()

    with correlation_scope("turn-7"):
        task = asyncio.create_task(read())
    outside = asyncio.create_task(read())

    assert await task == "turn-7"
    assert await outside is None


def test_audit_event_carries_billable_and_correlation_id() -> None:
    logger = _CapturingLogger()
    with correlation_scope(UUID_CORRELATION_ID):
        audit = OperationAudit(
            operation=_operation("get_card_detail"), logger=logger, clock=_Clock()
        )
    audit.start()

    payload = _formatted(logger.records[0])

    assert payload["billable"] is True
    # Цифры UUID не должны маскироваться как телефон.
    assert payload["correlation_id"] == UUID_CORRELATION_ID


def test_audit_event_without_scope_has_no_correlation_id() -> None:
    logger = _CapturingLogger()
    OperationAudit(operation=_operation("auth_user"), logger=logger, clock=_Clock()).start()

    payload = _formatted(logger.records[0])

    assert payload["billable"] is False
    assert "correlation_id" not in payload


@pytest.mark.asyncio
async def test_request_log_file_links_every_operation_to_caller_step(tmp_path: Path) -> None:
    audit_file = tmp_path / "audit.jsonl"
    settings = ConnectionSettings(
        base_url="https://api.example.ru/vip/", request_log_file=str(audit_file)
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(fake_api)) as http_client:
        transport = AsyncTransport(
            settings.base_url, http_client=http_client, rate_limit_policy=UNTHROTTLED
        )
        # Заглушка MockTransport не проверяет учётные данные.
        fake_value = "not-a-real-credential"
        credentials = StaticCredentialsProvider(
            api_key=fake_value, login=fake_value, password=fake_value
        )
        async with APIClient(
            settings=settings, transport=transport, credentials_provider=credentials
        ) as client:
            with correlation_scope("agent-turn-42"):
                await client.cards.get_cards_v2()

    events = [json.loads(line) for line in audit_file.read_text(encoding="utf-8").splitlines()]

    assert {event["operation"] for event in events} == {"auth_user", "get_cards_v2"}
    assert all(event["correlation_id"] == "agent-turn-42" for event in events)
    assert all(event["billable"] is False for event in events)
