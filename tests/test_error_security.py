from __future__ import annotations

import io
import json
import logging
import sys
from dataclasses import asdict

import pytest
from pydantic import ValidationError as PydanticValidationError

from apisdkopti24.error_reporting import OperationAudit, classify_exception
from apisdkopti24.errors import APIError, RequestValidationError, ValidationError, build_api_error
from apisdkopti24.execution_budget import OperationBudget
from apisdkopti24.logger import RequestAuditFormatter, SafeExceptionFormatter
from apisdkopti24.models.virtual_cards import PaymentQRRequest
from apisdkopti24.registry import build_default_registry
from apisdkopti24.runtime import SystemClock
from apisdkopti24.sanitization import sanitize_for_logging, scrub
from apisdkopti24.services.transactions import TransactionsService
from apisdkopti24.session import SessionManager
from apisdkopti24.utils import validate_month_span
from tests.service_support import NoopRequestExecutor
from tests.test_executor import StubTransport, build_executor, op


@pytest.mark.parametrize(
    "message",
    [
        "pin=1234",
        "new_pin=5678",
        "bare-opaque-credential",
        "\x1b[31mprivate",
        "password=multiple secret words",
    ],
)
def test_server_messages_stay_out_of_public_diagnostics(message: str) -> None:
    body = {"status": {"code": 400, "errors": [{"type": "validationFailed", "message": message}]}}
    error = build_api_error(status_code=400, body=body, endpoint="pay")
    descriptor = classify_exception(error)
    public = str(error) + repr(error) + repr(asdict(error.context)) + repr(asdict(descriptor))
    assert message not in public
    assert error.get_raw_payload() is body
    assert error.message == "Некорректные параметры запроса"


@pytest.mark.parametrize("http_status", [200, 400])
@pytest.mark.parametrize("error_type", [{}, [], 12, True, None, "private-type-value"])
def test_malformed_error_metadata_preserves_api_failure_and_audit(
    http_status: int, error_type: object
) -> None:
    error = build_api_error(
        status_code=http_status,
        body={"status": {"code": 400, "errors": [{"type": error_type}]}},
        endpoint="cards",
    )
    assert isinstance(error, ValidationError)
    assert error.context.error_type is None
    output = io.StringIO()
    logger = logging.Logger("audit-test")
    handler = logging.StreamHandler(output)
    handler.setFormatter(RequestAuditFormatter())
    logger.addHandler(handler)
    audit = OperationAudit(
        operation=build_default_registry().get("get_cards_v2"), logger=logger, clock=SystemClock()
    )
    audit.failed(error, OperationBudget(deadline_at=100, max_attempts=1))
    event = json.loads(output.getvalue())
    assert event["event"] == "failed"
    assert event["sdk_error_code"] == "api_validation_failed"
    assert event["http_status_code"] == http_status


def test_error_messages_are_bounded_without_traversing_arbitrary_nested_values() -> None:
    body = {"status": {"code": 400, "errors": [{"message": {"pin": "1234"}}] * 10000}}
    error = build_api_error(status_code=400, body=body, endpoint="pay")
    assert len(error.context.messages) == 1
    assert len(str(error)) < 1000
    assert error.get_raw_payload() is body


@pytest.mark.parametrize("key", ["pin", "new_pin", "device_id", "security", "payment_payload"])
def test_qr_sensitive_keys_are_redacted(key: str) -> None:
    assert sanitize_for_logging({key: "1234"}) == {key: "***"}
    assert "1234" not in scrub(f"{key}=1234")


@pytest.mark.parametrize(
    "start,end",
    [("2026-07-02", "2026-07-01"), ("2026-07-01", "2026-09-01"), ("private-input", "2026-07-01")],
)
def test_date_validation_is_local_and_does_not_reflect_values(start: str, end: str) -> None:
    with pytest.raises(RequestValidationError) as caught:
        validate_month_span(start, end)
    error = caught.value
    assert not isinstance(error, APIError)
    descriptor = classify_exception(error)
    assert descriptor.sdk_error_code == "request_validation_failed"
    assert descriptor.http_status_code is None
    assert descriptor.api_status_code is None
    assert "private-input" not in str(error)
    if start == "private-input":
        assert isinstance(error.__cause__, ValueError)


