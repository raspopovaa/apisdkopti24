from __future__ import annotations

from dataclasses import dataclass


class OperationTimeoutError(TimeoutError):
    """The total deadline of one SDK business operation has been exhausted."""


class RetryBudgetExceededError(RuntimeError):
    """The total number of HTTP attempts for one operation has been exhausted."""


@dataclass(slots=True)
class OperationBudget:
    deadline_at: float
    max_attempts: int
    attempts_used: int = 0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.attempts_used < 0 or self.attempts_used > self.max_attempts:
            raise ValueError("attempts_used must be between 0 and max_attempts")

    def remaining(self, now: float) -> float:
        remaining = self.deadline_at - now
        if remaining <= 0:
            raise OperationTimeoutError("operation deadline exceeded")
        return remaining

    def claim_attempt(self, now: float) -> float:
        remaining = self.remaining(now)
        if self.attempts_used >= self.max_attempts:
            raise RetryBudgetExceededError("operation retry budget exceeded")
        self.attempts_used += 1
        return remaining

    def ensure_delay_fits(self, now: float, delay: float) -> None:
        if delay < 0:
            raise ValueError("delay must be non-negative")
        if delay >= self.remaining(now):
            raise OperationTimeoutError("operation deadline would be exceeded during backoff")


__all__ = [
    "OperationBudget",
    "OperationTimeoutError",
    "RetryBudgetExceededError",
]
