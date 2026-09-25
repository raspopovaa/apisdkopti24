import calendar
import hashlib
import json
from datetime import date, datetime
from typing import Any

from .errors import RequestValidationError

# Preserve the existing utility imports for callers.
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
    """Проверка, что разница между датами не больше месяца."""
    try:
        d_from = date.fromisoformat(date_from)
        d_to = date.fromisoformat(date_to)
    except ValueError as exc:
        raise RequestValidationError("Dates must use ISO YYYY-MM-DD format") from exc
    if d_to < d_from:
        raise RequestValidationError("date_to не может быть меньше date_from")

    days_in_month = calendar.monthrange(d_from.year, d_from.month)[1]
    if (d_to - d_from).days > days_in_month:
        raise RequestValidationError(f"Разница между датами превышает {days_in_month} дней")


def format_date_russian(date_str: str) -> str:
    # Словарь русских названий месяцев
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    day = date_obj.day
    month = months[date_obj.month]
    year = date_obj.year

    return f"{day} {month} {year} года"


def format_number(number: float | int | None) -> str:
    if number is None:
        return "—"
    try:
        return f"{float(number):,.2f}".replace(",", " ")
    except (ValueError, TypeError):
        return "—"


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))
