from __future__ import annotations

from dataclasses import dataclass


class OperationTimeoutError(TimeoutError):
    """Исчерпан общий лимит времени одной операции SDK."""


class RetryBudgetExceededError(RuntimeError):
    """Исчерпан общий лимит HTTP-попыток одной операции."""


@dataclass(slots=True)
class OperationBudget:
    deadline_at: float
    max_attempts: int
    attempts_used: int = 0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts должен быть не меньше 1")
        if self.attempts_used < 0 or self.attempts_used > self.max_attempts:
            raise ValueError("attempts_used должен быть в диапазоне от 0 до max_attempts")

    def remaining(self, now: float) -> float:
        remaining = self.deadline_at - now
        if remaining <= 0:
            raise OperationTimeoutError("Превышен общий лимит времени операции")
        return remaining

    def claim_attempt(self, now: float) -> float:
        remaining = self.remaining(now)
        if self.attempts_used >= self.max_attempts:
            raise RetryBudgetExceededError("Исчерпан лимит попыток операции")
        self.attempts_used += 1
        return remaining

    def ensure_delay_fits(self, now: float, delay: float) -> None:
        if delay < 0:
            raise ValueError("delay не может быть отрицательным")
        if delay >= self.remaining(now):
            raise OperationTimeoutError(
                "Ожидание перед повтором превысит общий лимит времени операции"
            )


__all__ = [
    "OperationBudget",
    "OperationTimeoutError",
    "RetryBudgetExceededError",
]
