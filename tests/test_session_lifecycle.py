from apisdkopti24.session import SessionManager, SessionState


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
