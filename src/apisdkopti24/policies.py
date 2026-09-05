from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

SAFE_HTTP_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
IDEMPOTENT_HTTP_METHODS = SAFE_HTTP_METHODS | {"PUT", "DELETE"}


class RetryClass(StrEnum):
    NEVER = "never"
    SAFE = "safe"
    NETWORK_ONLY = "network_only"

    @classmethod
    def normalize(cls, value: str | RetryClass) -> RetryClass:
        if isinstance(value, cls):
            return value
        return cls(value)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    network_attempts: int = 5
    rate_limit_attempts: int = 3
    max_total_attempts: int = 5
    network_backoff_min_seconds: float = 2.0
    network_backoff_max_seconds: float = 60.0
    rate_limit_backoff_seconds: float = 0.5
    auth_retry_min_interval_seconds: float = 5.0

    def __post_init__(self) -> None:
        if (
            min(
                self.network_attempts,
                self.rate_limit_attempts,
                self.max_total_attempts,
            )
            < 1
        ):
            raise ValueError("retry attempts must be at least 1")
        if (
            min(
                self.network_backoff_min_seconds,
                self.network_backoff_max_seconds,
                self.rate_limit_backoff_seconds,
                self.auth_retry_min_interval_seconds,
            )
            < 0
        ):
            raise ValueError("retry backoff values must be non-negative")

    def network_attempt_count(
        self,
        retry_class: str | RetryClass,
        http_method: str,
        *,
        idempotent: bool | None = None,
    ) -> int:
        normalized = RetryClass.normalize(retry_class)
        resolved_idempotent = (
            http_method.upper() in IDEMPOTENT_HTTP_METHODS if idempotent is None else idempotent
        )
        if normalized is RetryClass.NETWORK_ONLY:
            return min(self.network_attempts, self.max_total_attempts)
        if normalized is RetryClass.SAFE and resolved_idempotent:
            return min(self.network_attempts, self.max_total_attempts)
        return 1

    def rate_limit_attempt_count(
        self,
        retry_class: str | RetryClass,
        http_method: str,
        *,
        idempotent: bool | None = None,
    ) -> int:
        normalized = RetryClass.normalize(retry_class)
        resolved_idempotent = (
            http_method.upper() in IDEMPOTENT_HTTP_METHODS if idempotent is None else idempotent
        )
        if normalized is RetryClass.SAFE and resolved_idempotent:
            return min(self.rate_limit_attempts, self.max_total_attempts)
        return 1

    def initial_network_backoff(self, retry_class: str | RetryClass) -> float:
        if RetryClass.normalize(retry_class) is RetryClass.NETWORK_ONLY:
            return max(
                self.network_backoff_min_seconds,
                self.auth_retry_min_interval_seconds,
            )
        return self.network_backoff_min_seconds


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    requests_per_second: float | None = None

    def __post_init__(self) -> None:
        if self.requests_per_second is not None and self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be greater than zero")

    @property
    def minimum_interval_seconds(self) -> float:
        if self.requests_per_second is None:
            return 0.0
        return 1.0 / self.requests_per_second


@dataclass(frozen=True, slots=True)
class ConcurrencyPolicy:
    max_in_flight: int = 20

    def __post_init__(self) -> None:
        if self.max_in_flight < 1:
            raise ValueError("max_in_flight must be at least 1")
