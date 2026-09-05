from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .env import load_env_file
from .policies import ConcurrencyPolicy, RateLimitPolicy, RetryPolicy


@dataclass(frozen=True, slots=True)
class TimeoutPolicy:
    default: float = 30.0
    auth: float = 30.0
    read_heavy: float = 120.0
    total_default: float = 120.0
    total_auth: float = 60.0
    total_read_heavy: float = 300.0

    def __post_init__(self) -> None:
        if (
            min(
                self.default,
                self.auth,
                self.read_heavy,
                self.total_default,
                self.total_auth,
                self.total_read_heavy,
            )
            <= 0
        ):
            raise ValueError("timeout values must be greater than zero")

    def resolve(self, timeout_class: str) -> float:
        return {
            "default": self.default,
            "auth": self.auth,
            "read_heavy": self.read_heavy,
        }.get(timeout_class, self.default)

    def resolve_total(self, timeout_class: str) -> float:
        return {
            "default": self.total_default,
            "auth": self.total_auth,
            "read_heavy": self.total_read_heavy,
        }.get(timeout_class, self.total_default)


def _load_environment(load_dotenv: bool, env_file: str | Path) -> None:
    if load_dotenv:
        load_env_file(env_file)


@dataclass(frozen=True, slots=True, kw_only=True)
class ConnectionSettings:
    base_url: str
    request_log_file: str = "./api_requests.jsonl"
    logger_file: str = "./api.log"
    log_level: str = "INFO"
    allow_insecure_http: bool = False
    timeouts: TimeoutPolicy = TimeoutPolicy()
    retry_policy: RetryPolicy = RetryPolicy()
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()
    concurrency_policy: ConcurrencyPolicy = ConcurrencyPolicy()

    @classmethod
    def from_env(
        cls,
        *,
        load_dotenv: bool = True,
        env_file: str | Path = ".env",
    ) -> ConnectionSettings:
        _load_environment(load_dotenv, env_file)
        requests_per_second = os.getenv("API_REQUESTS_PER_SECOND")
        max_in_flight = os.getenv("API_MAX_IN_FLIGHT")
        return cls(
            base_url=os.getenv("API_BASE_URL", ""),
            request_log_file=os.getenv("REQUEST_LOG_FILE", "./api_requests.jsonl"),
            logger_file=os.getenv("LOGGER_FILE", "./api.log"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            allow_insecure_http=os.getenv("API_ALLOW_INSECURE_HTTP", "false").lower()
            in {"1", "true", "yes"},
            rate_limit_policy=RateLimitPolicy(
                requests_per_second=(float(requests_per_second) if requests_per_second else None)
            ),
            concurrency_policy=ConcurrencyPolicy(
                max_in_flight=int(max_in_flight) if max_in_flight else 20
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class APISettings(ConnectionSettings):
    api_key: str = field(repr=False)
    login: str | None = field(default=None, repr=False)
    password: str | None = field(default=None, repr=False)

    @classmethod
    def from_env(
        cls,
        *,
        load_dotenv: bool = True,
        env_file: str | Path = ".env",
    ) -> APISettings:
        connection = ConnectionSettings.from_env(
            load_dotenv=load_dotenv,
            env_file=env_file,
        )
        return cls(
            base_url=connection.base_url,
            api_key=os.getenv("API_KEY", ""),
            login=os.getenv("API_LOGIN"),
            password=os.getenv("API_PASSWORD"),
            request_log_file=connection.request_log_file,
            logger_file=connection.logger_file,
            log_level=connection.log_level,
            allow_insecure_http=connection.allow_insecure_http,
            timeouts=connection.timeouts,
            retry_policy=connection.retry_policy,
            rate_limit_policy=connection.rate_limit_policy,
            concurrency_policy=connection.concurrency_policy,
        )

    def connection_settings(self) -> ConnectionSettings:
        return ConnectionSettings(
            base_url=self.base_url,
            request_log_file=self.request_log_file,
            logger_file=self.logger_file,
            log_level=self.log_level,
            allow_insecure_http=self.allow_insecure_http,
            timeouts=self.timeouts,
            retry_policy=self.retry_policy,
            rate_limit_policy=self.rate_limit_policy,
            concurrency_policy=self.concurrency_policy,
        )


__all__ = ["APISettings", "ConnectionSettings", "TimeoutPolicy"]
