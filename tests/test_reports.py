from pathlib import Path

import pytest

from api_client_opti24.models.reports import ReportListResponse
from api_client_opti24.services.reports import ReportsService
from api_client_opti24.session import SessionManager
from tests.service_support import (
    RecordingRequestExecutor,
    StubSessionGate,
    operation_name,
    service_dependencies,
)


@pytest.mark.asyncio
async def test_get_reports_returns_full_envelope() -> None:
    executor = RecordingRequestExecutor(
        {
            "get_reports": {
                "status": {"code": 200},
                "data": {"total_count": 1, "result": []},
                "timestamp": 1710000000,
            }
        }
    )
    session = SessionManager()
    service = ReportsService(executor, session, StubSessionGate(), service_dependencies(session)[3])

    response = await service.get_reports()

    assert isinstance(response, ReportListResponse)
    assert response.status.code == 200
    assert response.data.total_count == 1
    assert response.timestamp == 1710000000


@pytest.mark.asyncio
async def test_download_report_file_to_delegates_streaming(tmp_path: Path) -> None:
    class FileExecutor(RecordingRequestExecutor):
        async def execute_stream_to_file(
            self,
            operation: object,
            destination: str | Path,
            *,
            api_version: str | None = None,
            route_name: str = "default",
            path_params: object = None,
            **kwargs: object,
        ) -> Path:
            del api_version, route_name, kwargs
            self.calls.append((operation_name(operation), {"path_params": path_params}))
            target = Path(destination)
            target.write_bytes(b"report")
            return target

    executor = FileExecutor({})
    session = SessionManager()
    service = ReportsService(executor, session, StubSessionGate(), service_dependencies(session)[3])
    destination = tmp_path / "report.xlsx"

    result = await service.download_report_file_to(
        job_id="job-id",
        destination=destination,
    )

    assert result == destination
    assert destination.read_bytes() == b"report"
    assert executor.calls == [("download_report_file", {"path_params": {"job_id": "job-id"}})]
