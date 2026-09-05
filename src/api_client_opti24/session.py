from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum

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
        self._auth_lock = asyncio.Lock()

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def contract_id(self) -> str | None:
        return self._contract_id

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

    def select_contract(self, contract_id: str) -> None:
        self.set_contract(require_identifier(contract_id, "contract_id"))

    def restore(self, *, session_id: str, contract_id: str) -> None:
        self.mark_authenticated(
            require_identifier(session_id, "session_id"),
            require_identifier(contract_id, "contract_id"),
        )

    def clear(self) -> None:
        self.reset()

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
        self._state = SessionState.INVALID
        self._generation += 1

    def reset(self) -> None:
        self._session_id = None
        self._contract_id = None
        self._state = SessionState.ANONYMOUS
        self._generation += 1

    async def ensure_authenticated(
        self,
        authenticate: Callable[[], Awaitable[object]],
    ) -> str:
        if self._state == SessionState.AUTHENTICATED and self._session_id:
            return self._session_id

        async with self._auth_lock:
            if self._state == SessionState.AUTHENTICATED and self._session_id:
                return self._session_id

            self._state = SessionState.AUTHENTICATING
            try:
                await authenticate()
            except Exception:
                self.invalidate()
                raise

            if not self._session_id:
                self.invalidate()
                raise RuntimeError("Authentication completed without session_id")

            self._state = SessionState.AUTHENTICATED
            return self._session_id