def test_sdk_validation_exception_hides_input_and_formatter_omits_exception_chain() -> None:
    with pytest.raises(PydanticValidationError) as caught:
        PaymentQRRequest(pin="sensitive-invalid-pin")
    assert "sensitive-invalid-pin" not in str(caught.value)
    try:
        try:
            raise ValueError("sensitive-cause")
        except ValueError as cause:
            raise RuntimeError("sensitive-final") from cause
    except RuntimeError:
        record = logging.LogRecord(
            "test", logging.ERROR, __file__, 1, "Operation failed", (), sys.exc_info()
        )
    record.exc_text = "sensitive-cached-traceback"
    record.stack_info = "sensitive-stack"
    rendered = SafeExceptionFormatter().format(record)
    assert "sensitive" not in rendered
    assert "Operation failed" in rendered
    assert record.exc_text == "sensitive-cached-traceback"


def test_text_audit_contains_safe_reason_code_and_correlation() -> None:
    output = io.StringIO()
    logger = logging.Logger("text-audit")
    logger.addHandler(logging.StreamHandler(output))
    audit = OperationAudit(
        operation=build_default_registry().get("get_cards_v2"), logger=logger, clock=SystemClock()
    )
    audit.failed(
        ValidationError(400, "private-server-message"),
        OperationBudget(deadline_at=100, max_attempts=1),
    )
    text = output.getvalue()
    assert "sdk_error_code=api_validation_failed" in text
    assert "operation_id=" in text
    assert "Некорректные параметры запроса" in text
    assert "private-server-message" not in text


def test_logging_handler_failure_does_not_replace_operation_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class BrokenHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            raise RuntimeError("private-handler-error")

    logger = logging.Logger("broken-audit")
    logger.addHandler(BrokenHandler())
    audit = OperationAudit(
        operation=build_default_registry().get("get_cards_v2"), logger=logger, clock=SystemClock()
    )
    error = ValidationError(400, "private-response")
    audit.start()
    audit.failed(error, OperationBudget(deadline_at=100, max_attempts=1))
    assert audit.logging_failed
    assert "private" not in caplog.text


def test_classifier_failure_still_emits_one_terminal_event(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken_classifier(*args: object, **kwargs: object) -> object:
        raise TypeError("private-classifier-error")

    monkeypatch.setattr("apisdkopti24.error_reporting.classify_exception", broken_classifier)
    output = io.StringIO()
    logger = logging.Logger("fallback-audit")
    handler = logging.StreamHandler(output)
    handler.setFormatter(RequestAuditFormatter())
    logger.addHandler(handler)
    audit = OperationAudit(
        operation=build_default_registry().get("get_cards_v2"), logger=logger, clock=SystemClock()
    )
    budget = OperationBudget(deadline_at=100, max_attempts=1)
    audit.failed(ValueError("private-original"), budget)
    audit.failed(ValueError("private-second"), budget)
    assert len(output.getvalue().splitlines()) == 1
    event = json.loads(output.getvalue())
    assert event["sdk_error_code"] == "sdk_internal_error"
    assert "private" not in output.getvalue()


@pytest.mark.asyncio
async def test_invalid_period_never_authenticates_or_sends_request() -> None:
    class ForbiddenSessionGate:
        async def ensure_authenticated(self) -> str:
            raise AssertionError("Некорректные входные данные не должны запускать авторизацию")

    service = TransactionsService(
        request_executor=NoopRequestExecutor(),
        session_context=SessionManager(),
        session_gate=ForbiddenSessionGate(),
        logger=logging.Logger("period-test"),
    )
    with pytest.raises(RequestValidationError):
        await service.get_transactions_v2(date_from="2026-07-02", date_to="2026-07-01")


@pytest.mark.asyncio
async def test_executor_preserves_original_exception_when_audit_handler_fails() -> None:
    class BrokenAuditHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            if getattr(record, "request_audit", False):
                raise RuntimeError("private-audit-failure")

    logger = logging.Logger("executor-audit-failure")
    logger.addHandler(BrokenAuditHandler())
    original = ValidationError(400, "original-error")
    executor, _ = build_executor(StubTransport(original), logger=logger)
    with pytest.raises(ValidationError) as caught:
        await executor.execute(op("get_cards_v2"))
    assert caught.value is original


def test_context_transient_does_not_authorize_mutation_retry() -> None:
    error = build_api_error(status_code=500, body="private", endpoint="users")
    assert error.context.transient is True
    assert error.context.retryable is True
    descriptor = classify_exception(error, build_default_registry().get("create_user"))
    assert descriptor.transient is True
    assert descriptor.retry_allowed is False
