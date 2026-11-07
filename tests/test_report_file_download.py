"""Скачивание отчёта: сервер отвечает файлом, а не JSON (ответ application/octet-stream)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from apisdkopti24 import APIClient, AsyncTransport, ConnectionSettings, StaticCredentialsProvider
from tests.service_support import UNTHROTTLED
from tests.test_audit_metrics import AUTH_RESPONSE

REPORT_BYTES = b"PK\x03\x04 report body \x00\xff"


def _file_api(seen: list[httpx.URL]):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/v1/authUser"):
            return httpx.Response(200, json=AUTH_RESPONSE)
        seen.append(request.url)
        return httpx.Response(
            200,
            content=REPORT_BYTES,
            headers={"content-type": "application/octet-stream"},
        )

    return handler


def _client(http_client: httpx.AsyncClient) -> APIClient:
    settings = ConnectionSettings(base_url="https://api.example.ru/vip/")
    transport = AsyncTransport(
        settings.base_url, http_client=http_client, rate_limit_policy=UNTHROTTLED
    )
    # Заглушка MockTransport не проверяет учётные данные.
    fake_value = "not-a-real-credential"
    credentials = StaticCredentialsProvider(
        api_key=fake_value, login=fake_value, password=fake_value
    )
    return APIClient(settings=settings, transport=transport, credentials_provider=credentials)


@pytest.mark.asyncio
async def test_report_file_downloads_accept_binary_response(tmp_path: Path) -> None:
    seen: list[httpx.URL] = []
    mock = httpx.MockTransport(_file_api(seen))
    async with httpx.AsyncClient(transport=mock) as http_client, _client(http_client) as client:
        in_memory = await client.reports.download_report_file(job_id="job-1")
        v2_file = await client.reports.download_report_file_to(
            job_id="job-1", destination=tmp_path / "v2.xlsx"
        )
        in_memory_v1 = await client.reports.download_report_file_v1(job_id="job-2")
        v1_file = await client.reports.download_report_file_v1_to(
            job_id="job-2", destination=tmp_path / "v1.xlsx"
        )

    assert in_memory == REPORT_BYTES
    assert in_memory_v1 == REPORT_BYTES
    assert v2_file.read_bytes() == REPORT_BYTES
    assert v1_file.read_bytes() == REPORT_BYTES
    assert [url.path for url in seen] == [
        "/vip/v2/reports/jobs/job-1",
        "/vip/v2/reports/jobs/job-1",
        "/vip/v1/getReportFile",
        "/vip/v1/getReportFile",
    ]
    assert seen[2].params["job_id"] == "job-2"
