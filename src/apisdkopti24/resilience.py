from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

from .execution_budget import OperationBudget
from .logger import LoggerLike
from .policies import (
    IDEMPOTENT_HTTP_METHODS,
    SAFE_HTTP_METHODS,
    RetryClass,
    RetryPolicy,
)
from .runtime import Clock

ResultT = TypeVar("ResultT")
Jitter = Callable[[float], float]


class RateLimited:
    """Internal result indicating that the server requested a delayed retry."""


RATE_LIMITED = RateLimited()


class RateLimiter:
    """Coordinate proactive global and authentication request intervals."""

    def __init__(
        self,
        *,
        request_interval: float,
        auth_interval: float,
        clock: Clock,
    ) -> None:
        self._request_interval = request_interval
        self._auth_interval = auth_interval
        self._clock = clock
        self._request_lock = asyncio.Lock()
        self._auth_lock = asyncio.Lock()
        self._last_request: float | None = None
        self._last_auth_request: float | None = None

    async def acquire(
        self,
        retry_class: str | RetryClass,
        budget: OperationBudget | None,
    ) -> None:
        async with self._request_lock:
            self._last_request = await self._wait(
                previous=self._last_request,
                interval=self._request_interval,
                budget=budget,
            )
        if RetryClass.normalize(retry_class) is RetryClass.NETWORK_ONLY:
            async with self._auth_lock:
                self._last_auth_request = await self._wait(
                    previous=self._last_auth_request,
                    interval=self._auth_interval,
                    budget=budget,
                )

    async def _wait(
        self,
        *,
        previous: float | None,
        interval: float,
        budget: OperationBudget | None,
    ) -> float:
        if interval <= 0:
            return self._clock.monotonic()
        now = self._clock.monotonic()
        if previous is not None:
            delay = previous + interval - now
            if delay > 0:
                if budget is not None:
                    budget.ensure_delay_fits(now, delay)
                await self._clock.sleep(delay)
                now = self._clock.monotonic()
        return now


class RetryController:
    """Apply retry policy while preserving one shared operation budget."""

    def __init__(
        self,
        *,
        policy: RetryPolicy,
        limiter: RateLimiter,
        clock: Clock,
        logger: LoggerLike,
        jitter: Jitter | None = None,
    ) -> None:
        self._policy = policy
        self._limiter = limiter
        self._clock = clock
        self._logger = logger
        self._jitter = jitter or (lambda cap: random.uniform(0.0, cap))

    async def execute(
        self,
        *,
        method: str,
        operation_name: str,
        retry_class: str | RetryClass | None,
        idempotent: bool | None,
        budget: OperationBudget | None,
        attempt: Callable[[int, int, float | None], Awaitable[ResultT | RateLimited]],
    ) -> ResultT:
        normalized_method = method.upper()
        resolved_class = retry_class or (
            RetryClass.SAFE.value
            if normalized_method in SAFE_HTTP_METHODS
            else RetryClass.NEVER.value
        )
        resolved_idempotent = (
            normalized_method in IDEMPOTENT_HTTP_METHODS if idempotent is None else idempotent
        )
        network_attempts = self._policy.network_attempt_count(
            resolved_class,
            normalized_method,
            idempotent=resolved_idempotent,
        )
        rate_attempts = self._policy.rate_limit_attempt_count(
            resolved_class,
            normalized_method,
            idempotent=resolved_idempotent,
        )
        network_backoff = self._policy.initial_network_backoff(resolved_class)

        for network_attempt in range(1, network_attempts + 1):
            try:
                for rate_attempt in range(1, rate_attempts + 1):
                    await self._limiter.acquire(resolved_class, budget)
                    remaining = (
                        budget.claim_attempt(self._clock.monotonic())
                        if budget is not None
                        else None
                    )
                    result = await attempt(rate_attempt, rate_attempts, remaining)
                    if not isinstance(result, RateLimited):
                        return result
                    delay = self._jitter(self._policy.rate_limit_backoff_seconds * rate_attempt)
                    if budget is not None:
                        budget.ensure_delay_fits(self._clock.monotonic(), delay)
                    self._logger.warning(
                        "Rate limit method=%s operation=%s attempt=%s/%s backoff=%.2fs",
                        normalized_method,
                        operation_name,
                        rate_attempt,
                        rate_attempts,
                        delay,
                    )
                    await self._clock.sleep(delay)
                raise RuntimeError("Rate limit retry loop exhausted unexpectedly")
            except httpx.RequestError:
                if network_attempt >= network_attempts:
                    raise
                delay = self._jitter(network_backoff)
                if budget is not None:
                    budget.ensure_delay_fits(self._clock.monotonic(), delay)
                self._logger.warning(
                    "Network error method=%s operation=%s attempt=%s/%s backoff=%.2fs",
                    normalized_method,
                    operation_name,
                    network_attempt,
                    network_attempts,
                    delay,
                )
                await self._clock.sleep(delay)
                network_backoff = min(
                    network_backoff * 2,
                    self._policy.network_backoff_max_seconds,
                )
        raise RuntimeError("Network retry loop exhausted unexpectedly")


__all__ = ["RATE_LIMITED", "RateLimited", "RateLimiter", "RetryController"]
