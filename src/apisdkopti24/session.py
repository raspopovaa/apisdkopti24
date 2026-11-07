from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum

from .errors import ResponseShapeError
from .execution_budget import acquired_within
from .validation import require_identifier


class SessionState(StrEnum):
    ANONYMOUS = "anonymous"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class SessionSnapshot:
    state: SessionState
    session_id: str | None
    contract_id: str | None
    generation: int


@dataclass(frozen=True, slots=True)
class RequestContext:
    session_id: str | None
    contract_id: str | None
    session_generation: int


class SessionManager:
    def __init__(self) -> None:
        self._state = SessionState.ANONYMOUS
        self._session_id: str | None = None
        self._contract_id: str | None = None
        self._generation = 0
        self._available_contracts: tuple[tuple[str, str], ...] = ()
        # Выбор договора приложением: номер выбора и сам договор. Вход сравнивает номер
        # до и после authUser, чтобы не затереть договор, выбранный во время входа.
        self._contract_selection: tuple[int, str] = (0, "")
        self._auth_lock = asyncio.Lock()
        self._auth_failures = 0
        self._last_auth_failure: Exception | None = None

    @property
    def auth_failures(self) -> int:
        """Сколько раз вход завершился ошибкой: метка для ``failures_seen``."""
        return self._auth_failures

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def contract_id(self) -> str | None:
        return self._contract_id

    @property
    def available_contracts(self) -> tuple[tuple[str, str], ...]:
        """Пары (id, номер) договоров из последней авторизации без выбранного договора."""
        return self._available_contracts

    def remember_contracts(self, contracts: tuple[tuple[str, str], ...]) -> None:
        self._available_contracts = contracts

    def snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            state=self._state,
            session_id=self._session_id,
            contract_id=self._contract_id,
            generation=self._generation,
        )

    def request_context(self, *, contract_id: str | None = None) -> RequestContext:
        snapshot = self.snapshot()
        return RequestContext(
            session_id=snapshot.session_id,
            contract_id=contract_id if contract_id is not None else snapshot.contract_id,
            session_generation=snapshot.generation,
        )

    @property
    def contract_selection(self) -> tuple[int, str]:
        """Номер последнего выбора договора приложением и выбранный договор."""
        return self._contract_selection

    def select_contract(self, contract_id: str) -> None:
        selected = require_identifier(contract_id, "contract_id")
        self._contract_selection = (self._contract_selection[0] + 1, selected)
        self.set_contract(selected)

    def restore(self, *, session_id: str, contract_id: str) -> None:
        self.mark_authenticated(
            require_identifier(session_id, "session_id"),
            require_identifier(contract_id, "contract_id"),
        )

    def set_contract(self, contract_id: str | None) -> None:
        self._contract_id = contract_id
        self._generation += 1

    def mark_authenticated(self, session_id: str, contract_id: str | None = None) -> None:
        self._session_id = session_id
        self._contract_id = contract_id
        self._state = SessionState.AUTHENTICATED
        self._generation += 1

    def invalidate(self) -> None:
        self._session_id = None
        self._contract_id = None
        self._available_contracts = ()
        self._state = SessionState.INVALID
        self._generation += 1

    def expire(self) -> None:
        """Признать сессию недействительной, сохранив выбранный договор.

        Неудачная авторизация (сбой сети, 5xx, timeout) не отменяет выбор договора
        приложением: следующая попытка должна авторизоваться в том же договоре.
        """
        self._session_id = None
        self._state = SessionState.INVALID
        self._generation += 1

    def reset(self) -> None:
        self._session_id = None
        self._contract_id = None
        self._available_contracts = ()
        self._state = SessionState.ANONYMOUS
        self._generation += 1

    async def ensure_authenticated(
        self,
        authenticate: Callable[[], Awaitable[object]],
        *,
        failures_seen: int | None = None,
        wait_limit: float | None = None,
    ) -> str:
        """Вернуть session_id, при необходимости выполнив один вход на всех ожидающих.

        Если вход упал, пока вызов стоял в очереди, вызов получает ту же ошибку и не
        шлёт свой authUser: серия входов приводит к временному бану WAF. Новый вызов
        после неудачи пробует войти заново. ``failures_seen`` задаёт момент начала
        ожидания, если он раньше этого вызова; ``wait_limit`` ограничивает очередь.
        """
        if self._state == SessionState.AUTHENTICATED and self._session_id:
            return self._session_id

        seen = self._auth_failures if failures_seen is None else failures_seen
        async with acquired_within(
            self._auth_lock, wait_limit, "Общий лимит времени операции истёк в очереди входа"
        ):
            if self._state == SessionState.AUTHENTICATED and self._session_id:
                return self._session_id
            if self._auth_failures != seen and self._last_auth_failure is not None:
                raise self._last_auth_failure

            self._state = SessionState.AUTHENTICATING
            try:
                await authenticate()
            except asyncio.CancelledError:
                # Отменённый вход не должен оставлять сессию в AUTHENTICATING.
                self.expire()
                raise
            except Exception as error:
                self._record_auth_failure(error)
                raise

            if not self._session_id:
                missing_session = ResponseShapeError("Авторизация завершилась без session_id")
                self._record_auth_failure(missing_session)
                raise missing_session

            self._state = SessionState.AUTHENTICATED
            self._last_auth_failure = None
            return self._session_id

    def _record_auth_failure(self, error: Exception) -> None:
        self.expire()
        self._auth_failures += 1
        self._last_auth_failure = error
