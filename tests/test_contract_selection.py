"""Выбор договора при авторизации и договор, который сервисы подставляют в запросы."""

import asyncio
import logging
from typing import Any, TypeVar, cast

import pytest

from apisdkopti24 import ContractSelectionError
from apisdkopti24.authentication import (
    AUTH_USER,
    AuthenticationCoordinator,
    DefaultAuthenticator,
    _select_contract,
)
from apisdkopti24.execution_budget import OperationBudget
from apisdkopti24.models.auth import AuthUserResponse, ContractInfo
from apisdkopti24.operations import OperationSpec
from apisdkopti24.requests import RequestOptions
from apisdkopti24.service_base import _BaseService
from apisdkopti24.services.card_group import CardGroupsService
from apisdkopti24.services.cards import CardsService
from apisdkopti24.services.contract import ContractsService
from apisdkopti24.services.templates import TemplatesService
from apisdkopti24.session import SessionManager, SessionState
from tests.service_support import RecordingRequestExecutor, ServiceDependencies, StubSessionGate

ResponseT = TypeVar("ResponseT")


class StubRequestExecutor:
    def __init__(self, contracts: list[dict[str, Any]]) -> None:
        self.contracts = contracts
        self.calls = 0
        self.budgets: list[OperationBudget | None] = []

    def create_budget(self, operation: object) -> OperationBudget:
        del operation
        return OperationBudget(deadline_at=float("inf"), max_attempts=1)

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
        *,
        budget: OperationBudget | None = None,
    ) -> ResponseT:
        del options
        self.budgets.append(budget)
        self.calls += 1
        assert operation.name == "auth_user"
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
        assert operation.response_type is not None
        return cast(ResponseT, cast(Any, operation.response_type).model_validate(payload))


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


def dependencies(
    executor: RecordingRequestExecutor,
    contract_id: str | None = "contract-selected",
) -> ServiceDependencies:
    session = SessionManager()
    session.mark_authenticated("session", contract_id)
    return (
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("contract-selection-test"),
    )


@pytest.mark.asyncio
async def test_contract_bound_card_group_methods_use_selected_contract() -> None:
    executor = RecordingRequestExecutor(
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
        },
        omit_empty=True,
    )
    service = CardGroupsService(*dependencies(executor))

    await service.get_card_groups()
    await service.set_card_group(name="group")
    await service.remove_card_group(group_id="group-1")

    for _, kwargs in executor.calls:
        payload = kwargs.get("query") or kwargs.get("form")
        assert payload is not None
        assert payload["contract_id"] == "contract-selected"


@pytest.mark.asyncio
async def test_contract_bound_method_fails_before_request_without_selected_contract() -> None:
    executor = RecordingRequestExecutor({}, omit_empty=True)
    service = CardsService(*dependencies(executor, contract_id=None))

    with pytest.raises(ValueError, match="Необходимо указать contract_id"):
        await service.get_cards_v1()

    assert executor.calls == []


@pytest.mark.asyncio
async def test_explicit_contract_takes_priority_over_selected_contract() -> None:
    executor = RecordingRequestExecutor(
        {
            "get_cards_v1": {
                "status": {"code": 200},
                "data": {"total_count": 0, "result": []},
                "timestamp": 1,
            }
        },
        omit_empty=True,
    )
    service = CardsService(*dependencies(executor))

    await service.get_cards_v1(contract_id="contract-explicit")

    assert executor.calls[0][1]["query"]["contract_id"] == "contract-explicit"


ServiceT = TypeVar("ServiceT", bound=_BaseService)


def _response(data: Any) -> dict[str, Any]:
    return {"status": {"code": 200}, "data": data, "timestamp": 1710000000}


