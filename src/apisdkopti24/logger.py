from __future__ import annotations

import json
import logging
from copy import copy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, TypeAlias
from uuid import uuid4

from .errors import SDKConfigurationError
from .sanitization import REDACTED, message_mentions_sensitive_key, sanitize_for_logging, scrub

DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(module)s: %(message)s"
LoggerLike: TypeAlias = logging.Logger


class SanitizingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if args:
            if isinstance(args, dict):
                record.args = sanitize_for_logging(args)
            elif isinstance(record.msg, str) and message_mentions_sensitive_key(record.msg):
                record.args = tuple(
                    REDACTED if isinstance(arg, str) else sanitize_for_logging(arg) for arg in args
                )
            else:
                record.args = tuple(sanitize_for_logging(arg) for arg in args)

        if isinstance(record.msg, str) and not args:
            record.msg = scrub(record.msg)

        return True


class SafeExceptionFormatter(logging.Formatter):
    """Вывести диагностику без значений из трассировки и исходной цепочки исключений."""

    def format(self, record: logging.LogRecord) -> str:
        safe_record = copy(record)
        safe_record.exc_text = None
        safe_record.stack_info = None
        return super().format(safe_record)

    def formatException(
        self,
        ei: (
            tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
        ),
    ) -> str:
        # Не раскрываем значения исключений, пути и строки исходного кода.
        del ei
        return "Подробности исключения скрыты; используйте структурированный аудит SDK"


class RequestAuditFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return bool(getattr(record, "request_audit", False))


class RequestAuditFormatter(logging.Formatter):
    _FIELDS = (
        "event",
        "operation_id",
        "operation",
        "api_version",
        "route_name",
        "http_method",
        "recovered",
        "sdk_error_code",
        "error_source",
        "exception_type",
        "error_message",
        "transient",
        "retry_allowed",
        "retryable",
        "http_status_code",
        "api_status_code",
        "api_error_type",
        "elapsed_ms",
        "attempts_used",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
        }
        payload.update(
            {
                field_name: sanitize_for_logging(getattr(record, field_name))
                for field_name in self._FIELDS
                if hasattr(record, field_name)
            }
        )
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


sanitizing_filter = SanitizingFilter()
logger = logging.getLogger("apisdkopti24")
logger.addFilter(sanitizing_filter)
logger.addHandler(logging.NullHandler())
logger.propagate = False


SHARED_CLIENT_LOGGER_NAME = "apisdkopti24.client"


@dataclass(slots=True)
class ManagedLogger:
    logger: logging.Logger
    handlers: tuple[logging.Handler, ...]
    owns_logger: bool = False
    _closed: bool = False

    def close(self) -> None:
        if self._closed:
            return
        for handler in self.handlers:
            self.logger.removeHandler(handler)
            handler.close()
        if self.owns_logger:
            # logging хранит логгеры в глобальном реестре бессрочно; без удаления
            # каждый клиент с файловым журналом оставлял бы в памяти свой логгер.
            logging.Logger.manager.loggerDict.pop(self.logger.name, None)
        self._closed = True


def ensure_sanitizing_filter(target: logging.Logger) -> None:
    if not any(isinstance(item, SanitizingFilter) for item in target.filters):
        target.addFilter(SanitizingFilter())


def create_client_logger(
    *,
    log_level: str,
    logger_file: str | None = None,
    request_log_file: str | None = None,
) -> ManagedLogger:
    """Создать журнал клиента.

    Без ``logger_file`` и ``request_log_file`` клиент пишет в общий логгер
    ``apisdkopti24.client`` без обработчиков: вывод и уровень настраивает приложение.
    Файлы создаются только по явной настройке.
    """
    if logger_file is None and request_log_file is None:
        shared_logger = logging.getLogger(SHARED_CLIENT_LOGGER_NAME)
        ensure_sanitizing_filter(shared_logger)
        return ManagedLogger(shared_logger, ())
    if (
        logger_file is not None
        and request_log_file is not None
        and Path(logger_file).resolve() == Path(request_log_file).resolve()
    ):
        raise SDKConfigurationError(
            "logger_file и request_log_file должны указывать на разные файлы"
        )

    resolved_level = getattr(logging, log_level.upper(), logging.INFO)
    client_logger = logging.getLogger(f"{SHARED_CLIENT_LOGGER_NAME}.{uuid4().hex}")
    client_logger.handlers.clear()
    client_logger.propagate = False
    client_logger.setLevel(resolved_level)
    ensure_sanitizing_filter(client_logger)

    handlers: list[logging.Handler] = []
    if logger_file is not None:
        application_handler = logging.FileHandler(logger_file, mode="a", encoding="utf-8")
        application_handler.setLevel(resolved_level)
        application_handler.setFormatter(SafeExceptionFormatter(DEFAULT_LOG_FORMAT))
        handlers.append(application_handler)

    if request_log_file is not None:
        request_handler = logging.FileHandler(request_log_file, mode="a", encoding="utf-8")
        request_handler.setLevel(resolved_level)
        request_handler.addFilter(RequestAuditFilter())
        request_handler.setFormatter(RequestAuditFormatter())
        handlers.append(request_handler)

    for handler in handlers:
        client_logger.addHandler(handler)
    return ManagedLogger(client_logger, tuple(handlers), owns_logger=True)


__all__ = [
    "LoggerLike",
    "ManagedLogger",
    "RequestAuditFilter",
    "SanitizingFilter",
    "SafeExceptionFormatter",
    "create_client_logger",
    "ensure_sanitizing_filter",
    "logger",
]
