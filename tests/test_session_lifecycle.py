import logging

import pytest

from api_client_opti24 import APIClient
from api_client_opti24.session import SessionManager, SessionState


class StubTransport:
    async def aclose(self) -> None:
        return None


def test_session_manager_explicit_lifecycle() -> None:
    manager = SessionManager()
    initial_generation = manager.snapshot().generation

    manager.select_contract(" contract-1 ")
    assert manager.contract_id == "contract-1"

    manager.restore(session_id=" session-1 ", contract_id=" contract-1 ")
    assert manager.state is SessionState.AUTHENTICATED
    assert manager.session_id == "session-1"
    assert manager.request_context().contract_id == "contract-1"

    manager.clear()
    assert manager.state is SessionState.ANONYMOUS
    assert manager.session_id is None
    assert manager.contract_id is None
    assert manager.snapshot().generation == initial_generation + 3


@pytest.mark.parametrize(
    ("method_name", "kwargs"),
    [
        ("select_contract", {"contract_id": "  "}),
        ("restore_session", {"session_id": "", "contract_id": "contract-1"}),
        ("restore_session", {"session_id": "session-1", "contract_id": " "}),
    ],
)
def test_client_session_lifecycle_rejects_empty_values(
    method_name: str,
    kwargs: dict[str, str],
) -> None:
    client = APIClient(
        base_url="https://example.invalid/vip/",
        api_key="key",
        login="login",
        password="password",
        transport=StubTransport(),
        logger=logging.getLogger("session-lifecycle-test"),
    )

    with pytest.raises(ValueError, match="must not be empty"):
        getattr(client, method_name)(**kwargs)


def test_client_session_properties_are_read_only() -> None:
    assert APIClient.session_id.fset is None
    assert APIClient.contract_id.fset is None
