"""Распознавание известных ответов API, у которых HTTP-код не указывает причину."""

from __future__ import annotations

import json
import logging
from typing import Any

import pytest

import apisdkopti24
from apisdkopti24.error_reporting import classify_exception
from apisdkopti24.errors import (
    KNOWN_ERROR_REASONS,
    AccessDeniedError,
    DuplicateConflictError,
    DuplicateLoginError,
    InviteNotReadyError,
    PlanNotPaidError,
    ProcessingRefusalError,
    ReportFailedError,
    ServerError,
    build_api_error,
)
from apisdkopti24.logger import RequestAuditFormatter


def _body(code: int, error_type: str, message: str) -> dict[str, Any]:
    return {"status": {"code": code, "errors": [{"type": error_type, "message": message}]}}


def _error(code: int, error_type: str, message: str, method: str = "check_purchase") -> Any:
    return build_api_error(
        status_code=code,
        body=_body(code, error_type, message),
        endpoint="/vip/v2/cards/card-id/checkPurchase",
        method_name=method,
    )


@pytest.mark.parametrize(
    ("message", "code"),
    [
        ("ОТКАЗ. Недостаточно средств. [Код ошибки: 51]", 51),
        ("ОТКАЗ. Обратитесь к персоналу торговой точки для повтора операции. [Код ошибки: 12]", 12),
        ("отказ [код ошибки:7]", 7),
    ],
)
def test_processing_refusal_exposes_numeric_code(message: str, code: int) -> None:
    error = _error(403, "accessDenied", message)

    assert type(error) is ProcessingRefusalError
    assert isinstance(error, AccessDeniedError)
    assert error.processing_code == code
    assert error.context.retryable is False


@pytest.mark.parametrize(
    "message",
    [
        "ОТКАЗ. [Код ошибки: 123456]",
        "ОТКАЗ. [Код ошибки: abc]",
        "Код ошибки: 51",
    ],
)
def test_malformed_processing_code_keeps_plain_access_denied(message: str) -> None:
    error = _error(403, "accessDenied", message)

    assert type(error) is AccessDeniedError


def test_processing_code_outside_403_is_not_a_refusal() -> None:
    error = _error(404, "notFound", "На АЗС нет рабочих терминалов [Код ошибки: 51]")

    assert not isinstance(error, ProcessingRefusalError)


def test_unpaid_api_plan_is_recognized() -> None:
    error = _error(
        403, "accessDenied", "Отказано в доступе, требуется оплатить API VIP", "get_cards_v1"
    )

    assert type(error) is PlanNotPaidError
    assert isinstance(error, AccessDeniedError)
    assert error.context.hint is not None
    assert "оплат" in error.context.hint


def test_duplicate_login_is_both_access_denied_and_duplicate() -> None:
    error = _error(
        403,
        "accessDenied",
        "Указанный логин пользователя уже существует в системе",
        "create_user",
    )

    assert type(error) is DuplicateLoginError
    assert isinstance(error, AccessDeniedError)
    assert isinstance(error, DuplicateConflictError)
    assert error.status_code == 403


def test_invite_not_ready_is_server_error_without_retry() -> None:
    error = _error(
        500,
        "internalError",
        "Приглашение не готово к отправке. Добавьте привязанные карты или укажите шаблон виртуальной карты.",
        "create_invite",
    )

    assert type(error) is InviteNotReadyError
    assert isinstance(error, ServerError)
    assert error.context.retryable is False
    assert error.context.transient is False


def test_unrecognized_messages_keep_status_classes() -> None:
    denied = _error(
        403,
        "internalError",
        "Нет доступа (Не найден контракт, карта или группа)",
        "get_card_detail",
    )
    server = _error(500, "internalError", "У нас возникли технические проблемы", "create_invite")

    assert type(denied) is AccessDeniedError
    assert type(server) is ServerError
    assert server.context.retryable is True


def test_recognition_does_not_turn_success_status_into_error_subclass() -> None:
    error = build_api_error(
        status_code=200,
        body=_body(200, "accessDenied", "требуется оплатить API VIP"),
        endpoint="/vip/v1/cards",
        http_status_code=200,
    )

    # Тип из тела даёт AccessDeniedError; распознавание уточняет и этот случай.
    assert type(error) is PlanNotPaidError


def test_recognized_errors_keep_existing_audit_codes() -> None:
    refusal = classify_exception(_error(403, "accessDenied", "ОТКАЗ. [Код ошибки: 51]"))
    duplicate = classify_exception(
        _error(
            403,
            "accessDenied",
            "Указанный логин пользователя уже существует в системе",
            "create_user",
        )
    )
    invite = classify_exception(
        _error(500, "internalError", "Приглашение не готово к отправке.", "create_invite")
    )

    assert refusal.sdk_error_code == "api_access_denied"
    assert duplicate.sdk_error_code == "api_access_denied"
    assert invite.sdk_error_code == "api_server_error"
    assert invite.transient is False
    assert invite.retry_allowed is False


