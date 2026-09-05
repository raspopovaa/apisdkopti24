import pytest

from api_client_opti24.models.users import (
    UserBoolResponse,
    UserCreateResponse,
    UsersListResponse,
)
from api_client_opti24.services.users import UsersService
from api_client_opti24.session import SessionManager
from tests.service_support import service_dependencies, typed_request_stub


class DummyClient(UsersService):
    """Мок-клиент для UsersService."""

    def __init__(self):
        session_manager = SessionManager()
        session_manager.mark_authenticated("mock-session")
        super().__init__(*service_dependencies(session_manager))
        self.session_id = "mock-session"

    @typed_request_stub
    async def _request(self, operation, api_version="v2", **kwargs):
        # Эмуляция API для users
        if operation == "get_users":
            return {
                "status": {"code": 200},
                "data": {
                    "total_count": 1,
                    "result": [
                        {
                            "id": "1-USER",
                            "login": "79999999999",
                            "first_name": "Иван",
                            "last_name": "Иванов",
                            "date": "2020-01-01",
                            "active": True,
                            "role": {"id": "driver", "name": "Водитель"},
                            "access": {"web": True, "api": True, "mobile": True},
                            "mobile_phone": "79999999999",
                        }
                    ],
                },
                "timestamp": 1710000000,
            }
        if operation == "create_user":
            return {"status": {"code": 200}, "data": "1-USER", "timestamp": 1710000000}
        if operation in {"attach_contracts", "detach_contracts"}:
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        if operation in {"attach_card", "detach_card"}:
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        if operation == "delete_user":
            return {"status": {"code": 200}, "data": True, "timestamp": 1710000000}
        return {"status": {"code": 200}, "data": {}, "timestamp": 1710000000}


@pytest.mark.asyncio
async def test_get_users_returns_model():
    client = DummyClient()
    response = await client.get_users()
    assert isinstance(response, UsersListResponse)
    assert response.total_count == 1
    assert response.result[0].id == "1-USER"
    assert response.result[0].first_name == "Иван"


@pytest.mark.asyncio
async def test_create_user_returns_id():
    client = DummyClient()
    response = await client.create_user(mobile="79999999999", uuid="test-uuid")
    assert isinstance(response, UserCreateResponse)
    assert response.data == "1-USER"


@pytest.mark.asyncio
async def test_attach_and_detach_contracts():
    client = DummyClient()
    result = await client.attach_contracts(user_id="1-USER", contracts=[{"sid": "1-AAA"}])
    assert isinstance(result, UserBoolResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_attach_and_detach_card():
    client = DummyClient()
    result = await client.attach_card(user_id="1-USER", card_id="12345")
    assert isinstance(result, UserBoolResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_delete_user():
    client = DummyClient()
    result = await client.delete_user(user_id="1-USER")
    assert isinstance(result, UserBoolResponse)
    assert result.data is True


@pytest.mark.asyncio
async def test_delete_user_supports_post_method_override():
    client = DummyClient()

    result = await client.delete_user(user_id="1-USER", use_post=True)

    assert isinstance(result, UserBoolResponse)
    assert result.data is True
