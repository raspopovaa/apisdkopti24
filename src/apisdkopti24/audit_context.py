"""Связь событий аудита SDK с операцией вызывающего приложения.

Приложение (например, ИИ-агент) оборачивает свой шаг в ``correlation_scope`` и
передаёт идентификатор хода или вызова инструмента. Все операции SDK внутри блока,
включая задачи asyncio, созданные в нём, пишут этот идентификатор в аудит.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from .errors import SDKConfigurationError

_CORRELATION_ID: ContextVar[str | None] = ContextVar("apisdkopti24_correlation_id", default=None)
# Только безопасные символы: значение пишется в журнал без очистки, иначе фильтр
# принял бы цифры UUID за телефон и испортил бы идентификатор.
_CORRELATION_ID_RE = re.compile(r"[A-Za-z0-9._:-]{1,128}")


@contextmanager
def correlation_scope(correlation_id: str) -> Iterator[str]:
    """Писать ``correlation_id`` во все события аудита внутри блока ``with``.

    Допустимы латиница, цифры и ``. _ : -``, длина от 1 до 128 символов. Не
    передавайте персональные данные: значение попадает в журнал как есть.
    """
    if not isinstance(correlation_id, str) or not _CORRELATION_ID_RE.fullmatch(correlation_id):
        raise SDKConfigurationError(
            "correlation_id: от 1 до 128 символов, только латиница, цифры и . _ : -"
        )
    token = _CORRELATION_ID.set(correlation_id)
    try:
        yield correlation_id
    finally:
        _CORRELATION_ID.reset(token)


def current_correlation_id() -> str | None:
    """Вернуть ``correlation_id`` текущего блока ``correlation_scope`` или ``None``."""
    return _CORRELATION_ID.get()


__all__ = ["correlation_scope", "current_correlation_id"]
