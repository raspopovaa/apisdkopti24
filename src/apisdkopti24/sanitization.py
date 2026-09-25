"""Value redaction shared by diagnostics; never a substitute for safe message catalogs."""

import re
from typing import Any

REDACTED = "***"
SENSITIVE_LOG_KEYS = {
    "api_key",
    "pin",
    "new_pin",
    "device_id",
    "security",
    "payment_payload",
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
    r"\b(pin|new[_-]?pin|device[_-]?id|security|payment[_-]?payload|api[_-]?key|authorization|password|session[_-]?id|token|secret|"
    r"access[_-]?token|refresh[_-]?token|code|mobile(?:_phone)?|phone|email|login|uuid|"
    r"(?:card|client|contract|group|invite|job|office|poi|report|template|transaction|user)?[_-]?id)\b",
    flags=re.IGNORECASE,
)
_KEY_VALUE_RE = re.compile(
    r"(?P<prefix>(?P<key>pin|new[_-]?pin|device[_-]?id|security|payment[_-]?payload|api[_-]?key|authorization|password|session[_-]?id|token|secret|"
    r"access[_-]?token|refresh[_-]?token|code|mobile(?:_phone)?|phone|email|login|uuid|"
    r"(?:card|client|contract|group|invite|job|office|poi|report|template|transaction|user)?[_-]?id)"
    r"['\"]?\s*[:=]\s*['\"]?)(?P<value>[^,'\"}\]\s]+)",
    flags=re.IGNORECASE,
)


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
    if isinstance(value, BaseException):
        return "[exception details omitted]"

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
