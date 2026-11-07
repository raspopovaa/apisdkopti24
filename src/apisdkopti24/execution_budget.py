from __future__ import annotations

import asyncio
import math
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from .errors import Opti24Error


class OperationTimeoutError(Opti24Error, TimeoutError):
    """Исчерпан общий лимит времени одной операции SDK."""


class RetryBudgetExceededError(Opti24Error, RuntimeError):
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


@asynccontextmanager
async def acquired_within(
    primitive: asyncio.Lock | asyncio.Semaphore,
    limit: float | None,
    expired_message: str,
) -> AsyncIterator[None]:
    """Занять блокировку или слот, ожидая не дольше ``limit`` секунд."""
    try:
        if limit is None or not math.isfinite(limit):
            await primitive.acquire()
        else:
            async with asyncio.timeout(limit):
                await primitive.acquire()
    except TimeoutError as error:
        raise OperationTimeoutError(expired_message) from error
    try:
        yield
    finally:
        primitive.release()


__all__ = [
    "acquired_within",
    "OperationBudget",
    "OperationTimeoutError",
    "RetryBudgetExceededError",
]