def _service(
    service_type: type[ServiceT],
    responses: dict[str, dict[str, Any]],
    *,
    contract_id: str = "session-contract",
) -> tuple[ServiceT, RecordingRequestExecutor]:
    executor = RecordingRequestExecutor(responses, omit_empty=True)
    session = SessionManager()
    session.mark_authenticated("session-id", contract_id)
    service = service_type(
        executor,
        session,
        StubSessionGate(),
        logging.getLogger("contract-selection-test"),
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


@pytest.mark.asyncio
async def test_login_budget_comes_from_the_executor_factory() -> None:
    # Раньше без create_budget вход тихо получал другой лимит: 60 с и одна попытка.
    executor = StubRequestExecutor([contract("A", "1")])
    authenticator = DefaultAuthenticator(
        executor, SessionManager(), Credentials(), logging.getLogger("auth-budget")
    )

    await authenticator.authenticate()

    (budget,) = executor.budgets
    assert budget is not None
    assert budget.max_attempts == 1
    assert budget.deadline_at == float("inf")


def contract_infos(*pairs: tuple[str, str]) -> list[ContractInfo]:
    return [ContractInfo.model_validate(contract(*pair)) for pair in pairs]


def test_contract_number_selects_by_number_not_by_id() -> None:
    # Номер одного договора совпадает с ID другого: выбор идёт только по номеру.
    contracts = contract_infos(("A", "B"), ("B", "A"))

    selected = _select_contract(contracts, contract_id=None, contract_number="B")

    assert selected is not None
    assert selected.id == "A"


def test_contract_id_selects_by_id_not_by_number() -> None:
    contracts = contract_infos(("A", "B"), ("B", "A"))

    selected = _select_contract(contracts, contract_id="B", contract_number=None)

    assert selected is not None
    assert selected.id == "B"


@pytest.mark.parametrize(
    ("contract_id", "contract_number", "field"),
    [("missing", None, "contract_id"), (None, "missing", "contract_number")],
)
def test_unavailable_contract_error_names_the_requested_field(
    contract_id: str | None, contract_number: str | None, field: str
) -> None:
    with pytest.raises(ContractSelectionError) as exc_info:
        _select_contract(
            contract_infos(("A", "1")),
            contract_id=contract_id,
            contract_number=contract_number,
        )

    assert str(exc_info.value) == f"Договор по {field} недоступен или выбран неоднозначно"


def test_both_selectors_error_explains_the_conflict() -> None:
    with pytest.raises(ContractSelectionError) as exc_info:
        _select_contract(contract_infos(("A", "1")), contract_id="A", contract_number="1")

    assert str(exc_info.value) == "Укажите только один параметр: contract_id или contract_number"


def test_several_contracts_require_selection_by_default() -> None:
    contracts = contract_infos(("A", "1"), ("B", "2"))

    with pytest.raises(ContractSelectionError) as exc_info:
        _select_contract(contracts, contract_id=None, contract_number=None)

    assert str(exc_info.value) == (
        "Доступно несколько договоров; укажите contract_id или contract_number явно"
    )
    assert (
        _select_contract(contracts, contract_id=None, contract_number=None, require_contract=False)
        is None
    )


class RecordingAuthExecutor(StubRequestExecutor):
    def __init__(self, contracts: list[dict[str, Any]]) -> None:
        super().__init__(contracts)
        self.options: list[Any] = []

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
        *,
        budget: OperationBudget | None = None,
    ) -> ResponseT:
        self.options.append(options)
        return await super().execute(operation, options, budget=budget)


def audit_capture(name: str) -> tuple[logging.Logger, list[Any]]:
    # Поля аудита добавляются в LogRecord через extra, поэтому записи типизированы как Any.
    records: list[Any] = []

    class CapturingHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    capture_logger = logging.getLogger(name)
    capture_logger.handlers.clear()
    capture_logger.propagate = False
    capture_logger.setLevel(logging.INFO)
    capture_logger.addHandler(CapturingHandler())
    return capture_logger, records


