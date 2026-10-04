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
    limit = {
        "contract_id": "contract-1",
        "product_type": "fuel",
        "sum": {"currency": "810", "value": 5000},
        "time": {"type": 5, "number": 1},
    }

    response = await client.update_template_limit(
        template_id="template-1",
        limit_id="limit-1",
        limit=limit,
        use_post=True,
    )

    operation, kwargs = client.calls[-1]
    assert response.data == "limit-1"
    assert operation == "update_template_limit"
    assert kwargs["route_name"] == "default"
    assert kwargs["path_params"] == {"template_id": "template-1", "limit_id": "limit-1"}
    assert kwargs["json_body"]["_method"] == "PUT"
    assert "_method" not in limit


@pytest.mark.asyncio
async def test_update_template_limit_rejects_several_limits_before_request() -> None:
    client = DummyTemplatesClient()
    limit = {
        "contract_id": "contract-1",
        "product_type": "fuel",
        "sum": {"currency": "810", "value": 5000},
        "time": {"type": 5, "number": 1},
    }

    with (
        pytest.warns(DeprecationWarning, match="limits"),
        pytest.raises(RequestValidationError, match="ровно один лимит"),
    ):
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
        limit={
            "contract_id": "contract-1",
            "product_type": "fuel",
            "sum": {"currency": "810", "value": "5000"},
            "time": {"type": 5, "number": 1},
            "term": {"type": 1, "time": {"from": "03:00", "to": "08:00"}},
        },
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


class _CountingGate:
    def __init__(self) -> None:
        self.calls = 0

    async def ensure_authenticated(self) -> str:
        self.calls += 1
        return "session"


def _gated_templates() -> tuple[TemplatesService, RecordingExecutor, _CountingGate]:
    executor = RecordingExecutor({})
    gate = _CountingGate()
    service = TemplatesService(executor, SessionManager(), gate, logging.getLogger("tpl"))
    return service, executor, gate


VALID_LIMIT = {
    "product_type": "fuel",
    "sum": {"currency": "810", "value": 5000},
    "time": {"type": 5, "number": 1},
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("create_template", {"type_": "Limit", "name": "x" * 31}),
        ("create_template", {"type_": "Limit", "name": " "}),
        ("create_template", {"type_": "Card", "name": "Main"}),
        ("update_template", {"template_id": " ", "type_": "Limit", "name": "Main"}),
        ("update_template", {"template_id": "tpl-1", "type_": "Limit", "name": "x" * 31}),
        ("create_template_limit", {"template_id": " ", "payload": VALID_LIMIT}),
        ("update_template_limit", {"template_id": "tpl-1", "limit_id": " ", "limit": VALID_LIMIT}),
        ("update_template_limit", {"template_id": "tpl-1", "limit_id": "lim-1"}),
        (
            "create_template_restriction",
            {"template_id": " ", "payload": {"product_type": "fuel", "restriction_type": 1}},
        ),
        (
            "update_template_georestriction",
            {
                "template_id": "tpl-1",
                "georestriction_id": " ",
                "payload": {"country": "RUS", "restriction_type": 1},
            },
        ),
        (
            "create_template_limit",
            {
                "template_id": "tpl-1",
                "contract_id": "contract-a",
                "payload": {**VALID_LIMIT, "contract_id": "contract-b"},
            },
        ),
    ],
    ids=[
        "name-too-long",
        "empty-name",
        "unknown-type",
        "update-empty-template",
        "update-name-too-long",
        "limit-empty-template",
        "update-limit-empty-limit-id",
        "update-limit-missing-limit",
        "restriction-empty-template",
        "geo-empty-id",
        "conflicting-contracts",
    ],
)
async def test_template_methods_reject_invalid_input_before_login(
    method: str, kwargs: dict[str, Any]
) -> None:
    service, executor, gate = _gated_templates()

    with pytest.raises(RequestValidationError):
        await getattr(service, method)(**kwargs)

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "limit_part",
    [
        {"sum": {"currency": "810", "valeu": 5000}},
        {"sum": {"currency": "810", "value": "10.005"}},
        {"time": {"type": 9, "number": 1}},
        {"term": {"type": 1, "days": "11111"}},
    ],
    ids=["typo-in-sum", "fraction-of-kopeck", "unknown-period", "bad-days-mask"],
)
async def test_template_limit_uses_strict_limit_parts(limit_part: dict[str, Any]) -> None:
    service, executor, gate = _gated_templates()

    with pytest.raises(ValidationError):
        await service.create_template_limit(
            template_id="tpl-1", payload={**VALID_LIMIT, **limit_part}
        )

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
async def test_update_template_limit_accepts_single_limit_without_warning(recwarn) -> None:
    executor = RecordingExecutor(
        {"update_template_limit": {"status": {"code": 200}, "data": "lim-1", "timestamp": 1}}
    )
    service = TemplatesService(*recording_dependencies(executor))

    await service.update_template_limit(
        template_id="tpl-1", limit_id="lim-1", limit={**VALID_LIMIT, "contract_id": "c-1"}
    )

    assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]
    assert executor.calls[0][1]["json_body"]["sum"] == {"currency": "810", "value": 5000.0}
