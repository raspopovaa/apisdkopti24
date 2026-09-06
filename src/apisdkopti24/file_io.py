from __future__ import annotations

import asyncio
import os
import tempfile
from collections.abc import AsyncIterable
from pathlib import Path
from typing import Protocol


class FileWriter(Protocol):
    async def write_bytes(self, destination: Path, content: bytes) -> Path: ...

    async def write_stream(
        self,
        destination: Path,
        chunks: AsyncIterable[bytes],
        *,
        write_buffer_size: int,
    ) -> Path: ...


class AtomicFileWriter:
    """Write downloads atomically without exposing partial target files."""

    async def write_bytes(self, destination: Path, content: bytes) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._temporary_path(destination)
        try:
            await asyncio.to_thread(temporary.write_bytes, content)
            await asyncio.to_thread(os.replace, temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        return destination

    async def write_stream(
        self,
        destination: Path,
        chunks: AsyncIterable[bytes],
        *,
        write_buffer_size: int,
    ) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._temporary_path(destination)
        try:
            with temporary.open("wb") as output:
                buffer = bytearray()
                async for chunk in chunks:
                    buffer.extend(chunk)
                    if len(buffer) >= write_buffer_size:
                        await asyncio.to_thread(output.write, bytes(buffer))
                        buffer.clear()
                if buffer:
                    await asyncio.to_thread(output.write, bytes(buffer))
            await asyncio.to_thread(os.replace, temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        return destination

    @staticmethod
    def _temporary_path(destination: Path) -> Path:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".part",
            delete=False,
        ) as temporary:
            return Path(temporary.name)


__all__ = ["AtomicFileWriter", "FileWriter"]
