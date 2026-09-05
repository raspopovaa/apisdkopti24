from __future__ import annotations

import asyncio
from typing import Any, Protocol, TypeVar

from .errors import ContractSelectionError
from .logger import LoggerLike
from .modeling import ResponseModel
from .models.auth import AuthUserResponse, ContractInfo
from .operations import Operation, operation
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
        raise ContractSelectionError("Pass either contract_id or contract_number, not both")

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
                f"Requested {requested_field} is unavailable or ambiguous",
                available_contracts=_contract_choices(contracts),
            )
        return matches[0]

    if not contracts:
        return None
    if len(contracts) == 1:
        return contracts[0]
    raise ContractSelectionError(
        "Multiple contracts are available; pass contract_id or contract_number explicitly",
        available_contracts=_contract_choices(contracts),
    )


class Authenticator(Protocol):
    async def authenticate(
        self,
        *,
        api_version: str | None = None,
        contract_id: str | None = None,
        contract_number: str | None = None,
    ) -> AuthUserResponse: ...


class AuthenticationRequestExecutor(Protocol):
    async def execute(
        self,
        operation: Operation[ResponseT],
        *,
        api_version: str | None = None,
        **kwargs: Any,
    ) -> ResponseT: ...


class DefaultAuthenticator:
    def __init__(
        self,
        request_executor: AuthenticationRequestExecutor,
        session_mutator: SessionMutator,
        credentials_provider: CredentialsProvider,
        logger: LoggerLike,
    ) -> None:
        self.__request_executor = request_executor
        self.__session_mutator = session_mutator
        self.__credentials_provider = credentials_provider
        self.__logger = logger

    async def authenticate(
        self,
        *,
        api_version: str | None = None,
        contract_id: str | None = None,
        contract_number: str | None = None,
    ) -> AuthUserResponse:
        if contract_id is not None and contract_number is not None:
            raise ContractSelectionError("Pass either contract_id or contract_number, not both")

        login, password = self.__credentials_provider.get_credentials()
        auth_response = await self.__request_executor.execute(
            AUTH_USER,
            api_version=api_version,
            data={"login": login, "password": hash_password(password)},
        )
        try:
            selected = _select_contract(
                auth_response.data.contracts,
                contract_id=contract_id,
                contract_number=contract_number,
            )
        except ContractSelectionError:
            self.__session_mutator.invalidate()
            raise

        self.__session_mutator.mark_authenticated(
            session_id=auth_response.data.session_id,
            contract_id=selected.id if selected else None,
        )
        if selected:
            self.__logger.info("Contract selected")
        else:
            self.__logger.info("Authentication completed without an available contract")
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

    async def recover(self) -> str:
        failed_session_id = self.__session.session_id
        selected_contract_id = self.__session.contract_id
        async with self.__recovery_lock:
            current_session_id = self.__session.session_id
            if current_session_id is not None and current_session_id != failed_session_id:
                return current_session_id
            self.__session.invalidate()
            return await self.__session.ensure_authenticated(
                lambda: self.__authenticator.authenticate(contract_id=selected_contract_id)
            )
