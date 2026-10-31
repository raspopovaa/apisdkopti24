"""Ограничитель частоты ждёт по интервалам, но не дольше срока операции."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import pytest

from apisdkopti24.execution_budget import OperationBudget, OperationTimeoutError
from apisdkopti24.policies import RetryPolicy
from apisdkopti24.resilience import RateLimiter, RetryController


class ManualClock:
    def __init__(self) -> None:
        self.now_value = 100.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now_value

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(round(seconds, 6))
        self.now_value += seconds


def limiter(clock: ManualClock) -> RateLimiter:
    return RateLimiter(request_interval=1.0, auth_interval=5.0, clock=clock)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_consecutive_requests_keep_the_interval() -> None:
    clock = ManualClock()
    rate_limiter = limiter(clock)

    for _ in range(3):
        await rate_limiter.acquire("safe", None)

    assert clock.sleeps == [1.0, 1.0]


@pytest.mark.asyncio
async def test_request_interval_that_outlives_the_budget_fails_fast() -> None:
    clock = ManualClock()
    rate_limiter = limiter(clock)
    await rate_limiter.acquire("safe", None)

    with pytest.raises(OperationTimeoutError):
        await rate_limiter.acquire(
            "safe", OperationBudget(deadline_at=clock.now_value + 0.5, max_attempts=1)
        )

    assert clock.sleeps == []


@pytest.mark.asyncio
async def test_auth_interval_that_outlives_the_budget_fails_fast() -> None:
    clock = ManualClock()
    rate_limiter = limiter(clock)
    await rate_limiter.acquire("network_only", None)
    clock.now_value += 1.0

    with pytest.raises(OperationTimeoutError):
        await rate_limiter.acquire(
            "network_only", OperationBudget(deadline_at=clock.now_value + 2.0, max_attempts=1)
        )

    assert clock.sleeps == []


@pytest.mark.asyncio
async def test_auth_queue_wait_is_bounded_by_the_budget() -> None:
    clock = ManualClock()
    rate_limiter = limiter(clock)
    # Другой вход держит очередь авторизации дольше срока операции.
    await rate_limiter._auth_lock.acquire()
    try:
        with pytest.raises(OperationTimeoutError, match="очереди"):
            await rate_limiter.acquire(
                "network_only",
                OperationBudget(deadline_at=clock.now_value + 0.01, max_attempts=1),
            )
    finally:
        rate_limiter._auth_lock.release()


def controller(clock: ManualClock) -> RetryController:
    return RetryController(
        policy=RetryPolicy(),
        limiter=limiter(clock),
        clock=clock,  # type: ignore[arg-type]
        logger=logging.getLogger("rate-limiter-budget"),
        jitter=lambda cap: cap,
    )


async def run_once(
    retry: RetryController,
    budget: OperationBudget | None,
    gate: asyncio.Semaphore | None = None,
) -> list[float | None]:
    remaining_seen: list[float | None] = []

    async def attempt(rate_attempt: int, rate_attempts: int, remaining: float | None) -> Any:
        del rate_attempt, rate_attempts
        remaining_seen.append(remaining)
        return "payload"

    await retry.execute(
        method="GET",
        operation_name="get_cards_v2",
        retry_class="safe",
        idempotent=True,
        budget=budget,
        attempt=attempt,
        concurrency_gate=gate,
    )
    return remaining_seen


@pytest.mark.asyncio
async def test_controller_runs_without_operation_budget() -> None:
    assert await run_once(controller(ManualClock()), None) == [None]


@pytest.mark.asyncio
async def test_controller_applies_the_budget_to_the_rate_limiter() -> None:
    clock = ManualClock()
    retry = controller(clock)
    await run_once(retry, None)

    with pytest.raises(OperationTimeoutError):
        await run_once(retry, OperationBudget(deadline_at=clock.now_value + 0.5, max_attempts=3))

    assert clock.sleeps == []


@pytest.mark.asyncio
async def test_controller_bounds_the_wait_for_a_concurrency_slot() -> None:
    clock = ManualClock()
    gate = asyncio.Semaphore(1)
    await gate.acquire()
    try:
        with pytest.raises(OperationTimeoutError, match="слота"):
            await run_once(
                controller(clock),
                OperationBudget(deadline_at=clock.now_value + 0.01, max_attempts=3),
                gate,
            )
    finally:
        gate.release()
