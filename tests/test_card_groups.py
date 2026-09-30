"""Сервис групп карт."""

import json
import logging
from pathlib import Path
from typing import Any

import pytest

from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.card_group import CardGroupAssignmentRequest
from apisdkopti24.operations import Operation
from apisdkopti24.requests import RequestOptions
from apisdkopti24.services.card_group import CardGroupsService
from apisdkopti24.session import SessionManager
from tests.service_support import StubSessionGate

FIXTURES = Path(__file__).parent / "fixtures" / "spec" / "1.1.60"


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
        kwargs = {
            key: value
            for key, value in kwargs.items()
            if value is not None
            or key in {"api_version", "route_name", "path_params", "contract_header"}
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


def fixture(domain: str, name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / domain / name).read_text(encoding="utf-8"))


def dependencies(
    executor: RecordingExecutor,
    contract_id: str | None = "contract-selected",
) -> tuple[object, ...]:
    session = SessionManager()
    session.mark_authenticated("session", contract_id)
    return (
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("section-2a-service-contracts"),
    )


@pytest.mark.asyncio
async def test_card_group_assignment_uses_selected_contract_and_strict_action() -> None:
    executor = RecordingExecutor(
        {"set_cards_to_group": fixture("card_groups", "set_cards_to_group.success.json")}
    )
    service = CardGroupsService(*dependencies(executor))

    await service.set_cards_to_group(
        group_id="group-1",
        cards_list=[
            CardGroupAssignmentRequest(id="card-1", type="Attach"),
            {"id": "card-2", "type": "Detach"},
        ],
    )

    assert executor.calls[0][1]["form"] == {
        "contract_id": "contract-selected",
        "group_id": "group-1",
        "cards_list": json.dumps(
            [
                {"id": "card-1", "type": "Attach"},
                {"id": "card-2", "type": "Detach"},
            ]
        ),
    }

    with pytest.raises(ValidationError):
        await service.set_cards_to_group(
            group_id="group-1",
            cards_list=[{"id": "card-1", "type": "Unknown"}],
        )

    with pytest.raises(ValidationError):
        await service.set_cards_to_group(
            group_id="group-1",
            cards_list=[{"id": "card-1", "type": "Attach", "unexpected": True}],
        )

    assert len(executor.calls) == 1
