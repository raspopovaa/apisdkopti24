from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

import httpx
from pytest import MonkeyPatch

from apisdkopti24 import AsyncTransport


class CountingStream(httpx.AsyncByteStream):
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks
        self.consumed = 0

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            self.consumed += 1
            yield chunk


def patch_stream(
    monkeypatch: MonkeyPatch,
    transport: AsyncTransport,
    request: Callable[..., Awaitable[httpx.Response]],
) -> None:
    """Адаптировать тестовую функцию одного HTTP-вызова к streaming API транспорта."""

    @asynccontextmanager
    async def stream(*args: Any, **kwargs: Any) -> AsyncIterator[httpx.Response]:
        yield await request(*args, **kwargs)

    monkeypatch.setattr(transport.client, "stream", stream)


__all__ = ["CountingStream", "patch_stream"]
