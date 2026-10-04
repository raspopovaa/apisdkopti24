import calendar
import hashlib
import json
from datetime import date
from typing import Any

from .errors import RequestValidationError

# Сохраняем существующие пути импорта утилит.
from .sanitization import REDACTED as REDACTED
from .sanitization import SENSITIVE_LOG_KEYS as SENSITIVE_LOG_KEYS
from .sanitization import is_sensitive_log_key as is_sensitive_log_key
from .sanitization import message_mentions_sensitive_key as message_mentions_sensitive_key
from .sanitization import sanitize_for_logging as sanitize_for_logging
from .sanitization import scrub as scrub


def hash_password(password: str) -> str:
    """SHA-512 хэш пароля в нижнем регистре."""
    return hashlib.sha512(password.encode()).hexdigest().lower()


def to_json_param(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def validate_month_span(date_from: str, date_to: str) -> None:
    """Проверить порядок дат и предел интервала в днях.

    Предел равен числу дней в месяце date_from; конец интервала может
    находиться в следующем календарном месяце.
    """
    try:
        d_from = date.fromisoformat(date_from)
        d_to = date.fromisoformat(date_to)
    except ValueError as exc:
        raise RequestValidationError("Даты должны иметь формат ISO YYYY-MM-DD") from exc
    if d_to < d_from:
        raise RequestValidationError("date_to не может быть меньше date_from")

    days_in_month = calendar.monthrange(d_from.year, d_from.month)[1]
    if (d_to - d_from).days > days_in_month:
        raise RequestValidationError(f"Разница между датами превышает {days_in_month} дней")
