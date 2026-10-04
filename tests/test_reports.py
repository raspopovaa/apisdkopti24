from pathlib import Path

import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.models.reports import ReportListResponse, ReportParameter
from apisdkopti24.requests import RequestOptions
from apisdkopti24.services.reports import ReportsService
from apisdkopti24.session import SessionManager
from tests.service_support import (
    CountingSessionGate,
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
            options: RequestOptions | None = None,
        ) -> Path:
            request_options = options or RequestOptions()
            self.calls.append(
                (operation_name(operation), {"path_params": request_options.path_params or None})
            )
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


def test_report_parameter_label_is_required_but_nullable() -> None:
    parameter = ReportParameter.model_validate(
        {"name": "contract", "value": None, "label": None, "type": "Contract"}
    )
    assert parameter.label is None


def _gated_reports(
    responses: dict[str, dict[str, object]] | None = None,
    *,
    contract_id: str | None = None,
) -> tuple[ReportsService, RecordingRequestExecutor, CountingSessionGate]:
    executor = RecordingRequestExecutor(responses or {})
    session = SessionManager()
    if contract_id is not None:
        session.mark_authenticated("session-id", contract_id)
    gate = CountingSessionGate()
    service = ReportsService(executor, session, gate, service_dependencies(session)[3])
    return service, executor, gate


TRANSACTION_REPORT = "tsc_report_transaction_reriod"


@pytest.mark.asyncio
async def test_order_report_sends_list_parameters_and_emails_as_arrays() -> None:
    service, executor, _ = _gated_reports(
        {"order_report": {"status": {"code": 200}, "data": {"job_id": ["job-1"]}}}
    )

    await service.order_report(
        report_id=TRANSACTION_REPORT,
        format="xlsx",
        params={
            "start_date": "2026-09-01",
            "end_date": "2026-10-01",
            "id_agreement": ["contract-id"],
        },
        emails=["first@example.org", "second@example.org"],
    )

    assert executor.calls[0][1]["json_body"] == {
        "id": TRANSACTION_REPORT,
        "format": "xlsx",
        "emails": ["first@example.org", "second@example.org"],
        "params": {
            "start_date": "2026-09-01",
            "end_date": "2026-10-01",
            "id_agreement": ["contract-id"],
        },
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("params", "emails"),
    [
        ({"start_date": "2026-09-01", "end_date": "2026-10-02"}, None),
        ({"start_date": "2026-01-31", "end_date": "2026-03-01"}, None),
        ({"start_date": "2026-09-30", "end_date": "2026-09-01"}, None),
        ({"start_date": "01.09.2026", "end_date": "2026-09-30"}, None),
        ({}, "accounting@example.org"),
        ({}, []),
        ({}, ["not-an-email"]),
    ],
    ids=[
        "longer-than-month",
        "end-of-month-overflow",
        "end-before-start",
        "bad-date-format",
        "emails-as-string",
        "empty-emails",
        "invalid-email",
    ],
)
async def test_order_report_rejects_invalid_input_before_request(
    params: dict[str, object], emails: object
) -> None:
    service, executor, gate = _gated_reports()

    with pytest.raises(RequestValidationError):
        await service.order_report(
            report_id=TRANSACTION_REPORT,
            format="xlsx",
            params=params,
            emails=emails,  # type: ignore[arg-type]
        )

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("start", "end", "report_format", "message"),
    [
        ("2026-01-01", "2026-04-02", "xlsx", "3 календарных месяцев"),
        ("2026-09-30", "2026-09-01", "xlsx", "end не может предшествовать start"),
        ("01.09.2026", "2026-09-30", "xlsx", "start и end"),
        ("2026-09-01", "2026-09-30", "docx", "report_format"),
    ],
    ids=["longer-than-3-months", "end-before-start", "bad-date-format", "unknown-format"],
)
async def test_order_report_v1_rejects_invalid_input_before_login(
    start: str, end: str, report_format: str, message: str
) -> None:
    service, executor, gate = _gated_reports()

    with pytest.raises(RequestValidationError, match=message):
        await service.order_report_v1(
            start=start,
            end=end,
            report_format=report_format,  # type: ignore[arg-type]
        )

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
async def test_order_report_v1_uses_selected_contract_and_allows_three_months() -> None:
    service, executor, _ = _gated_reports(
        {"order_report_v1": {"status": {"code": 200}, "data": ["job-1"]}},
        contract_id="selected-contract",
    )

    await service.order_report_v1(start="2026-01-31", end="2026-04-30", report_format="csv")

    call = executor.calls[0][1]
    assert call["query"]["contract_id"] == "selected-contract"
    assert call["query"]["start"] == "2026-01-31"
    assert call["contract_header"] == "selected-contract"


def test_unused_report_file_model_is_removed() -> None:
    import apisdkopti24.models.reports as reports_models

    assert not hasattr(reports_models, "ReportFileResponse")
