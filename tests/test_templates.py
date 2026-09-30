import logging
from typing import Any

import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.templates import (
    TemplateCreateResponse,
    TemplateLimitCreateResponse,
)
from apisdkopti24.operations import Operation
from apisdkopti24.requests import RequestOptions
from apisdkopti24.services.templates import TemplatesService
from apisdkopti24.session import SessionManager
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
    assert kwargs["json_body"]["_method"] == "PUT"
    assert "_method" not in limits[0]


@pytest.mark.asyncio
async def test_update_template_limit_rejects_several_limits_before_request() -> None:
    client = DummyTemplatesClient()
    limit = {
        "contract_id": "contract-1",
        "product_type": "fuel",
        "sum": {"currency": "810", "value": 5000},
        "time": {"type": 5, "number": 1},
    }

    with pytest.raises(RequestValidationError, match="ровно один лимит"):
        await client.update_template_limit(
            template_id="template-1", limit_id="limit-1", limits=[limit, limit]
        )

    assert client.calls == []


@pytest.mark.asyncio
async def test_update_template_sends_put_method_override_by_default() -> None:
    client = DummyTemplatesClient()

    await client.update_template(template_id="template-1", type_="Limit", name="Main")

    operation, kwargs = client.calls[-1]
    assert operation == "update_template"
    assert kwargs["route_name"] == "default"
    assert kwargs["form"]["_method"] == "PUT"


@pytest.mark.asyncio
async def test_update_template_can_send_real_put() -> None:
    client = DummyTemplatesClient()

    await client.update_template(
        template_id="template-1", type_="Limit", name="Main", use_post=False
    )

    operation, kwargs = client.calls[-1]
    assert kwargs["route_name"] == "put"
    assert "_method" not in kwargs["form"]


class RecordingExecutor:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def execute(
        self, operation: Operation[Any] | str, options: RequestOptions | None = None
    ) -> Any:
        operation_name = operation.name if isinstance(operation, Operation) else operation
        request = options or RequestOptions()
        kwargs = {
            "api_version": request.api_version,
            "route_name": request.route_name,
            "path_params": request.path_params or None,
            "contract_header": request.contract_id,
            "query": dict(request.query) or None,
            "form": dict(request.form) if request.form is not None else None,
            "json_body": request.json_body,
        }
        self.calls.append((operation_name, kwargs))
        payload = self.responses[operation_name]
        if isinstance(operation, Operation):
            assert operation.response_type is not None
            return operation.response_type.model_validate(payload)
        return payload

    async def execute_stream(self, operation: str, **kwargs: Any) -> bytes:
        del kwargs
        raise AssertionError(f"Неожиданный запрос потоковой загрузки: {operation}")


class StubSessionContext:
    session_id = "session"
    contract_id = "contract"


class StubSessionGate:
    async def ensure_authenticated(self) -> str:
        return "session"


def recording_dependencies(executor: RecordingExecutor) -> tuple[object, ...]:
    return (
        executor,
        StubSessionContext(),
        StubSessionGate(),
        logging.getLogger("service-model-boundary-test"),
    )


@pytest.mark.asyncio
async def test_create_template_uses_request_model_and_typed_operation():
    executor = RecordingExecutor(
        {
            "create_template": {
                "status": {"code": 200},
                "data": "template-1",
                "timestamp": 1,
            }
        }
    )
    service = TemplatesService(*recording_dependencies(executor))
    result = await service.create_template(
        contract_id="contract-1",
        type_="Wallet",
        name="Main",
    )

    assert isinstance(result, TemplateCreateResponse)
    assert executor.calls[0][1]["form"] == {
        "contract_id": "contract-1",
        "type": "Wallet",
        "name": "Main",
    }


@pytest.mark.asyncio
async def test_update_template_limit_serializes_aliases_and_method_override():
    executor = RecordingExecutor(
        {
            "update_template_limit": {
                "status": {"code": 200},
                "data": "limit-1",
                "timestamp": 1,
            }
        }
    )
    service = TemplatesService(*recording_dependencies(executor))

    result = await service.update_template_limit(
        template_id="template-1",
        limit_id="limit-1",
        limits=[
            {
                "contract_id": "contract-1",
                "product_type": "fuel",
                "sum": {"currency": "810", "value": "5000"},
                "time": {"type": "5", "number": 1},
                "term": {"type": 1, "time": {"from": "03:00", "to": "08:00"}},
            }
        ],
    )

    assert isinstance(result, TemplateLimitCreateResponse)
    assert executor.calls[0][1]["json_body"] == {
        "contract_id": "contract-1",
        "product_type": "fuel",
        "sum": {"currency": "810", "value": 5000.0},
        "time": {"type": 5, "number": 1},
        "term": {"type": 1, "time": {"from": "03:00", "to": "08:00"}},
        "_method": "PUT",
    }


@pytest.mark.asyncio
async def test_template_payload_rejects_unknown_fields_before_request():
    executor = RecordingExecutor({})
    service = TemplatesService(*recording_dependencies(executor))

    with pytest.raises(ValidationError):
        await service.create_template_limit(
            template_id="template-1",
            payload={
                "contract_id": "contract-1",
                "product_type": "fuel",
                "sum": {"value": 5000},
                "time": {"type": 5, "number": 1},
                "unexpected": True,
            },
        )

    assert executor.calls == []


@pytest.mark.asyncio
async def test_template_limit_requires_amount_or_sum_before_request():
    executor = RecordingExecutor({})
    service = TemplatesService(*recording_dependencies(executor))

    with pytest.raises(ValueError, match="amount.*sum"):
        await service.create_template_limit(
            template_id="template-1",
            payload={
                "contract_id": "contract-1",
                "product_type": "fuel",
                "time": {"type": 5, "number": 1},
            },
        )

    assert executor.calls == []
