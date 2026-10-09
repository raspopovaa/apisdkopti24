"""Поведение RetryController по сценариям: попытки, паузы, итог и списанный бюджет.

Эталон снят с реализации до разбиения execute на шаги; любой рефакторинг должен
сохранить его без изменений.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import httpx
import pytest

from apisdkopti24.execution_budget import OperationBudget
from apisdkopti24.policies import RetryPolicy
from apisdkopti24.resilience import RATE_LIMITED, RateLimiter, RetryController

GOLDEN = Path(__file__).with_name("contracts") / "retry_controller_behaviour.json"
REQUEST = httpx.Request("GET", "https://api.example.test/vip/v2/cards")

# (метод, retry_class, idempotent, billable)
OPERATIONS = {
    "safe_get": ("GET", "safe", True, False),
    "safe_get_billable": ("GET", "safe", True, True),
    "safe_post_not_idempotent": ("POST", "safe", False, False),
    "never_post": ("POST", "never", False, False),
    "network_only_auth": ("POST", "network_only", None, False),
    "default_get_without_class": ("GET", None, None, False),
}
# Исход каждой попытки: ok — ответ, rl — 429/509, connect/read — сетевая ошибка.
SEQUENCES = {
    "ok": ["ok"],
    "rl_then_ok": ["rl", "ok"],
    "rl_forever": ["rl"] * 10,
    "connect_then_ok": ["connect", "ok"],
    "read_then_ok": ["read", "ok"],
    "connect_forever": ["connect"] * 10,
    "connect_rl_ok": ["connect", "rl", "ok"],
    "rl_connect_ok": ["rl", "connect", "ok"],
}
BUDGETS = {"roomy": (1_000.0, 10), "two_attempts": (1_000.0, 2), "tight_deadline": (3.0, 10)}


class _Records(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


class _Clock:
    def __init__(self) -> None:
        self.now_value = 0.0
        self.sleeps: list[float] = []

    def now(self) -> Any:
        raise AssertionError("RetryController не должен читать календарное время")

    def monotonic(self) -> float:
        return self.now_value

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(round(seconds, 6))
        self.now_value += seconds


def _error(kind: str) -> httpx.RequestError:
    if kind == "connect":
        return httpx.ConnectError("refused", request=REQUEST)
    return httpx.ReadTimeout("timeout", request=REQUEST)


async def _run(operation: str, sequence: str, budget_name: str) -> dict[str, Any]:
    method, retry_class, idempotent, billable = OPERATIONS[operation]
    outcomes = list(SEQUENCES[sequence])
    deadline, max_attempts = BUDGETS[budget_name]
    clock = _Clock()
    records = _Records()
    logger = logging.getLogger(f"retry-behaviour.{operation}.{sequence}.{budget_name}")
    logger.handlers[:] = [records]
    logger.propagate = False
    policy = RetryPolicy(
        network_attempts=3,
        rate_limit_attempts=3,
        max_total_attempts=5,
        network_backoff_min_seconds=1.0,
        network_backoff_max_seconds=4.0,
        rate_limit_backoff_seconds=0.5,
        auth_retry_min_interval_seconds=2.0,
    )
    controller = RetryController(
        policy=policy,
        limiter=RateLimiter(request_interval=0.0, auth_interval=0.0, clock=clock),
        clock=clock,
        logger=logger,
        jitter=lambda cap: cap,
    )
    budget = OperationBudget(deadline_at=deadline, max_attempts=max_attempts)
    calls: list[list[int]] = []

    async def attempt(rate_attempt: int, rate_attempts: int, remaining: float | None) -> Any:
        calls.append([rate_attempt, rate_attempts])
        outcome = outcomes.pop(0) if outcomes else "ok"
        if outcome == "ok":
            return "payload"
        if outcome == "rl":
            return RATE_LIMITED if rate_attempt < rate_attempts else "rate-limited-response"
        raise _error(outcome)

    try:
        result: Any = await controller.execute(
            method=method,
            operation_name=operation,
            retry_class=retry_class,
            idempotent=idempotent,
            budget=budget,
            billable=billable,
            attempt=attempt,
        )
        outcome_text = f"result:{result}"
    except Exception as error:  # noqa: BLE001 — фиксируем любой итог сценария
        cause = type(error.__cause__).__name__ if error.__cause__ else None
        outcome_text = f"raise:{type(error).__name__}<-{cause}"
    return {
        "calls": calls,
        "sleeps": clock.sleeps,
        "outcome": outcome_text,
        "attempts_used": budget.attempts_used,
        "log": records.messages,
    }


CASES = [
    (operation, sequence, budget)
    for operation in OPERATIONS
    for sequence in SEQUENCES
    for budget in BUDGETS
]


@pytest.mark.asyncio
@pytest.mark.parametrize(("operation", "sequence", "budget"), CASES)
async def test_retry_controller_matches_recorded_behaviour(operation, sequence, budget) -> None:
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))[f"{operation}/{sequence}/{budget}"]

    assert await _run(operation, sequence, budget) == expected
