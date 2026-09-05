import asyncio
import logging

import pytest

from api_client_opti24.authentication import AuthenticationCoordinator
from api_client_opti24.models.auth import AuthUserResponse
from api_client_opti24.services import AuthService
from api_client_opti24.session import SessionManager, SessionState
from tests.service_support import (
    FrozenClock,
    NoopRequestExecutor,
    StubSessionGate,
    typed_request_stub,
)


class DummyClient(AuthService):
    def __init__(self):
        self.session_manager = SessionManager()
        self.calls = []

        class StubAuthenticator:
            async def authenticate(
                inner_self,
                *,
                api_version=None,
                contract_id=None,
                contract_number=None,
            ):
                del inner_self, api_version
                response = AuthUserResponse(**self._auth_payload())
                contracts = response.data.contracts
                selected = None
                if contract_id:
                    selected = next((item for item in contracts if item.id == contract_id), None)
                elif contract_number:
                    selected = next(
                        (item for item in contracts if item.number == contract_number),
                        None,
                    )
                elif contracts:
                    selected = contracts[0]
                self.session_manager.mark_authenticated(
                    response.data.session_id,
                    selected.id if selected else None,
                )
                return response

        super().__init__(
            NoopRequestExecutor(),
            self.session_manager,
            StubSessionGate(),
            self.session_manager,
            StubAuthenticator(),
            FrozenClock(),
            logging.getLogger("auth-service-test"),
        )

    @staticmethod
    def _auth_payload():
        return {
            "status": {"code": 200},
            "data": {
                "session_id": "SESSION123",
                "client_id": "client-1",
                "client_status": "active",
                "org_name": "Test organization",
                "user_id": "user-1",
                "contracts": [
                    {"id": "1-AAA", "number": "NV0001", "mpc": True},
                    {"id": "1-BBB", "number": "NV0002", "mpc": False},
                ],
                "role_id": "Supervisor",
                "role_name": "Administrator",
                "access": {"web": True, "api": True, "mobile": True},
                "email": "user@example.test",
            },
            "timestamp": 1710000000,
        }

    @typed_request_stub
    async def _request(self, operation, **kwargs):
        self.calls.append((operation, kwargs))
        if operation == "auth_user":
            return self._auth_payload()
        elif operation == "logoff":
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        elif operation == "get_info":
            return {
                "status": {"code": 200},
                "data": {
                    "from": "2025-01-01 00:00:00",
                    "to": "2025-01-31 23:59:59",
                    "client_info": {
                        "Client": "client-1",
                        "ClientType": "D",
                        "Contract": "1-AAA",
                        "ContractName": "Demo Client",
                    },
                    "methods": {"all": 42, "cards": 10, "cardgroups": 3, "card": 4},
                    "methods_info": {"actions_bill": {}, "actions_not_bill": {}},
                },
                "timestamp": 1710000000,
            }
        else:
            raise ValueError(f"Unexpected operation: {operation}")

    @property
    def session_id(self):
        return self.session_manager.session_id

    @session_id.setter
    def session_id(self, value):
        if value is None:
            self.session_manager.invalidate()
        else:
            self.session_manager.mark_authenticated(value, self.contract_id)

    @property
    def contract_id(self):
        return self.session_manager.contract_id

    @contract_id.setter
    def contract_id(self, value):
        self.session_manager.set_contract(value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "contract_id,contract_number,expected_id",
    [
        ("1-AAA", None, "1-AAA"),  # выбор по id
        (None, "NV0002", "1-BBB"),  # выбор по номеру
        (None, None, "1-AAA"),  # автоселект первого по списку
    ],
)
async def test_auth_user_sets_session_and_contract_id(contract_id, contract_number, expected_id):
    client = DummyClient()
    response = await client.auth_user(contract_id=contract_id, contract_number=contract_number)

    assert isinstance(response, AuthUserResponse)
    assert client.session_id == "SESSION123"
    assert client.contract_id == expected_id
    assert client.session_manager.state == SessionState.AUTHENTICATED


@pytest.mark.asyncio
async def test_logoff_returns_true():
    client = DummyClient()
    client.session_id = "SESSION123"  # имитируем авторизацию

    result = await client.logoff()

    assert result.status.code == 200
    assert result.data is True


@pytest.mark.asyncio
async def test_get_info_returns_data():
    client = DummyClient()
    client.session_id = "SESSION123"  # имитируем авторизацию

    result = await client.get_info()

    assert result.status.code == 200
    assert result.data.client_info.ContractName == "Demo Client"
    operation, kwargs = client.calls[-1]
    assert operation == "get_info"
    assert kwargs["params"]["period"] == "2026-07-19 12:30:00"


