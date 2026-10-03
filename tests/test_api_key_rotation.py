import asyncio
import logging

import httpx
import pytest

from apisdkopti24 import (
    APIClient,
    AsyncTransport,
    ConnectionSettings,
    RefreshingAPIKeyProvider,
    SDKConfigurationError,
    StaticLoginPasswordProvider,
)
from tests.test_full_chain import _auth_success


class _ManualTicker:
    """Заменяет паузу между обновлениями: тест сам решает, когда она закончилась."""

    def __init__(self) -> None:
        self._ticks: asyncio.Queue[None] = asyncio.Queue()

    async def sleep(self, seconds: float) -> None:
        del seconds
        await self._ticks.get()

    async def tick(self) -> None:
        await self._ticks.put(None)
        for _ in range(10):
            await asyncio.sleep(0)


def _key_source(*outcomes: str | Exception):
    remaining = list(outcomes)

    async def fetch_api_key() -> str:
        outcome = remaining.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    return fetch_api_key


@pytest.mark.asyncio
async def test_client_sends_the_rotated_key_without_being_recreated() -> None:
    sent_keys: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent_keys.append(request.headers["api_key"])
        if request.url.path.endswith("/v1/authUser"):
            return httpx.Response(200, json=_auth_success("session-1"), request=request)
        body = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
        return httpx.Response(200, json=body, request=request)

    api_keys = RefreshingAPIKeyProvider(_key_source("key-1"), ttl_seconds=300)
    await api_keys.start()
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    settings = ConnectionSettings(base_url="https://api.example.test/vip/")
    async with APIClient(
        settings=settings,
        transport=AsyncTransport(settings.base_url, http_client=http_client),
        api_key_provider=api_keys,
        credentials_provider=StaticLoginPasswordProvider(login="login", password="password"),
    ) as client:
        await client.cards.get_cards_v2()
        api_keys.set_api_key("key-2")
        await client.cards.get_cards_v2()

    assert sent_keys == ["key-1", "key-1", "key-2"]
    await api_keys.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_background_refresh_replaces_the_key_after_each_interval() -> None:
    ticker = _ManualTicker()
    api_keys = RefreshingAPIKeyProvider(
        _key_source("key-1", "key-2"),
        ttl_seconds=300,
        sleep=ticker.sleep,
    )

    async with api_keys:
        assert api_keys.get_api_key() == "key-1"
        await ticker.tick()
        assert api_keys.get_api_key() == "key-2"
        assert api_keys.last_refresh_failed is False


@pytest.mark.asyncio
async def test_failed_refresh_keeps_the_previous_key_and_recovers(caplog) -> None:
    ticker = _ManualTicker()
    api_keys = RefreshingAPIKeyProvider(
        _key_source("key-1", OSError("vault is down: token=secret-value"), "", "key-3"),
        ttl_seconds=300,
        sleep=ticker.sleep,
    )

    with caplog.at_level(logging.WARNING, logger="apisdkopti24"):
        async with api_keys:
            await ticker.tick()  # источник недоступен
            assert api_keys.get_api_key() == "key-1"
            assert api_keys.last_refresh_failed is True

            await ticker.tick()  # источник вернул пустой ключ
            assert api_keys.get_api_key() == "key-1"
            assert api_keys.last_refresh_failed is True

            await ticker.tick()
            assert api_keys.get_api_key() == "key-3"
            assert api_keys.last_refresh_failed is False

    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "OSError" in messages
    assert "secret-value" not in messages


@pytest.mark.asyncio
async def test_key_must_be_obtained_before_first_request() -> None:
    api_keys = RefreshingAPIKeyProvider(_key_source(""), ttl_seconds=300)

    with pytest.raises(SDKConfigurationError, match="ещё не получен"):
        api_keys.get_api_key()
    with pytest.raises(SDKConfigurationError, match="api_key"):
        await api_keys.start()
    with pytest.raises(SDKConfigurationError, match="ещё не получен"):
        api_keys.get_api_key()


@pytest.mark.asyncio
async def test_aclose_stops_refreshing_and_keeps_the_last_key() -> None:
    ticker = _ManualTicker()
    calls = 0

    async def fetch_api_key() -> str:
        nonlocal calls
        calls += 1
        return f"key-{calls}"

    api_keys = RefreshingAPIKeyProvider(fetch_api_key, ttl_seconds=300, sleep=ticker.sleep)
    await api_keys.start()
    await api_keys.start()  # повторный запуск не создаёт вторую задачу
    await api_keys.aclose()
    await ticker.tick()

    assert calls == 1
    assert api_keys.get_api_key() == "key-1"
    await api_keys.aclose()


@pytest.mark.parametrize("ttl_seconds", [0, -1, float("inf"), float("nan")])
def test_ttl_must_be_positive_and_finite(ttl_seconds: float) -> None:
    with pytest.raises(SDKConfigurationError, match="ttl_seconds"):
        RefreshingAPIKeyProvider(_key_source("key"), ttl_seconds=ttl_seconds)


def test_repr_does_not_reveal_the_key() -> None:
    api_keys = RefreshingAPIKeyProvider(_key_source(), ttl_seconds=300)
    api_keys.set_api_key("very-secret-key")

    assert "very-secret-key" not in repr(api_keys)
    assert "api_key=***" in repr(api_keys)


@pytest.mark.asyncio
async def test_successful_manual_refresh_clears_the_failure_flag() -> None:
    ticker = _ManualTicker()
    api_keys = RefreshingAPIKeyProvider(
        _key_source("key-1", OSError("vault is down"), "key-2"),
        ttl_seconds=300,
        sleep=ticker.sleep,
    )

    async with api_keys:
        await ticker.tick()  # фоновое обновление не удалось
        assert api_keys.last_refresh_failed is True

        await api_keys.refresh()
        assert api_keys.get_api_key() == "key-2"
        assert api_keys.last_refresh_failed is False

        api_keys.set_api_key("key-manual")
        assert api_keys.last_refresh_failed is False
