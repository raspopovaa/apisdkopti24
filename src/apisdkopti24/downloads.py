from __future__ import annotations

from pathlib import Path

import httpx

from .errors import ResponseTooLargeError
from .file_io import FileWriter
from .requests import FileTarget, PreparedRequest
from .response import ResponseDecoder


class BoundedResponseReader:
    async def read(self, response: httpx.Response, maximum_bytes: int) -> bytes:
        content_length = response.headers.get("content-length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError:
                declared_size = None
            if declared_size is not None and declared_size > maximum_bytes:
                raise ResponseTooLargeError(maximum_bytes=maximum_bytes)

        content = bytearray()
        async for chunk in response.aiter_bytes():
            if len(content) + len(chunk) > maximum_bytes:
                raise ResponseTooLargeError(maximum_bytes=maximum_bytes)
            content.extend(chunk)
        return bytes(content)


class DownloadResponseHandler:
    """Разобрать ответ с ошибкой в пределах лимита; загрузить успешный ответ в память или файл."""

    def __init__(
        self,
        *,
        decoder: ResponseDecoder,
        file_writer: FileWriter,
        reader: BoundedResponseReader | None = None,
        max_in_memory_response_bytes: int,
        max_error_response_bytes: int,
    ) -> None:
        self._decoder = decoder
        self._file_writer = file_writer
        self._reader = reader or BoundedResponseReader()
        self._max_in_memory_response_bytes = max_in_memory_response_bytes
        self._max_error_response_bytes = max_error_response_bytes

    async def handle(
        self,
        response: httpx.Response,
        request: PreparedRequest,
        target: FileTarget | None,
    ) -> bytes | Path:
        content_type = response.headers.get("content-type", "").lower()
        if not 200 <= response.status_code < 300 or "json" in content_type:
            content = await self._reader.read(response, self._max_error_response_bytes)
            decoded_response = httpx.Response(
                response.status_code,
                headers=response.headers,
                content=content,
                request=response.request,
            )
            self._decoder.decode_bytes(
                decoded_response,
                content,
                request.endpoint,
                method_name=request.method_name,
            )
            if target is None:
                return content
            return await self._file_writer.write_bytes(target.destination, content)
        if target is None:
            return await self._reader.read(response, self._max_in_memory_response_bytes)
        return await self._file_writer.write_stream(
            target.destination,
            response.aiter_bytes(target.chunk_size),
            write_buffer_size=target.write_buffer_size,
        )


__all__ = ["BoundedResponseReader", "DownloadResponseHandler"]
