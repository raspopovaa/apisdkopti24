from pathlib import Path

import httpx
import pytest

from apisdkopti24.downloads import BoundedResponseReader, DownloadResponseHandler
from apisdkopti24.file_io import AtomicFileWriter
from apisdkopti24.requests import FileTarget
from apisdkopti24.response import ResponseDecoder
from tests.prepared_request_support import prepared_request


@pytest.mark.asyncio
async def test_bounded_reader_rejects_declared_oversized_response() -> None:
    response = httpx.Response(
        200,
        headers={"content-length": "101"},
        content=b"short",
        request=httpx.Request("GET", "https://example.test/file"),
    )

    with pytest.raises(ValueError, match="100-byte limit"):
        await BoundedResponseReader().read(response, 100)


@pytest.mark.asyncio
async def test_download_handler_writes_successful_binary_response(tmp_path: Path) -> None:
    response = httpx.Response(
        200,
        headers={"content-type": "application/octet-stream"},
        content=b"report",
        request=httpx.Request("GET", "https://example.test/file"),
    )
    handler = DownloadResponseHandler(
        decoder=ResponseDecoder(),
        file_writer=AtomicFileWriter(),
        max_in_memory_response_bytes=100,
        max_error_response_bytes=50,
    )
    destination = tmp_path / "report.bin"

    result = await handler.handle(
        response,
        prepared_request("GET", "reports/job/file"),
        FileTarget(destination),
    )

    assert result == destination
    assert destination.read_bytes() == b"report"
