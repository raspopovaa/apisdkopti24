from pathlib import Path

import httpx
import pytest

from apisdkopti24.downloads import BoundedResponseReader, DownloadResponseHandler
from apisdkopti24.errors import ResponseTooLargeError
from apisdkopti24.file_io import AtomicFileWriter
from apisdkopti24.requests import FileTarget
from apisdkopti24.response import ResponseDecoder
from tests.prepared_request_support import prepared_request
from tests.stream_support import CountingStream


@pytest.mark.asyncio
async def test_bounded_reader_rejects_declared_oversized_response() -> None:
    response = httpx.Response(
        200,
        headers={"content-length": "101"},
        content=b"short",
        request=httpx.Request("GET", "https://example.test/file"),
    )

    with pytest.raises(ResponseTooLargeError) as captured:
        await BoundedResponseReader().read(response, 100)

    assert captured.value.maximum_bytes == 100


@pytest.mark.asyncio
async def test_bounded_reader_returns_every_chunk_up_to_the_exact_limit() -> None:
    stream = CountingStream([b"1234", b"56"])
    response = httpx.Response(
        200,
        stream=stream,
        request=httpx.Request("GET", "https://example.test/data"),
    )

    assert await BoundedResponseReader().read(response, 6) == b"123456"


@pytest.mark.asyncio
async def test_bounded_reader_stops_stream_after_limit_is_exceeded() -> None:
    stream = CountingStream([b"1234", b"5678", b"should-not-be-read"])
    response = httpx.Response(
        200,
        stream=stream,
        request=httpx.Request("GET", "https://example.test/data"),
    )

    with pytest.raises(ResponseTooLargeError):
        await BoundedResponseReader().read(response, 6)

    assert stream.consumed == 2


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


@pytest.mark.parametrize("target", [None, "file"])
@pytest.mark.asyncio
async def test_compressed_json_error_of_download_becomes_api_error(tmp_path: Path, target) -> None:
    # Сжатое тело ошибки читается уже распакованным; пересобранный ответ не должен
    # распаковываться второй раз, иначе ошибка API превращается в сетевую.
    import gzip
    import json

    from apisdkopti24 import AsyncTransport, NotFoundError

    body = {
        "status": {
            "code": 404,
            "errors": [{"type": "notFound", "message": "Формирование отчета не завершено"}],
        }
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            content=gzip.compress(json.dumps(body).encode()),
            headers={"content-type": "application/json", "content-encoding": "gzip"},
            request=request,
        )

    transport = AsyncTransport(
        "https://api.example.test/vip/",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    request = prepared_request("get", "reports/jobs/job-1/file")
    with pytest.raises(NotFoundError) as caught:
        if target is None:
            await transport.request_stream(request)
        else:
            await transport.request_stream_to_file(request, FileTarget(tmp_path / "report.xlsx"))

    assert "Формирование отчета не завершено" in str(caught.value)
    assert not (tmp_path / "report.xlsx").exists()
    await transport.aclose()
