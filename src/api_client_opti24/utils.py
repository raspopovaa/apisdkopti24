import calendar
import hashlib
import json
import re
from datetime import date, datetime
from typing import Any

from .errors import APIError

REDACTED = "***"
SENSITIVE_LOG_KEYS = {
    "api_key",
    "authorization",
    "password",
    "session_id",
    "token",
    "secret",
    "access_token",
    "refresh_token",
    "code",
    "mobile",
    "mobile_phone",
    "phone",
    "email",
    "login",
    "id",
    "uuid",
    "card_id",
    "client_id",
    "contract_id",
    "group_id",
    "invite_id",
    "job_id",
    "office_id",
    "poi_id",
    "report_id",
    "template_id",
    "transaction_id",
    "user_id",
}

_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
_PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\-\s()]{8,}\d)(?!\d)")
_SENSITIVE_KEY_RE = re.compile(
    r"\b(api[_-]?key|authorization|password|session[_-]?id|token|secret|"
    r"access[_-]?token|refresh[_-]?token|code|mobile(?:_phone)?|phone|email|login|uuid|"
    r"(?:card|client|contract|group|invite|job|office|poi|report|template|transaction|user)?[_-]?id)\b",
    flags=re.IGNORECASE,
)
_KEY_VALUE_RE = re.compile(
    r"(?P<prefix>(?P<key>api[_-]?key|authorization|password|session[_-]?id|token|secret|"
    r"access[_-]?token|refresh[_-]?token|code|mobile(?:_phone)?|phone|email|login|uuid|"
    r"(?:card|client|contract|group|invite|job|office|poi|report|template|transaction|user)?[_-]?id)"
    r"['\"]?\s*[:=]\s*['\"]?)(?P<value>[^,'\"}\]\s]+)",
    flags=re.IGNORECASE,
)


def hash_password(password: str) -> str:
    """SHA-512 хэш пароля в нижнем регистре."""
    return hashlib.sha512(password.encode()).hexdigest().lower()


def scrub(text: str) -> str:
    redacted = _KEY_VALUE_RE.sub(lambda match: f"{match.group('prefix')}{REDACTED}", text)
    redacted = _EMAIL_RE.sub(REDACTED, redacted)
    return _PHONE_RE.sub(REDACTED, redacted)


def is_sensitive_log_key(key: str) -> bool:
    normalized = key.strip().lower().replace("-", "_")
    return normalized in SENSITIVE_LOG_KEYS


def message_mentions_sensitive_key(text: str) -> bool:
    return bool(_SENSITIVE_KEY_RE.search(text))


def sanitize_for_logging(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[Any, Any] = {}
        for key, item in value.items():
            key_str = str(key)
            sanitized[key] = (
                REDACTED if is_sensitive_log_key(key_str) else sanitize_for_logging(item)
            )
        return sanitized

    if isinstance(value, (list, tuple, set)):
        sanitized_items = [sanitize_for_logging(item) for item in value]
        if isinstance(value, tuple):
            return tuple(sanitized_items)
        if isinstance(value, set):
            return set(sanitized_items)
        return sanitized_items

    if isinstance(value, str):
        return scrub(value)

    return value


def to_json_param(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def validate_month_span(date_from: str, date_to: str) -> None:
    """Проверка, что разница между датами не больше месяца."""
    d_from = date.fromisoformat(date_from)
    d_to = date.fromisoformat(date_to)
    if d_to < d_from:
        raise APIError(3, "date_to не может быть меньше date_from")

    days_in_month = calendar.monthrange(d_from.year, d_from.month)[1]
    if (d_to - d_from).days > days_in_month:
        raise APIError(3, f"Разница между датами превышает {days_in_month} дней")


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
