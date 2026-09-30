"""Выбор договора при авторизации и договор, который сервисы подставляют в запросы."""

import asyncio
import logging
from typing import Any, TypeVar

import pytest

from apisdkopti24 import ContractSelectionError
from apisdkopti24.authentication import (
    AuthenticationCoordinator,
    DefaultAuthenticator,
)
from apisdkopti24.execution_budget import OperationBudget
from apisdkopti24.models.auth import AuthUserResponse
from apisdkopti24.operations import Operation
from apisdkopti24.requests import (
    RequestOptions,
)
from apisdkopti24.services.card_group import CardGroupsService
from apisdkopti24.services.cards import CardsService
from apisdkopti24.services.contract import ContractsService
from apisdkopti24.services.templates import TemplatesService
from apisdkopti24.session import SessionManager, SessionState
from tests.service_support import RecordingRequestExecutor, StubSessionGate


class StubRequestExecutor:
    def __init__(self, contracts: list[dict[str, Any]]) -> None:
        self.contracts = contracts
        self.calls = 0

    async def execute(
        self,
        operation: Operation[AuthUserResponse] | str,
        **kwargs: Any,
    ) -> AuthUserResponse | dict[str, Any]:
        del kwargs
        self.calls += 1
        operation_name = operation.name if isinstance(operation, Operation) else operation
        assert operation_name == "auth_user"
        payload = {
            "status": {"code": 200},
            "data": {
                "session_id": "new-session",
                "client_id": "client",
                "client_status": "active",
                "org_name": "Test organization",
                "user_id": "user",
                "contracts": self.contracts,
                "role_id": "Supervisor",
                "role_name": "Administrator",
                "access": {"web": True, "api": True, "mobile": True},
                "email": "user@example.test",
                "read_only": False,
            },
            "timestamp": 1,
        }
        if isinstance(operation, Operation):
            assert operation.response_type is not None
            return operation.response_type.model_validate(payload)
        return payload


class Credentials:
    def get_credentials(self) -> tuple[str, str]:
        return "login", "password"


def contract(identifier: str, number: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "number": number,
        "mpc": False,
        "cards_count": 0,
        "one_price": False,
    }


@pytest.mark.asyncio
async def test_multiple_contracts_require_explicit_selection() -> None:
    session = SessionManager()
    executor = StubRequestExecutor([contract("A", "1"), contract("B", "2")])
    authenticator = DefaultAuthenticator(
        executor, session, Credentials(), logging.getLogger("auth-test")
    )

    with pytest.raises(ContractSelectionError) as exc_info:
        await authenticator.authenticate()

    assert exc_info.value.available_contracts == (("A", "1"), ("B", "2"))
    assert "A" not in str(exc_info.value)
    assert "B" not in str(exc_info.value)
    assert session.state == SessionState.INVALID
    assert session.session_id is None
    assert session.contract_id is None


@pytest.mark.asyncio
async def test_single_contract_is_selected_automatically() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    await authenticator.authenticate()

    assert session.contract_id == "A"


@pytest.mark.asyncio
async def test_both_contract_selectors_are_rejected_before_network() -> None:
    session = SessionManager()
    executor = StubRequestExecutor([contract("A", "1")])
    authenticator = DefaultAuthenticator(
        executor, session, Credentials(), logging.getLogger("auth-test")
    )

    with pytest.raises(ContractSelectionError):
        await authenticator.authenticate(contract_id="A", contract_number="1")

    assert executor.calls == 0


@pytest.mark.asyncio
async def test_recovery_preserves_selected_contract() -> None:
    session = SessionManager()
    session.mark_authenticated("expired-session", "B")
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1"), contract("B", "2")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)

    await coordinator.recover(OperationBudget(deadline_at=60.0, max_attempts=3))

    assert session.session_id == "new-session"
    assert session.contract_id == "B"


@pytest.mark.asyncio
async def test_authentication_without_contracts_keeps_contract_unset() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    await authenticator.authenticate()

    assert session.session_id == "new-session"
    assert session.contract_id is None
    assert session.state == SessionState.AUTHENTICATED


@pytest.mark.asyncio
async def test_unknown_contract_does_not_fall_back_to_first() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1"), contract("B", "2")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    with pytest.raises(ContractSelectionError) as exc_info:
        await authenticator.authenticate(contract_id="missing")

    assert exc_info.value.available_contracts == (("A", "1"), ("B", "2"))
    assert session.session_id is None
    assert session.contract_id is None


