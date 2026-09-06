import inspect
import json
import logging
from pathlib import Path
from typing import Any

import pytest

from apisdkopti24.modeling import ValidationError
from apisdkopti24.models.card_group import CardGroupAssignmentRequest
from apisdkopti24.models.invites import (
    InviteCreateRequest,
    InviteListResponse,
    InviteResponse,
)
from apisdkopti24.models.users import UserAttachContractRequest, UserBoolResponse
from apisdkopti24.operations import Operation
from apisdkopti24.requests import RequestOptions
from apisdkopti24.services.auth import AuthService
from apisdkopti24.services.card_group import CardGroupsService
from apisdkopti24.services.cards import CardsService
from apisdkopti24.services.invites import InvitesService
from apisdkopti24.services.users import UsersService
from apisdkopti24.services.virtual_cards import VirtualCardsService
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
            "request_contract_id": request.contract_id,
            "params": dict(request.query) or None,
            "data": dict(request.form) if request.form is not None else None,
            "json": request.json_body,
        }
        kwargs = {
            key: value
            for key, value in kwargs.items()
            if value is not None
            or key in {"api_version", "route_name", "path_params", "request_contract_id"}
        }
        self.calls.append((operation_name, kwargs))
        payload = self.responses[operation_name]
        if isinstance(operation, Operation):
            assert operation.response_type is not None
            return operation.response_type.model_validate(payload)
        return payload

    async def execute_stream(self, operation: str, **kwargs: Any) -> bytes:
        del kwargs
        raise AssertionError(f"Unexpected stream request: {operation}")


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
async def test_attach_contracts_validates_and_serializes_request_model() -> None:
    executor = RecordingExecutor(
        {"attach_contracts": fixture("users", "attach_contracts.success.json")}
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
                "request_contract_id": None,
                "json": [
                    {"sid": "contract-1", "use_mpc": True},
                    {"sid": "contract-2", "template_id": "template-1"},
                ],
            },
        )
    ]


@pytest.mark.asyncio
async def test_attach_contracts_rejects_unknown_fields_before_request() -> None:
    executor = RecordingExecutor({})
    service = UsersService(*dependencies(executor))

    with pytest.raises(ValidationError):
        await service.attach_contracts(
            user_id="user-1",
            contracts=[{"sid": "contract-1", "unexpected": True}],
        )

    assert executor.calls == []


@pytest.mark.asyncio
async def test_create_invite_serializes_request_and_returns_full_envelope() -> None:
    executor = RecordingExecutor(
        {"create_invite": fixture("invites", "create_invite.success.json")}
    )
    service = InvitesService(*dependencies(executor))

    result = await service.create_invite(
        data=InviteCreateRequest(
            role="Driver",
            mobile="79990000000",
            contracts=[{"sid": "contract-1"}],
        ),
        with_send=False,
    )

    assert isinstance(result, InviteResponse)
    assert result.status.code == 200
    assert result.timestamp == 1596024392
    assert executor.calls[0][1]["route_name"] == "without_send"
    assert executor.calls[0][1]["json"] == {
        "role": "Driver",
        "mobile": "79990000000",
        "contracts": [{"id": "contract-1"}],
    }


@pytest.mark.asyncio
async def test_create_invite_requires_recipient_before_request() -> None:
    executor = RecordingExecutor({})
    service = InvitesService(*dependencies(executor))

    with pytest.raises(ValidationError, match="mobile or email"):
        await service.create_invite(data={"role": "Driver"})

    assert executor.calls == []


@pytest.mark.asyncio
async def test_create_invite_rejects_unknown_fields_before_request() -> None:
    executor = RecordingExecutor({})
    service = InvitesService(*dependencies(executor))

    with pytest.raises(ValidationError):
        await service.create_invite(
            data={"role": "Driver", "mobile": "79990000000", "unexpected": True}
        )

    assert executor.calls == []


