"""Пример из docs/configuration.md: метрики операций из событий аудита."""

from __future__ import annotations

import logging

import httpx
import pytest

from apisdkopti24 import (
    APIClient,
    AsyncTransport,
    ConnectionSettings,
    StaticCredentialsProvider,
)
from tests.service_support import UNTHROTTLED

AUTH_RESPONSE = {
    "status": {"code": 200},
    "data": {
        "session_id": "session-id",
        "client_id": "client-id",
        "client_status": "Active",
        "org_name": "Test organization",
        "user_id": "user-id",
        "contracts": [
            {
                "id": "contract-id",
                "number": "C-1",
                "mpc": False,
                "cards_count": 0,
                "one_price": False,
            }
        ],
        "role_id": "Supervisor",
        "role_name": "Administrator",
        "access": {"web": True, "api": True, "mobile": True},
        "email": "user@example.test",
        "read_only": False,
    },
}


class OperationMetricsHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.observations: list[tuple[str, str, float]] = []

    def emit(self, record: logging.LogRecord) -> None:
        event = getattr(record, "event", None)
        if event in {"completed", "failed"}:
            self.observations.append((record.operation, event, record.elapsed_ms))


def fake_api(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/v1/authUser"):
        return httpx.Response(200, json=AUTH_RESPONSE)
    if request.url.path.endswith("/v2/cards"):
        cards = {"total_count": 0, "result": []}
        return httpx.Response(200, json={"status": {"code": 200}, "data": cards})
    return httpx.Response(404, json={"status": {"code": 404}})


@pytest.mark.asyncio
async def test_audit_events_feed_operation_metrics_without_files() -> None:
    handler = OperationMetricsHandler()
    sdk_logger = logging.getLogger("apisdkopti24")
    previous_level = sdk_logger.level
    sdk_logger.setLevel(logging.INFO)
    sdk_logger.addHandler(handler)
    settings = ConnectionSettings(base_url="https://api.example.ru/vip/")
    try:
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
                await client.cards.get_cards_v2()
    finally:
        sdk_logger.removeHandler(handler)
        sdk_logger.setLevel(previous_level)

    operations = [(operation, event) for operation, event, _ in handler.observations]
    assert ("get_cards_v2", "completed") in operations
    assert all(elapsed_ms >= 0 for _, _, elapsed_ms in handler.observations)
