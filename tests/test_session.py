import asyncio

import pytest

from api_client_opti24.session import SessionManager, SessionState


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
