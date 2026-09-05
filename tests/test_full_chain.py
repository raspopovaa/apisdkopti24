import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, ConnectionSettings
from apisdkopti24.credentials import StaticCredentialsProvider


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
                    "contracts": [{"id": "contract-1", "number": "C-1", "mpc": False}],
                    "role_id": "Supervisor",
                    "role_name": "Administrator",
                    "access": {"web": True, "api": True, "mobile": True},
                    "email": "user@example.test",
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
            raise AssertionError(f"Unexpected request: {request.url}")
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
