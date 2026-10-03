import asyncio

import pytest

from apisdkopti24.errors import ResponseShapeError
from apisdkopti24.session import SessionManager, SessionState


@pytest.mark.asyncio
async def test_session_manager_authenticates_once_for_parallel_waiters():
    manager = SessionManager()
    calls = 0

    async def authenticate():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.01)
        manager.mark_authenticated("SESSION-1", "1-AAA")

    results = await asyncio.gather(
        manager.ensure_authenticated(authenticate),
        manager.ensure_authenticated(authenticate),
        manager.ensure_authenticated(authenticate),
    )

    assert results == ["SESSION-1", "SESSION-1", "SESSION-1"]
    assert calls == 1
    assert manager.state == SessionState.AUTHENTICATED


def test_session_manager_invalidate_resets_current_session():
    manager = SessionManager()
    manager.mark_authenticated("SESSION-1", "1-AAA")

    manager.invalidate()

    assert manager.session_id is None
    assert manager.contract_id is None
    assert manager.state == SessionState.INVALID


def test_session_manager_explicit_lifecycle() -> None:
    manager = SessionManager()
    initial_generation = manager.snapshot().generation

    manager.select_contract(" contract-1 ")
    assert manager.contract_id == "contract-1"

    manager.restore(session_id=" session-1 ", contract_id=" contract-1 ")
    assert manager.state is SessionState.AUTHENTICATED
    assert manager.session_id == "session-1"
    assert manager.request_context().contract_id == "contract-1"

    manager.clear()
    assert manager.state is SessionState.ANONYMOUS
    assert manager.session_id is None
    assert manager.contract_id is None
    assert manager.snapshot().generation == initial_generation + 3


def test_session_manager_expire_keeps_selected_contract():
    manager = SessionManager()
    manager.mark_authenticated("SESSION-1", "1-AAA")
    generation = manager.snapshot().generation

    manager.expire()

    assert manager.session_id is None
    assert manager.contract_id == "1-AAA"
    assert manager.state == SessionState.INVALID
    assert manager.snapshot().generation == generation + 1


@pytest.mark.asyncio
async def test_cancelled_authentication_does_not_stay_authenticating() -> None:
    manager = SessionManager()
    manager.select_contract("1-AAA")
    started = asyncio.Event()

    async def authenticate():
        started.set()
        await asyncio.Event().wait()

    task = asyncio.create_task(manager.ensure_authenticated(authenticate))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert manager.state == SessionState.INVALID
    assert manager.session_id is None
    assert manager.contract_id == "1-AAA"


@pytest.mark.asyncio
async def test_authentication_without_session_id_raises_typed_error() -> None:
    manager = SessionManager()

    async def authenticate():
        return None

    with pytest.raises(ResponseShapeError):
        await manager.ensure_authenticated(authenticate)
    assert manager.state == SessionState.INVALID
