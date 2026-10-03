import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, ConnectionSettings
from apisdkopti24.credentials import StaticCredentialsProvider
from apisdkopti24.errors import (
    ContractSelectionError,
    NotAuthenticatedError,
    ResponseValidationError,
)


@pytest.mark.asyncio
async def test_client_auth_and_cards_flow_through_mock_transport(tmp_path) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/v1/authUser"):
            payload = {
                "status": {"code": 200},
                "data": {
                    "session_id": "session-1",
                    "client_id": "client-1",
                    "client_status": "Active",
                    "org_name": "Test organization",
                    "user_id": "user-1",
                    "contracts": [
                        {
                            "id": "contract-1",
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
                "timestamp": 1710000000,
            }
        elif request.url.path.endswith("/v2/cards"):
            payload = {
                "status": {"code": 200},
                "data": {"total_count": 0, "result": []},
                "timestamp": 1710000001,
            }
        else:
            raise AssertionError(f"Неожиданный запрос: {request.url}")
        return httpx.Response(200, json=payload, request=request)

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = AsyncTransport(
        "https://api.example.test/vip/",
        http_client=http_client,
    )
    settings = ConnectionSettings(
        base_url="https://api.example.test/vip/",
        logger_file=str(tmp_path / "sdk.log"),
        request_log_file=str(tmp_path / "requests.jsonl"),
    )
    credentials = StaticCredentialsProvider(
        api_key="api-key",
        login="demo",
        password="password",
    )

    async with APIClient(
        settings=settings,
        credentials_provider=credentials,
        transport=transport,
    ) as client:
        auth = await client.auth.auth_user()
        cards = await client.cards.get_cards_v2()

    assert auth.data.session_id == "session-1"
    assert client.contract_id == "contract-1"
    assert cards.total_count == 0
    assert requests[0].headers["api_key"] == "api-key"
    assert requests[1].headers["session_id"] == "session-1"
    assert requests[1].headers["contract_id"] == "contract-1"
    await http_client.aclose()


def _auth_success(session_id: str) -> dict[str, object]:
    return {
        "status": {"code": 200},
        "data": {
            "session_id": session_id,
            "client_id": "client-1",
            "client_status": "Active",
            "org_name": "Test organization",
            "user_id": "user-1",
            "contracts": [
                {
                    "id": "contract-1",
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


def _client(handler) -> tuple[APIClient, httpx.AsyncClient]:
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = AsyncTransport("https://api.example.test/vip/", http_client=http_client)
    client = APIClient(
        settings=ConnectionSettings(base_url="https://api.example.test/vip/"),
        transport=transport,
        credentials_provider=StaticCredentialsProvider(
            api_key="api-key", login="login", password="password"
        ),
    )
    return client, http_client


def _endpoint(request: httpx.Request) -> str:
    return request.url.path.rsplit("/", 1)[-1]


@pytest.mark.asyncio
async def test_rejected_credentials_do_not_trigger_a_second_login() -> None:
    sent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(_endpoint(request))
        body = {"status": {"code": 401, "message": "Неверный логин или пароль"}}
        return httpx.Response(401, json=body, request=request)

    client, http_client = _client(handler)
    with pytest.raises(NotAuthenticatedError):
        await client.cards.get_cards_v2(contract_id="contract-1")

    assert sent == ["authUser"]
    await client.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_unauthorized_protected_call_still_recovers_the_session_once() -> None:
    sent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        endpoint = _endpoint(request)
        sent.append(endpoint)
        if endpoint == "authUser":
            session_id = "session-1" if sent.count("authUser") == 1 else "session-2"
            return httpx.Response(200, json=_auth_success(session_id), request=request)
        if request.headers["session_id"] == "session-1":
            body = {"status": {"code": 401, "message": "Сессия истекла"}}
            return httpx.Response(401, json=body, request=request)
        body = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
        return httpx.Response(200, json=body, request=request)

    client, http_client = _client(handler)
    response = await client.cards.get_cards_v2()

    assert response.total_count == 0
    assert sent == ["authUser", "cards", "authUser", "cards"]
    await client.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_logoff_without_session_sends_no_request() -> None:
    sent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(_endpoint(request))
        raise AssertionError("logoff без сессии не должен обращаться к API")

    client, http_client = _client(handler)
    client.select_contract(contract_id="contract-1")

    assert await client.auth.logoff() is None

    assert sent == []
    assert client.contract_id is None
    await client.aclose()
    await http_client.aclose()


def _two_contracts_handler(sent: list[httpx.Request]):
    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        if _endpoint(request) == "authUser":
            payload = _auth_success("session-1")
            payload["data"]["contracts"] = [  # type: ignore[index]
                {
                    "id": "contract-1",
                    "number": "C-1",
                    "mpc": False,
                    "cards_count": 0,
                    "one_price": False,
                },
                {
                    "id": "contract-2",
                    "number": "C-2",
                    "mpc": False,
                    "cards_count": 0,
                    "one_price": False,
                },
            ]
            return httpx.Response(200, json=payload, request=request)
        body = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
        return httpx.Response(200, json=body, request=request)

    return handler


@pytest.mark.asyncio
async def test_explicit_contract_works_with_lazy_auth_on_multi_contract_account() -> None:
    sent: list[httpx.Request] = []
    client, http_client = _client(_two_contracts_handler(sent))

    cards = await client.cards.get_cards_v2(contract_id="contract-2")

    assert cards.total_count == 0
    assert [_endpoint(request) for request in sent] == ["authUser", "cards"]
    assert sent[1].headers["contract_id"] == "contract-2"
    assert client.contract_id is None
    await client.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_method_without_contract_lists_contracts_on_multi_contract_account() -> None:
    sent: list[httpx.Request] = []
    client, http_client = _client(_two_contracts_handler(sent))

    with pytest.raises(ContractSelectionError) as caught:
        await client.cards.get_cards_v2()

    assert caught.value.available_contracts == (("contract-1", "C-1"), ("contract-2", "C-2"))
    assert [_endpoint(request) for request in sent] == ["authUser"]

    client.select_contract(contract_id="contract-1")
    await client.cards.get_cards_v2()
    assert [_endpoint(request) for request in sent] == ["authUser", "cards"]
    assert sent[1].headers["contract_id"] == "contract-1"
    await client.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_explicit_auth_user_still_requires_a_contract_choice() -> None:
    sent: list[httpx.Request] = []
    client, http_client = _client(_two_contracts_handler(sent))

    with pytest.raises(ContractSelectionError):
        await client.auth.auth_user()

    assert client.session_id is None
    await client.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_empty_session_id_fails_authentication_with_typed_error() -> None:
    sent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(_endpoint(request))
        return httpx.Response(200, json=_auth_success(""), request=request)

    client, http_client = _client(handler)
    with pytest.raises(ResponseValidationError):
        await client.cards.get_cards_v2(contract_id="contract-1")

    assert sent == ["authUser"]
    assert client.session_id is None
    await client.aclose()
    await http_client.aclose()
