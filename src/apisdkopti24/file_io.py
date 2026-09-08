from __future__ import annotations

import asyncio
import os
import tempfile
from collections.abc import AsyncIterable
from pathlib import Path
from typing import BinaryIO, Protocol


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
        output, temporary = self._temporary_file(destination)
        try:
            await asyncio.to_thread(output.write, content)
            await self._close_output(output)
            await asyncio.to_thread(os.replace, temporary, destination)
        finally:
            if not output.closed:
                output.close()
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
        output, temporary = self._temporary_file(destination)
        try:
            buffer = bytearray()
            async for chunk in chunks:
                buffer.extend(chunk)
                if len(buffer) >= write_buffer_size:
                    await asyncio.to_thread(output.write, bytes(buffer))
                    buffer.clear()
            if buffer:
                await asyncio.to_thread(output.write, bytes(buffer))
            await self._close_output(output)
            await asyncio.to_thread(os.replace, temporary, destination)
        finally:
            if not output.closed:
                output.close()
            temporary.unlink(missing_ok=True)
        return destination

    @staticmethod
    def _temporary_file(destination: Path) -> tuple[BinaryIO, Path]:
        descriptor, temporary_path = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".part",
        )
        return os.fdopen(descriptor, "w+b"), Path(temporary_path)

    @staticmethod
    async def _close_output(output: BinaryIO) -> None:
        await asyncio.to_thread(output.flush)
        await asyncio.to_thread(os.fsync, output.fileno())
        await asyncio.to_thread(output.close)


__all__ = ["AtomicFileWriter", "FileWriter"]
