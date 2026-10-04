import json
import logging
from pathlib import Path
from typing import Any

import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.users import (
    UserAttachContractRequest,
    UserBoolResponse,
    UserCreateResponse,
    UserListResponse,
)
from apisdkopti24.services.users import UsersService
from apisdkopti24.session import SessionManager
from tests.service_support import (
    RecordingRequestExecutor,
    StubSessionGate,
    service_dependencies,
    typed_request_stub,
)


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
                            "login": "79990000010",
                            "first_name": "Иван",
                            "last_name": "Иванов",
                            "middle_name": "Иванович",
                            "date": "2020-01-01",
                            "active": True,
                            "role": {"id": "driver", "name": "Водитель"},
                            "access": {"web": True, "api": True, "mobile": True},
                            "mobile_phone": "79990000010",
                            "position": "Водитель",
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
    assert isinstance(response, UserListResponse)
    assert response.total_count == 1
    assert response.result[0].id == "1-USER"
    assert response.result[0].first_name == "Иван"


def test_user_date_is_required_but_nullable() -> None:
    from apisdkopti24.models.users import UserItem

    payload = {
        "id": "user-id",
        "login": "login",
        "first_name": "",
        "last_name": "",
        "middle_name": "",
        "date": None,
        "position": "",
        "role": {"id": "Driver", "name": "Водитель"},
        "access": {"web": False, "api": False, "mobile": True},
    }
    assert UserItem.model_validate(payload).date is None


@pytest.mark.asyncio
async def test_create_user_returns_id():
    client = DummyClient()
    response = await client.create_user(mobile="79990000010", uuid="test-uuid")
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


FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"


def fixture(domain: str, name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / domain / name).read_text(encoding="utf-8"))


def dependencies(
    executor: RecordingRequestExecutor,
    contract_id: str | None = "contract-selected",
) -> tuple[object, ...]:
    session = SessionManager()
    session.mark_authenticated("session", contract_id)
    return (
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("users-test"),
    )


@pytest.mark.asyncio
async def test_attach_contracts_validates_and_serializes_request_model() -> None:
    executor = RecordingRequestExecutor(
        {"attach_contracts": fixture("users", "attach_contracts.success.json")}, omit_empty=True
    )
    service = UsersService(*dependencies(executor))

    result = await service.attach_contracts(
        user_id="user-1",
        contracts=[
            UserAttachContractRequest(sid="contract-1", use_mpc=True),
            {"sid": "contract-2", "template_id": "template-1"},
        ],
    )

    assert isinstance(result, UserBoolResponse)
    assert executor.calls == [
        (
            "attach_contracts",
            {
                "api_version": None,
                "route_name": "default",
                "path_params": {"user_id": "user-1"},
                "contract_header": None,
                "json_body": [
                    {"sid": "contract-1", "use_mpc": True},
                    {"sid": "contract-2", "template_id": "template-1"},
                ],
            },
        )
    ]


@pytest.mark.asyncio
async def test_attach_contracts_rejects_unknown_fields_before_request() -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = UsersService(*dependencies(executor))

    with pytest.raises(ValidationError):
        await service.attach_contracts(
            user_id="user-1",
            contracts=[{"sid": "contract-1", "unexpected": True}],
        )

    assert executor.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("create_user", {"uuid": "external-1", "mobile": "+79990000000"}),
        ("create_user", {"uuid": "external-1", "mobile": "7999999999"}),
        ("create_user", {"uuid": " ", "mobile": "79990000000"}),
        ("attach_contracts", {"user_id": "user-1", "contracts": []}),
        ("attach_contracts", {"user_id": " ", "contracts": [{"sid": "contract-1"}]}),
        ("detach_contracts", {"user_id": "user-1", "contracts": []}),
        ("detach_contracts", {"user_id": "user-1", "contracts": [" "]}),
        ("attach_card", {"user_id": "user-1", "card_id": " "}),
        ("detach_card", {"user_id": "user-1", "card_id": ""}),
        ("get_users", {"sort": "bogus"}),
        ("get_users", {"sort": "login,-unknown"}),
    ],
    ids=[
        "mobile-with-plus",
        "mobile-ten-digits",
        "empty-uuid",
        "attach-empty-contracts",
        "attach-empty-user",
        "detach-empty-contracts",
        "detach-empty-contract-id",
        "attach-empty-card",
        "detach-empty-card",
        "unknown-sort",
        "unknown-desc-sort",
    ],
)
async def test_invalid_scalar_arguments_raise_typed_error_before_request(
    method: str, kwargs: dict[str, Any]
) -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = UsersService(*dependencies(executor))

    with pytest.raises(RequestValidationError):
        await getattr(service, method)(**kwargs)

    assert executor.calls == []


@pytest.mark.asyncio
async def test_get_users_rejects_unknown_role_filter_before_request() -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = UsersService(*dependencies(executor))

    with pytest.raises(ValidationError):
        await service.get_users(filter={"role": "Admin"})

    assert executor.calls == []


@pytest.mark.asyncio
async def test_get_users_sends_normalized_sort_and_role_filter() -> None:
    executor = RecordingRequestExecutor(
        {"get_users": {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}},
        omit_empty=True,
    )
    service = UsersService(*dependencies(executor))

    await service.get_users(sort="login, -id", filter={"role": "Readonly", "active": True})

    query = executor.calls[0][1]["query"]
    assert query["sort"] == "login,-id"
    assert json.loads(query["filter"]) == {"role": "Readonly", "active": True}


@pytest.mark.asyncio
async def test_create_user_sends_mobile_digits_as_form() -> None:
    executor = RecordingRequestExecutor(
        {"create_user": {"status": {"code": 200}, "data": "user-1", "timestamp": 1}},
        omit_empty=True,
    )
    service = UsersService(*dependencies(executor))

    await service.create_user(uuid="external-1", mobile=" 79990000000 ")

    assert executor.calls[0][1]["form"] == {"uuid": "external-1", "mobile": "79990000000"}


def test_users_list_response_alias_is_removed() -> None:
    import apisdkopti24.models.users as users_models

    assert not hasattr(users_models, "UsersListResponse")


def _users_page(total_count: int) -> dict[str, Any]:
    page = fixture("users", "get_users.success.json")
    page["data"]["result"] = page["data"]["result"][:1]
    page["data"]["total_count"] = total_count
    return page


@pytest.mark.asyncio
async def test_iter_users_pages_until_total_count_and_forwards_filters() -> None:
    # Страница отдаёт одного пользователя, всего 3: нужны страницы 1, 2 и 3.
    executor = RecordingRequestExecutor({"get_users": _users_page(3)}, omit_empty=True)
    service = UsersService(*dependencies(executor))

    users = [
        user
        async for user in service.iter_users(
            sort="-id", filter={"role": "Driver"}, contract_id="contract-1", on_page=1
        )
    ]

    assert len(users) == 3
    queries = [call["query"] for _, call in executor.calls]
    assert [query["page"] for query in queries] == [1, 2, 3]
    assert all(query["on_page"] == 1 and query["sort"] == "-id" for query in queries)
    assert all(query["contract_id"] == "contract-1" for query in queries)


@pytest.mark.asyncio
async def test_iter_users_stops_at_max_pages() -> None:
    executor = RecordingRequestExecutor({"get_users": _users_page(100)}, omit_empty=True)
    service = UsersService(*dependencies(executor))

    users = [user async for user in service.iter_users(on_page=1, max_pages=2)]

    assert len(users) == 2
    assert len(executor.calls) == 2
