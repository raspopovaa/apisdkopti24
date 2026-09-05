import pytest

from api_client_opti24.services.templates import TemplatesService
from api_client_opti24.session import SessionManager
from tests.service_support import service_dependencies, typed_request_stub


class DummyTemplatesClient(TemplatesService):
    def __init__(self) -> None:
        self.session_manager = SessionManager()
        self.session_manager.mark_authenticated("session-1", "contract-1")
        self.calls = []
        super().__init__(*service_dependencies(self.session_manager))

    @property
    def session_id(self):
        return self.session_manager.session_id

    @property
    def contract_id(self):
        return self.session_manager.contract_id

    @typed_request_stub
    async def _request(self, operation, **kwargs):
        self.calls.append((operation, kwargs))
        return {"status": {"code": 200}, "data": "limit-1", "timestamp": 1710000000}


@pytest.mark.asyncio
async def test_update_template_limit_does_not_mutate_input() -> None:
    client = DummyTemplatesClient()
    limits = [
        {
            "contract_id": "contract-1",
            "product_type": "fuel",
            "sum": {"currency": "810", "value": 5000},
            "time": {"type": 5, "number": 1},
        }
    ]

    response = await client.update_template_limit(
        template_id="template-1",
        limit_id="limit-1",
        limits=limits,
        use_post=True,
    )

    operation, kwargs = client.calls[-1]
    assert response.data == "limit-1"
    assert operation == "update_template_limit"
    assert kwargs["route_name"] == "default"
    assert kwargs["path_params"] == {"template_id": "template-1", "limit_id": "limit-1"}
    assert kwargs["json"][0]["_method"] == "PUT"
    assert "_method" not in limits[0]
