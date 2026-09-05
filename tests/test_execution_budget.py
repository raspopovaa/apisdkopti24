import pytest

from api_client_opti24 import (
    OperationBudget,
    OperationTimeoutError,
    RetryBudgetExceededError,
)


def test_operation_budget_reports_remaining_time_and_claims_attempts() -> None:
    budget = OperationBudget(deadline_at=10.0, max_attempts=2)

    assert budget.remaining(4.0) == 6.0
    assert budget.claim_attempt(5.0) == 5.0
    assert budget.attempts_used == 1


def test_operation_budget_rejects_invalid_initial_state() -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        OperationBudget(deadline_at=10.0, max_attempts=0)
    with pytest.raises(ValueError, match="attempts_used"):
        OperationBudget(deadline_at=10.0, max_attempts=1, attempts_used=2)


def test_operation_budget_enforces_attempt_limit() -> None:
    budget = OperationBudget(deadline_at=10.0, max_attempts=1)

    budget.claim_attempt(1.0)

    with pytest.raises(RetryBudgetExceededError, match="retry budget"):
        budget.claim_attempt(2.0)


def test_operation_budget_enforces_deadline() -> None:
    budget = OperationBudget(deadline_at=10.0, max_attempts=1)

    with pytest.raises(OperationTimeoutError, match="deadline exceeded"):
        budget.remaining(10.0)


def test_operation_budget_rejects_backoff_that_exhausts_deadline() -> None:
    budget = OperationBudget(deadline_at=10.0, max_attempts=1)

    budget.ensure_delay_fits(7.0, 2.0)

    with pytest.raises(OperationTimeoutError, match="during backoff"):
        budget.ensure_delay_fits(7.0, 3.0)
    with pytest.raises(ValueError, match="non-negative"):
        budget.ensure_delay_fits(7.0, -1.0)