def test_secret_in_refusal_text_stays_redacted() -> None:
    error = _error(403, "accessDenied", "ОТКАЗ. password=secret [Код ошибки: 51]")

    assert type(error) is ProcessingRefusalError
    assert "secret" not in str(error)
    assert all("secret" not in message for message in error.server_messages)


@pytest.mark.parametrize(
    "name",
    [
        "ProcessingRefusalError",
        "PlanNotPaidError",
        "DuplicateLoginError",
        "InviteNotReadyError",
        "ReportFailedError",
    ],
)
def test_recognized_errors_are_exported(name: str) -> None:
    assert name in apisdkopti24.__all__
    assert issubclass(getattr(apisdkopti24, name), apisdkopti24.APIError)


_REPORT_FAILED = "Произошла ошибка. Отчет не будет сформирован. Закажите новый отчет"
_TECH_PROBLEMS = (
    "У нас возникли технические проблемы. Пожалуйста, попробуйте повторить запрос позднее."
)


@pytest.mark.parametrize("method", ["download_report_file", "download_report_file_v1"])
def test_failed_report_is_not_retryable(method: str) -> None:
    error = _error(500, "internalError", _REPORT_FAILED, method)

    assert type(error) is ReportFailedError
    assert isinstance(error, ServerError)
    assert error.context.retryable is False
    assert error.context.reason == "report_failed"
    assert error.context.hint is not None
    assert "заново" in error.context.hint


def test_failed_report_text_with_yo_is_recognized() -> None:
    error = _error(500, "internalError", "Отчёт не будет сформирован", "download_report_file")

    assert type(error) is ReportFailedError


def test_move_to_card_technical_problems_is_not_retryable() -> None:
    error = _error(500, "internalError", _TECH_PROBLEMS, "move_to_card")

    assert type(error) is ServerError
    assert error.context.retryable is False
    assert error.context.reason == "transfer_failed"
    assert error.context.hint is not None
    assert "остаток" in error.context.hint


def test_technical_problems_in_other_methods_stay_retryable() -> None:
    error = _error(500, "internalError", _TECH_PROBLEMS, "remove_card_group")

    assert type(error) is ServerError
    assert error.context.retryable is True
    assert error.context.reason is None


@pytest.mark.parametrize(
    ("code", "error_type", "message", "method", "reason"),
    [
        (403, "accessDenied", "ОТКАЗ. [Код ошибки: 51]", "check_purchase", "processing_refused"),
        (403, "accessDenied", "требуется оплатить API VIP", "get_cards_v1", "plan_not_paid"),
        (
            403,
            "accessDenied",
            "Указанный логин пользователя уже существует",
            "create_user",
            "duplicate_login",
        ),
        (
            500,
            "internalError",
            "Приглашение не готово к отправке.",
            "create_invite",
            "invite_not_ready",
        ),
        (500, "internalError", _REPORT_FAILED, "download_report_file", "report_failed"),
        (500, "internalError", _TECH_PROBLEMS, "move_to_card", "transfer_failed"),
    ],
)
def test_recognized_errors_have_stable_reason(
    code: int, error_type: str, message: str, method: str, reason: str
) -> None:
    error = _error(code, error_type, message, method)

    assert error.context.reason == reason
    assert reason in KNOWN_ERROR_REASONS


def test_unrecognized_error_has_no_reason() -> None:
    error = _error(403, "accessDenied", "Нет доступа", "get_card_detail")

    assert error.context.reason is None
    assert classify_exception(error).error_reason is None


def test_audit_descriptor_carries_reason_and_processing_code() -> None:
    descriptor = classify_exception(_error(403, "accessDenied", "ОТКАЗ. [Код ошибки: 51]"))

    assert descriptor.exception_type == "ProcessingRefusalError"
    assert descriptor.error_reason == "processing_refused"
    assert descriptor.processing_code == 51


def test_audit_descriptor_ignores_unknown_reason() -> None:
    error = AccessDeniedError(403, "Доступ запрещён", reason="made_up")

    assert classify_exception(error).error_reason is None


def test_audit_log_line_contains_reason_and_processing_code() -> None:
    descriptor = classify_exception(_error(403, "accessDenied", "ОТКАЗ. [Код ошибки: 51]"))
    record = logging.LogRecord("apisdkopti24", logging.WARNING, __file__, 1, "audit", None, None)
    for key, value in {"request_audit": True, **descriptor.as_log_fields()}.items():
        setattr(record, key, value)

    payload = json.loads(RequestAuditFormatter().format(record))

    assert payload["exception_type"] == "ProcessingRefusalError"
    assert payload["error_reason"] == "processing_refused"
    assert payload["processing_code"] == 51
