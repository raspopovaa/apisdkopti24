from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Protocol, TypeVar, cast

from .error_reporting import OperationAudit
from .errors import ContractSelectionError
from .execution_budget import OperationBudget
from .logger import LoggerLike
from .modeling import ResponseModel
from .models.auth import AuthUserResponse, ContractInfo
from .operations import OperationSpec, operation
from .requests import RequestOptions
from .runtime import Clock, SystemClock
from .service_base import CredentialsProvider, SessionMutator
from .session import SessionManager
from .utils import hash_password

ResponseT = TypeVar("ResponseT", bound=ResponseModel)
AUTH_USER = operation("auth_user", AuthUserResponse)


def _contract_choices(contracts: list[ContractInfo]) -> tuple[tuple[str, str], ...]:
    return tuple((item.id, item.number) for item in contracts)


def _select_contract(
    contracts: list[ContractInfo],
    *,
    contract_id: str | None,
    contract_number: str | None,
) -> ContractInfo | None:
    if contract_id is not None and contract_number is not None:
        raise ContractSelectionError(
            "Укажите только один параметр: contract_id или contract_number"
        )

    lookup = contract_id if contract_id is not None else contract_number
    if lookup is not None:
        matches = [
            item
            for item in contracts
            if (item.id if contract_id is not None else item.number) == lookup
        ]
        if len(matches) != 1:
            requested_field = "contract_id" if contract_id is not None else "contract_number"
            raise ContractSelectionError(
                f"Договор по {requested_field} недоступен или выбран неоднозначно",
                available_contracts=_contract_choices(contracts),
            )
        return matches[0]

    if not contracts:
        return None
    if len(contracts) == 1:
        return contracts[0]
    raise ContractSelectionError(
        "Доступно несколько договоров; укажите contract_id или contract_number явно",
        available_contracts=_contract_choices(contracts),
    )


class Authenticator(Protocol):
    async def authenticate(
        self,
        *,
        api_version: str | None = None,
        contract_id: str | None = None,
        contract_number: str | None = None,
        operation_budget: OperationBudget | None = None,
    ) -> AuthUserResponse: ...


class AuthenticationRequestExecutor(Protocol):
    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
        *,
        budget: OperationBudget | None = None,
    ) -> ResponseT: ...


class DefaultAuthenticator:
    def __init__(
        self,
        request_executor: AuthenticationRequestExecutor,
        session_mutator: SessionMutator,
        credentials_provider: CredentialsProvider,
        logger: LoggerLike,
        clock: Clock | None = None,
    ) -> None:
        self.__request_executor = request_executor
        self.__session_mutator = session_mutator
        self.__credentials_provider = credentials_provider
        self.__logger = logger
        self.__clock = clock or SystemClock()

    def __create_budget(self) -> OperationBudget:
        create_budget = getattr(self.__request_executor, "create_budget", None)
        if callable(create_budget):
            factory = cast(Callable[[OperationSpec[object]], OperationBudget], create_budget)
            return factory(AUTH_USER)
        return OperationBudget(
            deadline_at=self.__clock.monotonic() + 60.0,
            max_attempts=1,
        )

    async def authenticate(
        self,
        *,
        api_version: str | None = None,
        contract_id: str | None = None,
        contract_number: str | None = None,
        operation_budget: OperationBudget | None = None,
    ) -> AuthUserResponse:
        budget = operation_budget or self.__create_budget()
        audit = OperationAudit(
            operation=AUTH_USER,
            logger=self.__logger,
            clock=self.__clock,
            api_version=api_version,
        )
        try:
            audit.start()
            if contract_id is not None and contract_number is not None:
                raise ContractSelectionError(
                    "Укажите только один параметр: contract_id или contract_number"
                )

            login, password = self.__credentials_provider.get_credentials()
            auth_response = await self.__request_executor.execute(
                AUTH_USER,
                options=RequestOptions(
                    api_version=api_version,
                    form={"login": login, "password": hash_password(password)},
                ),
                budget=budget,
            )
            selected = _select_contract(
                auth_response.data.contracts,
                contract_id=contract_id,
                contract_number=contract_number,
            )
            self.__session_mutator.mark_authenticated(
                session_id=auth_response.data.session_id,
                contract_id=selected.id if selected else None,
            )
        except asyncio.CancelledError as error:
            audit.cancelled(error, budget)
            raise
        except ContractSelectionError as error:
            self.__session_mutator.invalidate()
            audit.failed(error, budget)
            raise
        except Exception as error:
            audit.failed(error, budget)
            raise
        audit.completed(budget)
        if selected:
            self.__logger.info("Договор выбран")
        else:
            self.__logger.info("Авторизация завершена; доступных договоров нет")
        return auth_response


class AuthenticationCoordinator:
    def __init__(
        self,
        session: SessionManager,
        authenticator: Authenticator,
    ) -> None:
        self.__session = session
        self.__authenticator = authenticator
        self.__recovery_lock = asyncio.Lock()

    async def authenticate(self) -> AuthUserResponse:
        return await self.__authenticator.authenticate(
            contract_id=self.__session.contract_id,
        )

    async def ensure_authenticated(self) -> str:
        return await self.__session.ensure_authenticated(self.authenticate)

    async def recover(self, budget: OperationBudget) -> str:
        failed_session_id = self.__session.session_id
        selected_contract_id = self.__session.contract_id
        async with self.__recovery_lock:
            current_session_id = self.__session.session_id
            if current_session_id is not None and current_session_id != failed_session_id:
                return current_session_id
            self.__session.invalidate()
            return await self.__session.ensure_authenticated(
                lambda: self.__authenticator.authenticate(
                    contract_id=selected_contract_id,
                    operation_budget=budget,
                )
            )
