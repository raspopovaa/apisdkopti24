from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeAlias
from uuid import uuid4

from .utils import REDACTED, message_mentions_sensitive_key, sanitize_for_logging, scrub

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


class RequestAuditFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return bool(getattr(record, "request_audit", False))


class RequestAuditFormatter(logging.Formatter):
    _FIELDS = (
        "event",
        "operation",
        "api_version",
        "route_name",
        "http_method",
        "recovered",
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
logger = logging.getLogger("api_client_opti24")
logger.addFilter(sanitizing_filter)
logger.addHandler(logging.NullHandler())
logger.propagate = False


@dataclass(slots=True)
class ManagedLogger:
    logger: logging.Logger
    handlers: tuple[logging.Handler, ...]
    _closed: bool = False

    def close(self) -> None:
        if self._closed:
            return
        for handler in self.handlers:
            self.logger.removeHandler(handler)
            handler.close()
        self._closed = True


def ensure_sanitizing_filter(target: logging.Logger) -> None:
    if not any(isinstance(item, SanitizingFilter) for item in target.filters):
        target.addFilter(SanitizingFilter())


def create_client_logger(
    *,
    log_level: str,
    logger_file: str,
    request_log_file: str,
) -> ManagedLogger:
    if Path(logger_file).resolve() == Path(request_log_file).resolve():
        raise ValueError("logger_file and request_log_file must be different files")

    resolved_level = getattr(logging, log_level.upper(), logging.INFO)
    client_logger = logging.getLogger(f"api_client_opti24.client.{uuid4().hex}")
    client_logger.handlers.clear()
    client_logger.propagate = False
    client_logger.setLevel(resolved_level)
    ensure_sanitizing_filter(client_logger)

    application_handler = logging.FileHandler(logger_file, mode="a", encoding="utf-8")
    application_handler.setLevel(resolved_level)
    application_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))

    request_handler = logging.FileHandler(request_log_file, mode="a", encoding="utf-8")
    request_handler.setLevel(resolved_level)
    request_handler.addFilter(RequestAuditFilter())
    request_handler.setFormatter(RequestAuditFormatter())

    client_logger.addHandler(application_handler)
    client_logger.addHandler(request_handler)
    return ManagedLogger(client_logger, (application_handler, request_handler))


__all__ = [
    "LoggerLike",
    "ManagedLogger",
    "RequestAuditFilter",
    "SanitizingFilter",
    "create_client_logger",
    "ensure_sanitizing_filter",
    "logger",
]
