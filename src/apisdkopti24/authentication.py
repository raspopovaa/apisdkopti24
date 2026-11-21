"""Вход (``authUser``), выбор договора и восстановление сессии (перелогин).

:class:`DefaultAuthenticator` выполняет один вход и выбирает договор.
:class:`AuthenticationCoordinator` решает, когда входить: лениво перед первым
запросом и повторно, когда сервер отклонил сессию.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar

from .error_reporting import OperationAudit
from .errors import ContractSelectionError, ServerError
from .execution_budget import OperationBudget, OperationTimeoutError, acquired_within
from .logger import LoggerLike
from .modeling import ResponseModel
from .models.auth import AuthUserResponse, ContractInfo
from .operations import OperationSpec, operation
from .protocols import CredentialsProvider, SessionMutator
from .requests import RequestOptions
from .runtime import Clock, SystemClock
from .session import SessionManager
from .utils import hash_password

ResponseT = TypeVar("ResponseT", bound=ResponseModel)
AUTH_USER = operation("auth_user", AuthUserResponse)


def _contract_choices(contracts: list[ContractInfo]) -> tuple[tuple[str, str], ...]:
    """Свести договоры логина к парам ``(id, номер)`` для ошибки и подсказки выбора.

    :param contracts: Договоры из ответа ``authUser``.
    :return: Кортеж пар ``(id, номер)``.
    """
    return tuple((item.id, item.number) for item in contracts)


def _select_contract(
    contracts: list[ContractInfo],
    *,
    contract_id: str | None,
    contract_number: str | None,
    require_contract: bool = True,
) -> ContractInfo | None:
    """Выбрать договор сессии из договоров логина.

    Явный ``contract_id`` или ``contract_number`` должен совпасть ровно с одним
    договором. Без них: единственный договор выбирается сам; нет договоров —
    ``None``; несколько — ``None`` при ``require_contract=False`` (ленивый вход),
    иначе ошибка.

    :param contracts: Договоры из ответа ``authUser``.
    :param contract_id: Нужный договор по идентификатору.
    :param contract_number: Нужный договор по номеру.
    :param require_contract: Требовать однозначный выбор, когда договоров несколько.
    :return: Выбранный договор или ``None``.
    :raises ContractSelectionError: Заданы оба параметра, нужный договор не найден или
        найден не один, либо договоров несколько при ``require_contract=True``. В ошибке
        список доступных договоров.
    """
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
    if not require_contract:
        return None
    raise ContractSelectionError(
        "Доступно несколько договоров; укажите contract_id или contract_number явно",
        available_contracts=_contract_choices(contracts),
    )


# authUser изредка отвечает 500, а следующая попытка проходит. Вход ничего
# не меняет на сервере, поэтому после ответа 5xx SDK повторяет его один раз. Паузу задаёт
# ограничитель частоты входа (RetryPolicy.auth_retry_min_interval_seconds).


class Authenticator(Protocol):
    """Интерфейс входа: выполнить ``authUser`` и записать сессию."""

    async def authenticate(
        self,
        *,
        contract_id: str | None = None,
        contract_number: str | None = None,
        operation_budget: OperationBudget | None = None,
        require_contract: bool = True,
    ) -> AuthUserResponse:
        """Войти и выбрать договор; см. :meth:`DefaultAuthenticator.authenticate`."""
        ...


class AuthenticationRequestExecutor(Protocol):
    """Часть исполнителя, нужная для входа: бюджет операции и отправка запроса."""

    def create_budget(self, operation: OperationSpec[object]) -> OperationBudget:
        """Создать бюджет времени и попыток для операции входа."""
        ...

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
        *,
        budget: OperationBudget | None = None,
    ) -> ResponseT:
        """Отправить запрос и вернуть проверенную модель ответа."""
        ...


class DefaultAuthenticator:
    """Вход по логину и паролю с аудитом и выбором договора.

    Пароль уходит на сервер хешем (``hash_password``), не открытым текстом.

    :param request_executor: Исполнитель для ``authUser``.
    :param session_mutator: Куда записать ``session_id`` и договор после входа.
    :param credentials_provider: Источник логина и пароля; читается при каждом входе.
    :param logger: Журнал SDK.
    :param clock: Часы для длительности в аудите; по умолчанию системные.
    """

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

    async def authenticate(
        self,
        *,
        contract_id: str | None = None,
        contract_number: str | None = None,
        operation_budget: OperationBudget | None = None,
        require_contract: bool = True,
    ) -> AuthUserResponse:
        """Авторизоваться и выбрать договор.

        ``require_contract=False`` нужен для ленивой авторизации: если договоров несколько
        и ни один не выбран, сессия открывается без договора по умолчанию; договор
        тогда передаётся в каждый метод явно.
        """
        budget = operation_budget or self.__request_executor.create_budget(AUTH_USER)
        audit = OperationAudit(
            operation=AUTH_USER,
            logger=self.__logger,
            clock=self.__clock,
        )
        try:
            audit.start()
            if contract_id is not None and contract_number is not None:
                raise ContractSelectionError(
                    "Укажите только один параметр: contract_id или contract_number"
                )

            login, password = self.__credentials_provider.get_credentials()
            options = RequestOptions(
                form={"login": login, "password": hash_password(password)},
            )
            auth_response = await self.__retry_after_server_error(
                lambda: self.__request_executor.execute(AUTH_USER, options=options, budget=budget)
            )
            selected = _select_contract(
                auth_response.data.contracts,
                contract_id=contract_id,
                contract_number=contract_number,
                require_contract=require_contract,
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
        elif auth_response.data.contracts:
            self.__logger.info(
                "Авторизация завершена без договора по умолчанию: передавайте contract_id"
            )
        else:
            self.__logger.info("Авторизация завершена; доступных договоров нет")
        return auth_response

    async def __retry_after_server_error(
        self, send: Callable[[], Awaitable[AuthUserResponse]]
    ) -> AuthUserResponse:
        """Отправить authUser; после временного ответа 5xx повторить один раз."""
        try:
            return await send()
        except ServerError as error:
            if not error.context.transient:
                raise
            first_error = error
        self.__logger.warning(
            "Сервер ответил %s на вход; SDK повторит вход один раз", first_error.status_code
        )
        try:
            return await send()
        except OperationTimeoutError:
            # Срок входа истёк на повторе: важнее исходный ответ сервера.
            raise first_error from None


class AuthenticationCoordinator:
    """Когда входить: лениво до первого запроса и заново после отказа сервера в сессии.

    Все параллельные вызовы ждут один вход (очередь в
    :meth:`SessionManager.ensure_authenticated`), чтобы серия ``authUser`` не
    привела к временной блокировке WAF.

    :param session: Состояние сессии клиента.
    :param authenticator: Кто выполняет сам вход.
    :param clock: Часы для остатка бюджета операции.
    :param auth_wait_limit: Сколько секунд ждать очередь входа, когда бюджета ещё нет
        (вход нужен сервису до начала операции, чтобы узнать договор).
    """

    def __init__(
        self,
        session: SessionManager,
        authenticator: Authenticator,
        clock: Clock | None = None,
        auth_wait_limit: float | None = None,
    ) -> None:
        self.__session = session
        self.__authenticator = authenticator
        self.__clock = clock or SystemClock()
        self.__auth_wait_limit = auth_wait_limit
        self.__recovery_lock = asyncio.Lock()

    async def authenticate(self) -> AuthUserResponse:
        """Войти лениво в договоре текущей сессии (без обязательного выбора договора).

        :return: Ответ ``authUser``.
        """
        return await self.__authenticate_lazily(self.__session.contract_id)

    async def __authenticate_lazily(
        self,
        contract_id: str | None,
        budget: OperationBudget | None = None,
    ) -> AuthUserResponse:
        """Войти без обязательного выбора договора и обновить сессию.

        Если приложение вызвало ``select_contract()``, пока шёл ``authUser``, выбор
        приложения важнее того, что выбрал вход. Если договор не выбран, запоминает
        договоры логина: их покажет ``ContractSelectionError`` в методе без
        ``contract_id``.

        :param contract_id: Договор, в котором входить, или ``None``.
        :param budget: Бюджет операции, внутри которой идёт вход, или ``None``.
        :return: Ответ ``authUser``.
        """
        # Без выбранного договора ленивая авторизация не требует выбора: метод с явным
        # contract_id работает, а метод без него получит ContractSelectionError со списком.
        selection_before = self.__session.contract_selection
        response = await self.__authenticator.authenticate(
            contract_id=contract_id,
            operation_budget=budget,
            require_contract=False,
        )
        selection_after = self.__session.contract_selection
        if selection_after != selection_before:
            # select_contract() во время authUser: вход выбрал договор по прежнему
            # состоянию, а приложение уже указало другой.
            self.__session.set_contract(selection_after[1])
        self.__session.remember_contracts(
            ()
            if self.__session.contract_id is not None
            else _contract_choices(response.data.contracts)
        )
        return response

    def __wait_limit(self, budget: OperationBudget | None) -> float | None:
        """Сколько можно ждать очередь входа.

        :param budget: Бюджет операции или ``None``.
        :return: Остаток срока операции; без бюджета — ``auth_wait_limit``.
        """
        # Без бюджета вход нужен сервису до начала операции, чтобы узнать договор.
        if budget is None:
            return self.__auth_wait_limit
        return budget.remaining(self.__clock.monotonic())

    async def ensure_authenticated(self, budget: OperationBudget | None = None) -> str:
        """Вернуть ``session_id``, войдя при необходимости.

        Если сессия уже есть, сети нет. Иначе один вход на всех ожидающих.

        :param budget: Бюджет операции; ограничивает ожидание очереди входа.
        :return: Действующий ``session_id``.
        :raises OperationTimeoutError: Срок операции истёк в очереди входа.
        """
        return await self.__session.ensure_authenticated(
            lambda: self.__authenticate_lazily(self.__session.contract_id, budget),
            wait_limit=self.__wait_limit(budget),
        )

    async def recover(self, budget: OperationBudget) -> str:
        """Перелогин после того, как сервер отклонил сессию (401 или ``notAuthenticated``).

        Если, пока вызов ждал блокировку, другая операция уже вошла заново
        (``session_id`` сменился), возвращает новую сессию без второго входа. Иначе
        сбрасывает сессию с сохранением выбранного договора и входит в том же договоре.
        Если вход упал, пока вызов ждал, вызов получает ту же ошибку и свой ``authUser``
        не шлёт.

        :param budget: Бюджет операции; перелогин тратит её срок и попытки.
        :return: Новый ``session_id``.
        :raises OperationTimeoutError: Срок операции истёк в очереди восстановления или входа.
        """
        failed_session_id = self.__session.session_id
        selected_contract_id = self.__session.contract_id
        failures_seen = self.__session.auth_failures
        async with acquired_within(
            self.__recovery_lock,
            self.__wait_limit(budget),
            "Общий лимит времени операции истёк в очереди восстановления сессии",
        ):
            current_session_id = self.__session.session_id
            if current_session_id is not None and current_session_id != failed_session_id:
                return current_session_id
            self.__session.expire()
            return await self.__session.ensure_authenticated(
                lambda: self.__authenticate_lazily(selected_contract_id, budget),
                failures_seen=failures_seen,
                wait_limit=self.__wait_limit(budget),
            )