@pytest.mark.asyncio
async def test_get_info_uses_explicit_period():
    client = DummyClient()
    client.session_id = "SESSION123"

    await client.get_info(period="2025-01-15 12:30:00")

    operation, kwargs = client.calls[-1]
    assert operation == "get_info"
    assert kwargs["params"]["period"] == "2025-01-15 12:30:00"


@pytest.mark.asyncio
async def test_authentication_coordinator_preserves_contract_during_recovery():
    session = SessionManager()
    session.mark_authenticated("SESSION-OLD", "1-BBB")
    selected_contracts = []

    class RecordingAuthenticator:
        async def authenticate(
            self,
            *,
            api_version=None,
            contract_id=None,
            contract_number=None,
        ):
            del api_version, contract_number
            selected_contracts.append(contract_id)
            session.mark_authenticated("SESSION-NEW", contract_id)
            return AuthUserResponse(**DummyClient._auth_payload())

    coordinator = AuthenticationCoordinator(session, RecordingAuthenticator())

    recovered_session = await coordinator.recover()

    assert recovered_session == "SESSION-NEW"
    assert session.contract_id == "1-BBB"
    assert selected_contracts == ["1-BBB"]


@pytest.mark.asyncio
async def test_authentication_coordinator_authenticates_once_for_concurrent_calls():
    session = SessionManager()
    calls = 0
    started = asyncio.Event()
    release = asyncio.Event()

    class ConcurrentAuthenticator:
        async def authenticate(
            self,
            *,
            api_version=None,
            contract_id=None,
            contract_number=None,
        ):
            nonlocal calls
            del api_version, contract_id, contract_number
            calls += 1
            started.set()
            await release.wait()
            session.mark_authenticated("SESSION-NEW", "1-AAA")
            return AuthUserResponse(**DummyClient._auth_payload())

    coordinator = AuthenticationCoordinator(session, ConcurrentAuthenticator())

    tasks = [asyncio.create_task(coordinator.ensure_authenticated()) for _ in range(3)]
    await asyncio.wait_for(started.wait(), timeout=1)
    release.set()
    sessions = await asyncio.gather(*tasks)

    assert sessions == ["SESSION-NEW", "SESSION-NEW", "SESSION-NEW"]
    assert calls == 1


@pytest.mark.asyncio
async def test_authentication_coordinator_recovers_once_for_concurrent_failures():
    session = SessionManager()
    session.mark_authenticated("SESSION-OLD", "1-BBB")
    calls = 0
    selected_contracts = []
    started = asyncio.Event()
    release = asyncio.Event()

    class ConcurrentRecoveryAuthenticator:
        async def authenticate(
            self,
            *,
            api_version=None,
            contract_id=None,
            contract_number=None,
        ):
            nonlocal calls
            del api_version, contract_number
            calls += 1
            selected_contracts.append(contract_id)
            started.set()
            await release.wait()
            session.mark_authenticated("SESSION-NEW", contract_id)
            return AuthUserResponse(**DummyClient._auth_payload())

    coordinator = AuthenticationCoordinator(session, ConcurrentRecoveryAuthenticator())

    tasks = [asyncio.create_task(coordinator.recover()) for _ in range(3)]
    await asyncio.wait_for(started.wait(), timeout=1)
    release.set()
    sessions = await asyncio.gather(*tasks)

    assert sessions == ["SESSION-NEW", "SESSION-NEW", "SESSION-NEW"]
    assert calls == 1
    assert selected_contracts == ["1-BBB"]
    assert session.contract_id == "1-BBB"


@pytest.mark.asyncio
async def test_cancelled_authentication_does_not_poison_session_lock():
    session = SessionManager()
    started = asyncio.Event()
    release = asyncio.Event()

    class CancellableAuthenticator:
        async def authenticate(self, **kwargs):
            del kwargs
            started.set()
            await release.wait()
            session.mark_authenticated("SESSION-NEW", "1-AAA")
            return AuthUserResponse(**DummyClient._auth_payload())

    coordinator = AuthenticationCoordinator(session, CancellableAuthenticator())
    first = asyncio.create_task(coordinator.ensure_authenticated())
    await asyncio.wait_for(started.wait(), timeout=1)
    first.cancel()
    with pytest.raises(asyncio.CancelledError):
        await first

    release.set()
    assert await asyncio.wait_for(coordinator.ensure_authenticated(), timeout=1) == "SESSION-NEW"