@pytest.mark.asyncio
async def test_duplicate_contract_number_is_ambiguous() -> None:
    session = SessionManager()
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "same"), contract("B", "same")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )

    with pytest.raises(ContractSelectionError):
        await authenticator.authenticate(contract_number="same")

    assert session.session_id is None
    assert session.contract_id is None


@pytest.mark.asyncio
async def test_lazy_authentication_uses_preselected_contract_once_concurrently() -> None:
    session = SessionManager()
    session.set_contract("B")
    executor = StubRequestExecutor([contract("A", "1"), contract("B", "2")])
    authenticator = DefaultAuthenticator(
        executor,
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)

    session_ids = await asyncio.gather(*(coordinator.ensure_authenticated() for _ in range(20)))

    assert session_ids == ["new-session"] * 20
    assert executor.calls == 1
    assert session.contract_id == "B"


@pytest.mark.asyncio
async def test_recovery_fails_if_selected_contract_is_no_longer_available() -> None:
    session = SessionManager()
    session.mark_authenticated("expired-session", "B")
    authenticator = DefaultAuthenticator(
        StubRequestExecutor([contract("A", "1")]),
        session,
        Credentials(),
        logging.getLogger("auth-test"),
    )
    coordinator = AuthenticationCoordinator(session, authenticator)

    with pytest.raises(ContractSelectionError):
        await coordinator.recover(OperationBudget(deadline_at=60.0, max_attempts=3))

    assert session.session_id is None
    assert session.contract_id is None
    assert session.state == SessionState.INVALID


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
        payload = kwargs.get("query") or kwargs.get("form")
        assert payload["contract_id"] == "contract-selected"


@pytest.mark.asyncio
async def test_contract_bound_method_fails_before_request_without_selected_contract() -> None:
    executor = RecordingExecutor({})
    service = CardsService(*dependencies(executor, contract_id=None))

    with pytest.raises(ValueError, match="Необходимо указать contract_id"):
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

    assert executor.calls[0][1]["query"]["contract_id"] == "contract-explicit"


ServiceT = TypeVar("ServiceT")


def _response(data: Any) -> dict[str, Any]:
    return {"status": {"code": 200}, "data": data, "timestamp": 1710000000}


def _service(
    service_type: type[ServiceT],
    responses: dict[str, dict[str, Any]],
    *,
    contract_id: str = "session-contract",
) -> tuple[ServiceT, RecordingRequestExecutor]:
    executor = RecordingRequestExecutor(responses)
    session = SessionManager()
    session.mark_authenticated("session-id", contract_id)
    service = service_type(
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("section-2b-test"),
    )
    return service, executor


@pytest.mark.asyncio
async def test_contract_fallback_and_explicit_override() -> None:
    service, executor = _service(
        ContractsService,
        {"get_payments": _response({"total_count": 0, "result": []})},
    )

    await service.get_payments()
    await service.get_payments(contract_id="explicit-contract")

    assert executor.calls[0][1]["query"] == {"contract_id": "session-contract"}
    assert executor.calls[1][1]["query"] == {"contract_id": "explicit-contract"}


@pytest.mark.asyncio
async def test_header_contract_override_is_forwarded() -> None:
    service, executor = _service(
        ContractsService,
        {"get_documents": _response({"total_count": 0, "result": []})},
    )

    await service.get_documents(
        date_start="2026-01-01",
        date_end="2026-01-31",
        contract_id="explicit-contract",
    )

    assert executor.calls[0][1]["contract_header"] == "explicit-contract"


@pytest.mark.asyncio
async def test_template_contract_fallback_and_override() -> None:
    service, executor = _service(
        TemplatesService,
        {
            "create_template": _response("template-1"),
            "create_template_restriction": _response("restriction-1"),
        },
    )

    await service.create_template(type_="Limit", name="Default")
    await service.create_template_restriction(
        template_id="template-1",
        contract_id="explicit-contract",
        payload={
            "product_type": "fuel",
            "restriction_type": 1,
        },
    )

    assert executor.calls[0][1]["form"]["contract_id"] == "session-contract"
    assert executor.calls[1][1]["json_body"]["contract_id"] == "explicit-contract"
