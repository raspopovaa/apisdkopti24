import hashlib
import json
from typing import Any

from .validation import validate_month_span as validate_month_span


def hash_password(password: str) -> str:
    """SHA-512 хэш пароля в нижнем регистре."""
    return hashlib.sha512(password.encode()).hexdigest().lower()


def to_json_param(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