@pytest.mark.asyncio
async def test_authenticate_forwards_api_version_and_contract_number() -> None:
    session = SessionManager()
    executor = RecordingAuthExecutor([contract("A", "1"), contract("B", "2")])
    auth_logger, records = audit_capture("auth-test-forwarding")
    authenticator = DefaultAuthenticator(executor, session, Credentials(), auth_logger)

    await authenticator.authenticate(api_version="v1", contract_number="2")

    assert executor.options[0].api_version == "v1"
    assert session.contract_id == "B"
    audit = [record for record in records if getattr(record, "request_audit", False)]
    assert {record.api_version for record in audit} == {"v1"}
    assert [record.getMessage() for record in records if not hasattr(record, "request_audit")] == [
        "Договор выбран"
    ]


@pytest.mark.parametrize(
    ("contracts", "message"),
    [
        (
            [contract("A", "1"), contract("B", "2")],
            "Авторизация завершена без договора по умолчанию: передавайте contract_id",
        ),
        ([], "Авторизация завершена; доступных договоров нет"),
    ],
)
@pytest.mark.asyncio
async def test_authenticate_logs_how_the_contract_was_left(
    contracts: list[dict[str, Any]], message: str
) -> None:
    auth_logger, records = audit_capture(f"auth-test-outcome-{len(contracts)}")
    authenticator = DefaultAuthenticator(
        StubRequestExecutor(contracts), SessionManager(), Credentials(), auth_logger
    )

    await authenticator.authenticate(require_contract=False)

    assert [record.getMessage() for record in records if not hasattr(record, "request_audit")] == [
        message
    ]


@pytest.mark.asyncio
async def test_authenticate_audits_cancellation_with_its_budget() -> None:
    class CancellingExecutor(StubRequestExecutor):
        async def execute(
            self,
            operation: OperationSpec[ResponseT],
            options: RequestOptions | None = None,
            *,
            budget: OperationBudget | None = None,
        ) -> ResponseT:
            raise asyncio.CancelledError

    auth_logger, records = audit_capture("auth-test-cancelled")
    authenticator = DefaultAuthenticator(
        CancellingExecutor([]), SessionManager(), Credentials(), auth_logger
    )
    budget = OperationBudget(deadline_at=float("inf"), max_attempts=2)

    with pytest.raises(asyncio.CancelledError):
        await authenticator.authenticate(operation_budget=budget)

    cancelled = [record for record in records if getattr(record, "request_audit", False)][-1]
    assert cancelled.event == "cancelled"
    assert cancelled.exception_type == "CancelledError"
    assert cancelled.attempts_used == 0


class RecordingAuthenticator:
    def __init__(self, session: SessionManager, contracts: list[dict[str, Any]]) -> None:
        self.session = session
        self.executor = StubRequestExecutor(contracts)
        self.calls: list[dict[str, Any]] = []

    async def authenticate(self, **kwargs: Any) -> AuthUserResponse:
        self.calls.append(kwargs)
        response = await self.executor.execute(AUTH_USER)
        self.session.mark_authenticated(response.data.session_id, kwargs.get("contract_id"))
        return response


@pytest.mark.asyncio
async def test_recovery_passes_operation_budget_and_lazy_selection() -> None:
    session = SessionManager()
    session.mark_authenticated("expired-session", "A")
    authenticator = RecordingAuthenticator(session, [contract("A", "1"), contract("B", "2")])
    budget = OperationBudget(deadline_at=60.0, max_attempts=3)

    await AuthenticationCoordinator(session, authenticator).recover(budget)

    assert authenticator.calls == [
        {"contract_id": "A", "operation_budget": budget, "require_contract": False}
    ]
    assert session.available_contracts == ()


@pytest.mark.asyncio
async def test_lazy_login_without_contract_remembers_the_choices() -> None:
    session = SessionManager()
    authenticator = RecordingAuthenticator(session, [contract("A", "1"), contract("B", "2")])

    await AuthenticationCoordinator(session, authenticator).authenticate()

    assert session.contract_id is None
    assert session.available_contracts == (("A", "1"), ("B", "2"))