@pytest.mark.asyncio
async def test_get_invites_returns_full_envelope() -> None:
    executor = RecordingExecutor({"get_invites": fixture("invites", "get_invites.success.json")})
    service = InvitesService(*dependencies(executor))

    result = await service.get_invites()

    assert isinstance(result, InviteListResponse)
    assert result.status.code == 200
    assert result.data.total_count == 1
    assert result.timestamp == 1591147422


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

    assert executor.calls[0][1]["data"] == {
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


@pytest.mark.asyncio
async def test_contract_bound_card_group_methods_use_selected_contract() -> None:
    executor = RecordingExecutor(
        {
            "get_card_groups": {
                "status": {"code": 200},
                "data": {"total_count": 0, "result": []},
                "timestamp": 1,
            },
            "set_card_group": {
                "status": {"code": 200},
                "data": {"id": "group-1"},
                "timestamp": 1,
            },
            "remove_card_group": {
                "status": {"code": 200},
                "data": True,
                "timestamp": 1,
            },
        }
    )
    service = CardGroupsService(*dependencies(executor))

    await service.get_card_groups()
    await service.set_card_group(name="group")
    await service.remove_card_group(group_id="group-1")

    for _, kwargs in executor.calls:
        payload = kwargs.get("params") or kwargs.get("data")
        assert payload["contract_id"] == "contract-selected"


@pytest.mark.asyncio
async def test_contract_bound_method_fails_before_request_without_selected_contract() -> None:
    executor = RecordingExecutor({})
    service = CardsService(*dependencies(executor, contract_id=None))

    with pytest.raises(ValueError, match="contract_id is required"):
        await service.get_cards_v1()

    assert executor.calls == []


@pytest.mark.asyncio
async def test_explicit_contract_takes_priority_over_selected_contract() -> None:
    executor = RecordingExecutor(
        {
            "get_cards_v1": {
                "status": {"code": 200},
                "data": {"total_count": 0, "result": []},
                "timestamp": 1,
            }
        }
    )
    service = CardsService(*dependencies(executor))

    await service.get_cards_v1(contract_id="contract-explicit")

    assert executor.calls[0][1]["params"]["contract_id"] == "contract-explicit"


def test_section_2a_public_service_parameters_are_keyword_only() -> None:
    methods = {
        AuthService: ("logoff", "get_info", "auth_user"),
        UsersService: (
            "get_users",
            "create_user",
            "attach_contracts",
            "detach_contracts",
            "attach_card",
            "detach_card",
            "delete_user",
        ),
        InvitesService: (
            "get_invites",
            "create_invite",
            "delete_invite",
            "resend_invite",
            "prolong_invite",
        ),
        CardsService: (
            "get_cards_v1",
            "get_cards_v2",
            "get_cards_by_group",
            "get_card_drivers",
            "get_card_detail",
            "block_card",
            "set_card_comment",
            "verify_pin",
            "reset_pin",
        ),
        CardGroupsService: (
            "get_card_groups",
            "set_card_group",
            "set_cards_to_group",
            "remove_card_group",
        ),
        VirtualCardsService: ("create_virtual_card", "release_virtual_card"),
    }

    for service_type, method_names in methods.items():
        for method_name in method_names:
            parameters = list(
                inspect.signature(getattr(service_type, method_name)).parameters.values()
            )
            assert parameters[0].name == "self"
            assert all(
                parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters[1:]
            )


def test_qr_mpc_method_parameter_kinds_remain_unchanged() -> None:
    positional_parameters = {
        "delete_mpc": ("card_id", "api_version"),
        "reset_mpc": ("card_id", "type_", "api_version"),
    }

    for method_name, expected in positional_parameters.items():
        parameters = list(
            inspect.signature(getattr(VirtualCardsService, method_name)).parameters.values()
        )
        assert tuple(parameter.name for parameter in parameters[1 : 1 + len(expected)]) == expected
        assert all(
            parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
            for parameter in parameters[1 : 1 + len(expected)]
        )
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in parameters[1 + len(expected) :]
        )
