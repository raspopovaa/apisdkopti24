import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, get_args

from ..errors import ReportWaitTimeoutError, RequestValidationError
from ..logger import LoggerLike
from ..models.reports import (
    ReportJobItem,
    ReportJobListResponse,
    ReportListResponse,
    ReportOrderRequest,
    ReportOrderResponse,
    ReportV1JobListResponse,
    ReportV1OrderResponse,
)
from ..operations import binary_operation, operation
from ..runtime import Clock, SystemClock
from ..service_base import RequestExecutor, SessionContext, SessionGate, _StreamingService
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
# Ожидание вызывает только бесплатный get_report_jobs; пауза не короче минимальной,
# чтобы не опрашивать список чаще, чем отчёт успевает продвинуться.
WAIT_FOR_REPORT_MIN_POLL_INTERVAL = 5.0


def _require_positive_seconds(value: float, name: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise RequestValidationError(f"{name} должен быть числом секунд")
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0 or seconds < minimum:
        bound = f"не меньше {minimum:g}" if minimum > 0 else "больше 0"
        raise RequestValidationError(f"{name} должен быть конечным числом секунд {bound}")
    return seconds


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

    def __init__(
        self,
        request_executor: RequestExecutor,
        session_context: SessionContext,
        session_gate: SessionGate,
        logger: LoggerLike,
        *,
        clock: Clock | None = None,
    ) -> None:
        super().__init__(request_executor, session_context, session_gate, logger)
        self.__clock = clock or SystemClock()

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

        ``emails``: список адресов; без него отчёт доступен только по ссылке.
        ``params.id_agreement``, ``id_card``, ``card_group_code`` и ``id_client``:
        списки строк. Если заданы ``params.start_date`` и ``params.end_date``, SDK до
        запроса проверяет формат ``YYYY-MM-DD``, порядок дат и длину периода: не
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

    async def wait_for_report(
        self,
        *,
        job_id: str,
        timeout: float = 900.0,
        poll_interval: float = 30.0,
        api_version: str | None = None,
    ) -> ReportJobItem:
        """Дождаться, когда у задачи отчёта ``available_after`` станет ``0``.

        Опрашивает бесплатный ``get_report_jobs`` и возвращает найденную задачу.
        Между запросами ждёт ``available_after`` секунд, но не меньше
        ``poll_interval``; пока задачи нет в списке — ``poll_interval``. Список
        задач общий для v1 и v2, поэтому ``job_id`` из ``order_report_v1`` тоже
        подходит. Заказ не повторяется и файл не скачивается.

        ``available_after = 0`` не гарантирует готовность файла: скачивание может
        ещё отвечать ``NotFoundError`` «Формирование отчета не завершено». В таком
        случае повторяйте скачивание с паузой, а не заказывайте отчёт заново.

        ``timeout`` — общее время ожидания в секундах, ``poll_interval`` — не
        меньше 5 секунд. Если срок вышел, выдаётся ``ReportWaitTimeoutError``.
        Ошибки ``get_report_jobs`` пробрасываются без повтора сверх политики SDK.
        """
        target_job_id = require_identifier(job_id, "job_id")
        wait_seconds = _require_positive_seconds(timeout, "timeout")
        interval = _require_positive_seconds(
            poll_interval, "poll_interval", minimum=WAIT_FOR_REPORT_MIN_POLL_INTERVAL
        )
        deadline = self.__clock.monotonic() + wait_seconds
        available_after: int | None = None
        while True:
            jobs = await self.get_report_jobs(api_version=api_version)
            job = next(
                (entry for entry in jobs.data.result or [] if entry.job_id == target_job_id),
                None,
            )
            if job is not None:
                if job.available_after <= 0:
                    return job
                available_after = job.available_after
            remaining = deadline - self.__clock.monotonic()
            if remaining <= 0:
                raise ReportWaitTimeoutError(
                    job_id=target_job_id, timeout=wait_seconds, available_after=available_after
                )
            delay = max(interval, float(job.available_after)) if job is not None else interval
            await self.__clock.sleep(min(delay, remaining))

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

        ``start`` и ``end``: даты ``YYYY-MM-DD``; период не длиннее 3 календарных
        месяцев (конец не позже той же даты через 3 месяца). Более длинный период
        сервер не отклоняет, а молча сокращает, поэтому SDK отклоняет его до
        запроса. ``report_format``: ``xlsx``, ``xml``, ``pdf`` или ``csv``. Без
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
