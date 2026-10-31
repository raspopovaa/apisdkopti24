from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pytest

from apisdkopti24.errors import AccessDeniedError, ReportWaitTimeoutError, RequestValidationError
from apisdkopti24.models.reports import ReportJobItem, ReportListResponse, ReportParameter
from apisdkopti24.operations import OperationSpec
from apisdkopti24.requests import RequestOptions
from apisdkopti24.service_groups import ServiceContainer
from apisdkopti24.services.auth import AuthService
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
            operation: OperationSpec[bytes],
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
        ("01.09.2026", "2026-09-30", "xlsx", "start: ожидается дата"),
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


class _SequencedJobsExecutor(RecordingRequestExecutor):
    """Отдавать ``get_report_jobs`` по очереди из заданного списка ответов."""

    def __init__(self, job_pages: list[list[dict[str, object]]]) -> None:
        super().__init__({})
        self.job_pages = job_pages

    async def execute(self, operation: Any, options: RequestOptions | None = None) -> Any:
        page = self.job_pages[min(len(self.calls), len(self.job_pages) - 1)]
        self.responses["get_report_jobs"] = {
            "status": {"code": 200},
            "data": {"total_count": len(page), "result": page},
            "timestamp": 1710000000,
        }
        return await super().execute(operation, options)


def _job(job_id: str, available_after: int) -> dict[str, object]:
    return {
        "date": "2026-10-01 10:00:00",
        "client_id": "client-id",
        "user_id": "user-id",
        "contract_id": "contract-id",
        "job_id": job_id,
        "report_name": "Транзакционный отчёт",
        "report_format": "xlsx",
        "available_after": available_after,
    }


class _FakeClock:
    def __init__(self) -> None:
        self.current = 1000.0
        self.sleeps: list[float] = []

    def now(self) -> datetime:
        raise AssertionError("Ожидание отчёта не должно читать календарное время")

    def monotonic(self) -> float:
        return self.current

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.current += seconds


@pytest.fixture
def fake_clock() -> _FakeClock:
    return _FakeClock()


def _reports_service(
    executor: RecordingRequestExecutor, clock: _FakeClock | None = None
) -> ReportsService:
    session = SessionManager()
    return ReportsService(
        executor, session, StubSessionGate(), service_dependencies(session)[3], clock=clock
    )


@pytest.mark.asyncio
async def test_wait_for_report_polls_free_job_list_until_ready(fake_clock: _FakeClock) -> None:
    executor = _SequencedJobsExecutor(
        [
            [],
            [_job("other-job", 0), _job("job-id", 120)],
            [_job("job-id", 3)],
            [_job("job-id", 0)],
        ]
    )

    job = await _reports_service(executor, fake_clock).wait_for_report(
        job_id="job-id", poll_interval=10
    )

    assert isinstance(job, ReportJobItem)
    assert job.job_id == "job-id"
    assert job.available_after == 0
    assert [name for name, _ in executor.calls] == ["get_report_jobs"] * 4
    # Нет задачи — poll_interval; available_after больше интервала — ждём его;
    # меньше интервала — не опрашиваем чаще poll_interval.
    assert fake_clock.sleeps == [10.0, 120.0, 10.0]


@pytest.mark.asyncio
async def test_wait_for_report_returns_immediately_when_ready(fake_clock: _FakeClock) -> None:
    executor = _SequencedJobsExecutor([[_job("job-id", 0)]])

    job = await _reports_service(executor, fake_clock).wait_for_report(job_id="job-id")

    assert job.job_id == "job-id"
    assert len(executor.calls) == 1
    assert fake_clock.sleeps == []


@pytest.mark.asyncio
async def test_wait_for_report_times_out_with_last_countdown(fake_clock: _FakeClock) -> None:
    executor = _SequencedJobsExecutor([[_job("job-id", 300)]])

    with pytest.raises(ReportWaitTimeoutError) as caught:
        await _reports_service(executor, fake_clock).wait_for_report(
            job_id="job-id", timeout=100, poll_interval=30
        )

    assert caught.value.job_id == "job-id"
    assert caught.value.timeout == 100.0
    assert caught.value.available_after == 300
    assert "job-id" not in str(caught.value)
    # Ожидание обрезается по остатку срока, последний опрос — на самом сроке.
    assert fake_clock.sleeps == [100.0]
    assert len(executor.calls) == 2


@pytest.mark.asyncio
async def test_wait_for_report_times_out_when_job_never_listed(fake_clock: _FakeClock) -> None:
    executor = _SequencedJobsExecutor([[_job("other-job", 0)]])

    with pytest.raises(ReportWaitTimeoutError, match="не появилась") as caught:
        await _reports_service(executor, fake_clock).wait_for_report(
            job_id="job-id", timeout=25, poll_interval=10
        )

    assert caught.value.available_after is None
    assert fake_clock.sleeps == [10.0, 10.0, 5.0]


@pytest.mark.asyncio
async def test_wait_for_report_propagates_api_error_without_extra_polls(
    fake_clock: _FakeClock,
) -> None:
    class FailingExecutor(RecordingRequestExecutor):
        async def execute(self, operation: Any, options: RequestOptions | None = None) -> Any:
            self.calls.append((operation_name(operation), {}))
            raise AccessDeniedError(403, "Доступ запрещён")

    executor = FailingExecutor({})

    with pytest.raises(AccessDeniedError):
        await _reports_service(executor, fake_clock).wait_for_report(job_id="job-id")

    assert len(executor.calls) == 1
    assert fake_clock.sleeps == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"job_id": ""}, "job_id"),
        ({"job_id": "job-id", "timeout": 0}, "timeout"),
        ({"job_id": "job-id", "timeout": float("inf")}, "timeout"),
        ({"job_id": "job-id", "timeout": True}, "timeout"),
        ({"job_id": "job-id", "poll_interval": 1}, "poll_interval"),
        ({"job_id": "job-id", "poll_interval": float("nan")}, "poll_interval"),
    ],
)
async def test_wait_for_report_rejects_invalid_arguments_without_request(
    arguments: dict[str, Any], message: str
) -> None:
    executor = RecordingRequestExecutor({})

    with pytest.raises(RequestValidationError, match=message):
        await _reports_service(executor).wait_for_report(**arguments)

    assert executor.calls == []


@pytest.mark.asyncio
async def test_service_container_passes_client_clock_to_report_waiting(
    fake_clock: _FakeClock,
) -> None:
    executor = _SequencedJobsExecutor([[_job("job-id", 30)], [_job("job-id", 0)]])
    session = SessionManager()
    services = ServiceContainer.create(
        request_executor=executor,
        session_context=session,
        session_gate=StubSessionGate(),
        logger=service_dependencies(session)[3],
        auth=cast(AuthService, None),
        clock=fake_clock,
    )

    await services.reports.wait_for_report(job_id="job-id")

    assert fake_clock.sleeps == [30.0]


@pytest.mark.asyncio
async def test_service_container_create_keeps_clock_optional() -> None:
    session = SessionManager()
    services = ServiceContainer.create(
        request_executor=_SequencedJobsExecutor([]),
        session_context=session,
        session_gate=StubSessionGate(),
        logger=service_dependencies(session)[3],
        auth=cast(AuthService, None),
    )

    assert isinstance(services.reports, ReportsService)
