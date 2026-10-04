"""Сервис групп карт."""

import json
import logging
from pathlib import Path
from typing import Any

import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.card_group import CardGroupAssignmentRequest
from apisdkopti24.services.card_group import CardGroupsService
from apisdkopti24.session import SessionManager
from tests.service_support import RecordingRequestExecutor, StubSessionGate

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
        logging.getLogger("card-groups-test"),
    )


@pytest.mark.asyncio
async def test_card_group_assignment_uses_selected_contract_and_strict_action() -> None:
    executor = RecordingRequestExecutor(
        {"set_cards_to_group": fixture("card_groups", "set_cards_to_group.success.json")},
        omit_empty=True,
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
        # Компактный JSON, как во всех методах SDK (to_json_param).
        "cards_list": '[{"id":"card-1","type":"Attach"},{"id":"card-2","type":"Detach"}]',
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


@pytest.mark.parametrize(
    ("name", "message"),
    [("Г" * 51, "не длиннее 50"), ("Отдел: Север", "двоеточие")],
)
@pytest.mark.asyncio
async def test_set_card_group_rejects_invalid_name_before_request(name, message) -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = CardGroupsService(*dependencies(executor))

    with pytest.raises(RequestValidationError, match=message):
        await service.set_card_group(name=name)

    assert executor.calls == []


@pytest.mark.asyncio
async def test_set_cards_to_group_rejects_empty_list_with_typed_error() -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = CardGroupsService(*dependencies(executor))

    with pytest.raises(RequestValidationError, match="cards_list"):
        await service.set_cards_to_group(group_id="group-1", cards_list=[])

    assert executor.calls == []
