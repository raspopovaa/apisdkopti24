"""Общая очистка диагностических значений; не заменяет безопасные каталоги сообщений."""

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
    "card_number",
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
# Ключи в тексте пишут и через дефис, и слитно; «-id» встречается как окончание имени.
_KEY_PATTERN = "|".join(
    [key.replace("_", "[_-]?") for key in sorted(SENSITIVE_LOG_KEYS, key=len, reverse=True)]
    + ["[_-]id"]
)
_SENSITIVE_KEY_RE = re.compile(rf"\b({_KEY_PATTERN})\b", flags=re.IGNORECASE)
_KEY_VALUE_RE = re.compile(
    rf"(?P<prefix>(?P<key>{_KEY_PATTERN})['\"]?\s*[:=]\s*['\"]?)(?P<value>[^,'\"}}\]\s]+)",
    flags=re.IGNORECASE,
)


def scrub(text: str) -> str:
    """Замаскировать секреты и персональные данные в произвольном тексте.

    Заменяет на ``***`` значение после чувствительного ключа (``pin=1234``,
    ``"session_id": "…"``, ``card-id: …``), адреса почты и телефоны. Ключ остаётся,
    чтобы по журналу было видно, какое поле скрыто. Ключ ``code`` тоже считается
    чувствительным (код подтверждения), поэтому ``code: Field required`` в тексте
    ошибки Pydantic превращается в ``code: *** required``.

    :param text: Текст сообщения, ошибки или значения для журнала.
    :return: Текст той же структуры со скрытыми значениями.
    """
    redacted = _KEY_VALUE_RE.sub(lambda match: f"{match.group('prefix')}{REDACTED}", text)
    redacted = _EMAIL_RE.sub(REDACTED, redacted)
    return _PHONE_RE.sub(REDACTED, redacted)


def is_sensitive_log_key(key: str) -> bool:
    """Проверить, что значение поля с таким именем нельзя писать в журнал.

    Регистр, пробелы по краям и дефис вместо подчёркивания не важны:
    ``Card-Id`` и ``card_id`` равнозначны.

    :param key: Имя поля словаря или параметра.
    :return: ``True``, если ключ есть в ``SENSITIVE_LOG_KEYS``.
    """
    normalized = key.strip().lower().replace("-", "_")
    return normalized in SENSITIVE_LOG_KEYS


def message_mentions_sensitive_key(text: str) -> bool:
    """Проверить, упоминает ли текст чувствительный ключ где угодно.

    Нужна, когда текст нельзя безопасно разобрать на пары ключ–значение (например,
    ответ сервера): такое сообщение заменяют безопасным текстом целиком.

    :param text: Проверяемый текст.
    :return: ``True``, если в тексте найдено имя чувствительного ключа.
    """
    return bool(_SENSITIVE_KEY_RE.search(text))


def sanitize_for_logging(value: Any) -> Any:
    """Рекурсивно очистить значение перед записью в журнал.

    Словари: значения чувствительных ключей заменяются на ``***``, остальные
    очищаются вглубь. Списки, кортежи и множества сохраняют свой тип. Строки
    проходят через :func:`scrub`. Исключение целиком заменяется заглушкой: его текст
    и аргументы могут содержать запрос или ответ с секретами.

    :param value: Любое значение из полей события журнала.
    :return: Безопасная для журнала копия; исходное значение не меняется.
    """
    if isinstance(value, BaseException):
        return "[подробности исключения скрыты]"

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
