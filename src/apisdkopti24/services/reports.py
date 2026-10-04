from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, get_args

from ..errors import RequestValidationError
from ..models.reports import (
    ReportJobListResponse,
    ReportListResponse,
    ReportOrderRequest,
    ReportOrderResponse,
    ReportV1JobListResponse,
    ReportV1OrderResponse,
)
from ..operations import binary_operation, operation
from ..service_base import _StreamingService
from ..utils import to_json_param
from ..validation import (
    require_identifier,
    validate_email,
    validate_email_list,
    validate_identifier_list,
    validate_non_empty_value,
    validate_period_months,
)

GET_REPORTS = operation("get_reports", ReportListResponse)
ORDER_REPORT = operation("order_report", ReportOrderResponse)
GET_REPORT_JOBS = operation("get_report_jobs", ReportJobListResponse)
DOWNLOAD_REPORT_FILE = binary_operation("download_report_file")
ORDER_REPORT_V1 = operation("order_report_v1", ReportV1OrderResponse)
GET_REPORT_JOB_LIST_V1 = operation("get_report_job_list_v1", ReportV1JobListResponse)
DOWNLOAD_REPORT_FILE_V1 = binary_operation("download_report_file_v1")

ReportV1Format = Literal["xlsx", "xml", "pdf", "csv"]
# Сервер не отклоняет более длинный период, а молча сокращает его.
ORDER_REPORT_MAX_MONTHS = 1
ORDER_REPORT_V1_MAX_MONTHS = 3


def _validate_report_period(params: Mapping[str, Any]) -> None:
    start, end = params.get("start_date"), params.get("end_date")
    if start is not None and end is not None:
        validate_period_months(
            start,
            end,
            months=ORDER_REPORT_MAX_MONTHS,
            start_name="start_date",
            end_name="end_date",
        )


class ReportsService(_StreamingService):
    """Методы работы с отчётами (v1 и v2)."""

    async def get_reports(
        self,
        *,
        api_version: str | None = None,
    ) -> ReportListResponse:
        """Получить список доступных отчётов v2."""
        return await self._request(GET_REPORTS, api_version=api_version)

    async def order_report(
        self,
        *,
        report_id: str,
        format: str,
        params: dict[str, Any],
        emails: list[str] | None = None,
        api_version: str | None = None,
    ) -> ReportOrderResponse:
        """Заказать формирование отчёта v2.

        Типовой сценарий:
            Создать асинхронную задачу отчёта, затем получить её статус и файл.

        Пример:
            ``await client.reports.order_report(report_id="id", format="xlsx", params={})``

        ``emails`` — список адресов; без него отчёт доступен только по ссылке.
        ``params.id_agreement``, ``id_card``, ``card_group_code`` и ``id_client`` —
        списки строк. Если заданы ``params.start_date`` и ``params.end_date``, SDK до
        запроса проверяет формат ``YYYY-MM-DD``, порядок дат и длину периода — не
        больше 1 календарного месяца (конец не позже той же даты следующего месяца).
        Более длинный период сервер не отклоняет, а молча сокращает.
        """
        _validate_report_period(params)
        request = ReportOrderRequest.model_validate(
            {
                "id": require_identifier(report_id, "report_id"),
                "format": validate_non_empty_value(format, "format"),
                "params": params,
                "emails": validate_email_list(emails, "emails") if emails is not None else None,
            }
        )
        return await self._request(
            ORDER_REPORT,
            api_version=api_version,
            json_body=request.model_dump(exclude_none=True, by_alias=True),
        )

    async def get_report_jobs(
        self,
        *,
        api_version: str | None = None,
    ) -> ReportJobListResponse:
        """Получить список задач формирования отчётов v2."""
        return await self._request(GET_REPORT_JOBS, api_version=api_version)

    async def download_report_file(
        self,
        *,
        job_id: str,
        api_version: str | None = None,
    ) -> bytes:
        """Скачать сформированный отчёт v2 в память."""
        return await self._request_stream(
            DOWNLOAD_REPORT_FILE,
            api_version=api_version,
            path_params={"job_id": require_identifier(job_id, "job_id")},
        )

    async def download_report_file_to(
        self,
        *,
        job_id: str,
        destination: str | Path,
        api_version: str | None = None,
    ) -> Path:
        """Потоково скачать отчёт v2 в файл."""
        return await self._request_stream_to_file(
            DOWNLOAD_REPORT_FILE,
            destination,
            api_version=api_version,
            path_params={"job_id": require_identifier(job_id, "job_id")},
        )

    async def order_report_v1(
        self,
        *,
        start: str,
        end: str,
        report_format: ReportV1Format,
        contract_id: str | None = None,
        email: str | None = None,
        cards_list: list[str] | None = None,
        group_id: list[str] | None = None,
        archive: bool = False,
        api_version: str | None = None,
    ) -> ReportV1OrderResponse:
        """Заказать транзакционный отчёт v1.

        ``start`` и ``end`` — даты ``YYYY-MM-DD``; период не длиннее 3 календарных
        месяцев (конец не позже той же даты через 3 месяца). Более длинный период
        сервер не отклоняет, а молча сокращает, поэтому SDK отклоняет его до
        запроса. ``report_format`` — ``xlsx``, ``xml``, ``pdf`` или ``csv``. Без
        ``contract_id`` используется выбранный договор сессии.
        """
        validate_period_months(
            start,
            end,
            months=ORDER_REPORT_V1_MAX_MONTHS,
            start_name="start",
            end_name="end",
        )
        if report_format not in get_args(ReportV1Format):
            raise RequestValidationError(
                f"report_format должен быть одним из: {', '.join(get_args(ReportV1Format))}"
            )
        params: dict[str, Any] = {"start": start, "end": end, "report_format": report_format}
        if email is not None:
            params["email"] = validate_email(email)
        if cards_list is not None:
            params["cards_list"] = to_json_param(validate_identifier_list(cards_list, "cards_list"))
        if group_id is not None:
            params["group_id"] = to_json_param(validate_identifier_list(group_id, "group_id"))
        if archive:
            params["archive"] = "true"
        cid = await self._resolve_contract_id(contract_id)
        params = {"contract_id": cid, **params}
        return await self._request(
            ORDER_REPORT_V1,
            api_version=api_version,
            query=params,
            contract_header=cid,
        )

    async def get_report_job_list_v1(
        self,
        *,
        api_version: str | None = None,
    ) -> ReportV1JobListResponse:
        """Получить список задач формирования отчётов v1."""
        return await self._request(GET_REPORT_JOB_LIST_V1, api_version=api_version)

    async def download_report_file_v1(
        self,
        *,
        job_id: str,
        archive: bool = False,
        api_version: str | None = None,
    ) -> bytes:
        """Скачать сформированный отчёт v1 в память."""
        params = {"job_id": require_identifier(job_id, "job_id")}
        if archive:
            params["archive"] = "true"
        return await self._request_stream(
            DOWNLOAD_REPORT_FILE_V1,
            api_version=api_version,
            query=params,
        )

    async def download_report_file_v1_to(
        self,
        *,
        job_id: str,
        destination: str | Path,
        archive: bool = False,
        api_version: str | None = None,
    ) -> Path:
        """Потоково скачать отчёт v1 в файл."""
        params = {"job_id": require_identifier(job_id, "job_id")}
        if archive:
            params["archive"] = "true"
        return await self._request_stream_to_file(
            DOWNLOAD_REPORT_FILE_V1,
            destination,
            api_version=api_version,
            query=params,
        )
