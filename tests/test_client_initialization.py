import logging

import pytest

import api_client_opti24.client as client_module
from api_client_opti24 import APIClient
from api_client_opti24.config import APISettings


def test_client_closes_managed_logger_when_transport_initialization_fails(
    monkeypatch,
) -> None:
    class FakeManagedLogger:
        def __init__(self) -> None:
            self.logger = logging.getLogger("failed-client-init")
            self.closed = False

        def close(self) -> None:
            self.closed = True

    managed_logger = FakeManagedLogger()

    def create_logger(**kwargs):
        del kwargs
        return managed_logger

    class FailingTransport:
        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs
            raise RuntimeError("transport initialization failed")

    monkeypatch.setattr(client_module, "create_client_logger", create_logger)
    monkeypatch.setattr(client_module, "AsyncTransport", FailingTransport)

    settings = APISettings(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
    )

    with pytest.raises(RuntimeError, match="transport initialization failed"):
        APIClient(settings=settings)

    assert managed_logger.closed is True


@pytest.mark.asyncio
async def test_client_does_not_close_external_transport_and_closes_logger_once(
    monkeypatch,
) -> None:
    class CountingTransport:
        def __init__(self) -> None:
            self.close_calls = 0

        async def aclose(self) -> None:
            self.close_calls += 1

    class FakeManagedLogger:
        def __init__(self) -> None:
            self.logger = logging.getLogger("external-transport-client")
            self.close_calls = 0

        def close(self) -> None:
            self.close_calls += 1

    transport = CountingTransport()
    managed_logger = FakeManagedLogger()

    def create_logger(**kwargs):
        del kwargs
        return managed_logger

    monkeypatch.setattr(client_module, "create_client_logger", create_logger)
    client = APIClient(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        transport=transport,
    )

    await client.aclose()
    await client.aclose()

    assert transport.close_calls == 0
    assert managed_logger.close_calls == 1


@pytest.mark.asyncio
async def test_client_closes_owned_transport_once(monkeypatch) -> None:
    class CountingTransport:
        instances = []

        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs
            self.close_calls = 0
            self.instances.append(self)

        async def aclose(self) -> None:
            self.close_calls += 1

    monkeypatch.setattr(client_module, "AsyncTransport", CountingTransport)
    client = APIClient(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        logger=logging.getLogger("owned-transport-client"),
    )

    await client.aclose()
    await client.aclose()

    assert len(CountingTransport.instances) == 1
    assert CountingTransport.instances[0].close_calls == 1


@pytest.mark.asyncio
async def test_client_exposes_explicit_read_only_session_lifecycle() -> None:
    client = APIClient(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        logger=logging.getLogger("session-lifecycle-client"),
    )

    assert client.session_id is None
    assert client.contract_id is None

    client.restore_session(session_id="session-1", contract_id="contract-1")
    assert client.session_id == "session-1"
    assert client.contract_id == "contract-1"

    client.select_contract(contract_id="contract-2")
    assert client.session_id == "session-1"
    assert client.contract_id == "contract-2"

    with pytest.raises(AttributeError):
        client.session_id = "other-session"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        client.contract_id = "other-contract"  # type: ignore[misc]

    client.clear_session()
    assert client.session_id is None
    assert client.contract_id is None

    await client.aclose()


@pytest.mark.asyncio
async def test_client_rejects_incomplete_or_empty_session_lifecycle_values() -> None:
    client = APIClient(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        logger=logging.getLogger("invalid-session-lifecycle-client"),
    )

    with pytest.raises(ValueError, match="session_id"):
        client.restore_session(session_id=" ", contract_id="contract-1")
    with pytest.raises(ValueError, match="contract_id"):
        client.restore_session(session_id="session-1", contract_id=" ")
    with pytest.raises(ValueError, match="contract_id"):
        client.select_contract(contract_id=" ")

    assert client.session_id is None
    assert client.contract_id is None
    await client.aclose()
