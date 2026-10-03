from __future__ import annotations

import logging
import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path

from .env import load_env_file
from .errors import SDKConfigurationError
from .policies import ConcurrencyPolicy, RateLimitPolicy, RetryPolicy


@dataclass(frozen=True, slots=True)
class TimeoutPolicy:
    default: float = 30.0
    auth: float = 30.0
    read_heavy: float = 120.0
    # remove_card_group: сервер иногда отвечает дольше 120 секунд, хотя группа удаляется.
    slow_mutation: float = 300.0
    total_default: float = 120.0
    total_auth: float = 60.0
    total_read_heavy: float = 300.0
    total_slow_mutation: float = 360.0
    connect: float = 10.0

    def __post_init__(self) -> None:
        if (
            min(
                self.default,
                self.auth,
                self.read_heavy,
                self.slow_mutation,
                self.total_default,
                self.total_auth,
                self.total_read_heavy,
                self.total_slow_mutation,
                self.connect,
            )
            <= 0
        ):
            raise SDKConfigurationError("Значения таймаутов должны быть больше нуля")

    def resolve(self, timeout_class: str) -> float:
        return {
            "default": self.default,
            "auth": self.auth,
            "read_heavy": self.read_heavy,
            "slow_mutation": self.slow_mutation,
        }.get(timeout_class, self.default)

    def resolve_total(self, timeout_class: str) -> float:
        return {
            "default": self.total_default,
            "auth": self.total_auth,
            "read_heavy": self.total_read_heavy,
            "slow_mutation": self.total_slow_mutation,
        }.get(timeout_class, self.total_default)


def _load_environment(load_dotenv: bool, env_file: str | Path) -> None:
    if load_dotenv:
        load_env_file(env_file)


def _env_value(name: str) -> str | None:
    """Вернуть значение переменной; пустая строка означает «не задано»."""
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return None
    return raw_value.strip()


_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})


def _bool_from_env(name: str, default: bool) -> bool:
    raw_value = _env_value(name)
    if raw_value is None:
        return default
    normalized = raw_value.lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise SDKConfigurationError(f"{name} должен быть true или false")


def _positive_int_from_env(name: str, default: int) -> int:
    raw_value = _env_value(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise SDKConfigurationError(f"{name} должен содержать целое число") from exc
    if value <= 0:
        raise SDKConfigurationError(f"{name} должен быть больше нуля")
    return value


def _positive_float_from_env(name: str) -> float | None:
    raw_value = _env_value(name)
    if raw_value is None:
        return None
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise SDKConfigurationError(f"{name} должен содержать число") from exc
    if value <= 0:
        raise SDKConfigurationError(f"{name} должен быть больше нуля")
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class ConnectionSettings:
    base_url: str
    request_log_file: str | None = None
    logger_file: str | None = None
    log_level: str = "INFO"
    allow_insecure_http: bool = False
    max_json_response_bytes: int = 16 * 1024 * 1024
    max_in_memory_response_bytes: int = 64 * 1024 * 1024
    max_error_response_bytes: int = 1024 * 1024
    timeouts: TimeoutPolicy = TimeoutPolicy()
    retry_policy: RetryPolicy = RetryPolicy()
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()
    concurrency_policy: ConcurrencyPolicy = ConcurrencyPolicy()

    def __post_init__(self) -> None:
        if not isinstance(logging.getLevelName(self.log_level.upper()), int):
            raise SDKConfigurationError(
                "log_level должен быть уровнем logging: DEBUG, INFO, WARNING, ERROR или CRITICAL"
            )

    @classmethod
    def from_env(
        cls,
        *,
        load_dotenv: bool = True,
        env_file: str | Path = ".env",
    ) -> ConnectionSettings:
        _load_environment(load_dotenv, env_file)
        return cls(
            base_url=os.getenv("API_BASE_URL", ""),
            request_log_file=_env_value("REQUEST_LOG_FILE"),
            logger_file=_env_value("LOGGER_FILE"),
            log_level=_env_value("LOG_LEVEL") or "INFO",
            allow_insecure_http=_bool_from_env("API_ALLOW_INSECURE_HTTP", False),
            max_json_response_bytes=_positive_int_from_env(
                "API_MAX_JSON_RESPONSE_BYTES", 16 * 1024 * 1024
            ),
            max_in_memory_response_bytes=_positive_int_from_env(
                "API_MAX_IN_MEMORY_RESPONSE_BYTES", 64 * 1024 * 1024
            ),
            max_error_response_bytes=_positive_int_from_env(
                "API_MAX_ERROR_RESPONSE_BYTES", 1024 * 1024
            ),
            rate_limit_policy=RateLimitPolicy(
                requests_per_second=_positive_float_from_env("API_REQUESTS_PER_SECOND")
            ),
            concurrency_policy=ConcurrencyPolicy(
                max_in_flight=_positive_int_from_env("API_MAX_IN_FLIGHT", 20)
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class APISettings(ConnectionSettings):
    """Устарело: настройки вместе с учётными данными.

    Используйте ``ConnectionSettings`` и отдельные ``credentials_provider`` и
    ``api_key_provider``: так учётные данные не попадают в объект настроек.
    """

    api_key: str = field(repr=False)
    login: str | None = field(default=None, repr=False)
    password: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        warnings.warn(
            "APISettings устарел: передайте ConnectionSettings и credentials_provider "
            "(или api_key_provider) в APIClient",
            DeprecationWarning,
            stacklevel=3,
        )
        ConnectionSettings.__post_init__(self)

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
            max_json_response_bytes=connection.max_json_response_bytes,
            max_in_memory_response_bytes=connection.max_in_memory_response_bytes,
            max_error_response_bytes=connection.max_error_response_bytes,
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
            max_json_response_bytes=self.max_json_response_bytes,
            max_in_memory_response_bytes=self.max_in_memory_response_bytes,
            max_error_response_bytes=self.max_error_response_bytes,
            timeouts=self.timeouts,
            retry_policy=self.retry_policy,
            rate_limit_policy=self.rate_limit_policy,
            concurrency_policy=self.concurrency_policy,
        )


__all__ = ["APISettings", "ConnectionSettings", "TimeoutPolicy"]
