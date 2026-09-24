import json
import logging
from dataclasses import asdict

import httpx
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError as PydanticValidationError

from apisdkopti24.error_reporting import classify_exception
from apisdkopti24.errors import (
    DuplicateConflictError,
    NotAuthenticatedError,
    RateLimitError,
    ResponseShapeError,
    ResponseTooLargeError,
    ValidationError,
    build_api_error,
)
from apisdkopti24.logger import RequestAuditFormatter
from apisdkopti24.registry import build_default_registry


def test_build_api_error_preserves_raw_payload_and_error_type():
    body = {
        "status": {
            "code": 400,
            "errors": [
                {
                    "type": "validationFailed",
                    "message": "Invalid contract_id",
                }
            ],
        }
    }

    exc = build_api_error(status_code=400, body=body, endpoint="cards")

    assert isinstance(exc, ValidationError)
    assert exc.context.error_type == "validationFailed"
    assert exc.get_raw_payload() == body
    assert exc.context.messages == ("API error response contained sensitive data",)


def test_build_api_error_maps_auth_errors():
    body = {
        "status": {
            "code": 401,
            "errors": [
                {
                    "type": "notAuthenticated",
                    "message": "Необходима авторизация",
                }
            ],
        }
    }

    exc = build_api_error(status_code=401, body=body, endpoint="info")

    assert isinstance(exc, NotAuthenticatedError)
    assert exc.context.messages == ("Необходима авторизация",)


def test_build_api_error_collects_multiple_messages_and_hint():
    body = {
        "status": {
            "code": 409,
            "errors": [
                {"type": "duplicateConflict", "message": "Duplicate request"},
                {"type": "duplicateConflict", "message": ["Duplicate request", "Retry later"]},
            ],
        }
    }

    exc = build_api_error(status_code=409, body=body, endpoint="cards")

    assert isinstance(exc, DuplicateConflictError)
    assert exc.context.messages == ("Duplicate request", "Retry later")
    assert exc.context.hint is not None
    assert exc.context.retryable is False


def test_build_api_error_uses_payload_status_code_when_http_code_is_200():
    body = {
        "status": {
            "code": 401,
            "errors": [
                {
                    "type": "notAuthenticated",
                    "message": "Session expired",
                }
            ],
        }
    }

    exc = build_api_error(
        status_code=401,
        http_status_code=200,
        body=body,
        endpoint="info",
    )

    assert isinstance(exc, NotAuthenticatedError)
    assert exc.status_code == 401
    assert exc.http_status_code == 200
    assert exc.api_status_code == 401


def test_build_api_error_maps_rate_limit_errors():
    exc = build_api_error(
        status_code=509,
        body="rate limited",
        endpoint="transactions",
    )

    assert isinstance(exc, RateLimitError)
    assert exc.context.retryable is True


def test_api_error_string_does_not_expose_endpoint_identifier() -> None:
    secret_card_id = "secret-card-identifier"
    exc = build_api_error(
        status_code=404,
        body={"status": {"code": 404}},
        endpoint=f"cards/{secret_card_id}/drivers",
        method_name="get_card_drivers",
    )

    assert secret_card_id not in str(exc)
    assert secret_card_id not in repr(exc.context)
    assert "get_card_drivers" in str(exc)


def test_api_error_string_scrubs_reflected_secrets_and_control_characters() -> None:
    reflected_secret = "secret@example.com"
    exc = build_api_error(
        status_code=400,
        body={
            "status": {
                "code": 400,
                "errors": [
                    {
                        "type": "validationFailed",
                        "message": f"email={reflected_secret}\r\nforged-log-entry",
                    }
                ],
            }
        },
        endpoint="users",
        method_name="create_user",
    )

    rendered = str(exc)
    assert reflected_secret not in rendered
    assert "\r" not in rendered
    assert "\n" not in rendered


def test_api_error_string_is_bounded_but_raw_context_is_preserved() -> None:
    raw_message = "x" * 10_000
    body = {"status": {"code": 500, "message": raw_message}}

    exc = build_api_error(status_code=500, body=body, endpoint="reports")

    assert len(str(exc)) < 1_000
    assert exc.get_raw_payload() == body
    assert not hasattr(exc, "body")


def test_api_error_context_does_not_expose_raw_payload_through_repr_or_asdict() -> None:
    secret = "raw-secret-value"
    body = {"status": {"code": 500}, "secret": secret}

    exc = build_api_error(status_code=500, body=body, endpoint="reports")

    assert secret not in repr(exc.context)
    assert secret not in repr(asdict(exc.context))
    assert exc.get_raw_payload() == body


def test_api_error_string_rejects_unquoted_multiword_sensitive_values() -> None:
    exc = build_api_error(
        status_code=400,
        body={
            "status": {
                "code": 400,
                "errors": [
                    {
                        "type": "validationFailed",
                        "message": "password=very secret value",
                    }
                ],
            }
        },
        endpoint="authUser",
    )

    rendered = str(exc)
    assert "very" not in rendered
    assert "secret" not in rendered
    assert "value" not in rendered


def test_error_classifier_does_not_expose_network_url_or_file_path() -> None:
    request = httpx.Request("GET", "https://api.example.test/cards?session_id=secret-session")
    network_error = httpx.ReadTimeout("secret network details", request=request)
    file_error = PermissionError("/private/contracts/secret-contract/report.xlsx")

    network = classify_exception(network_error)
    filesystem = classify_exception(file_error)

    assert network.sdk_error_code == "network_timeout"
    assert "secret" not in network.error_message
    assert "api.example.test" not in network.error_message
    assert filesystem.sdk_error_code == "filesystem_error"
    assert "secret-contract" not in filesystem.error_message


def test_error_classifier_does_not_expose_pydantic_input() -> None:
    class Response(PydanticBaseModel):
        count: int

    try:
        Response.model_validate({"count": "secret-input"})
    except PydanticValidationError as error:
        descriptor = classify_exception(error)
    else:  # pragma: no cover - the fixture intentionally violates the model
        raise AssertionError("Pydantic fixture must fail validation")

    assert descriptor.sdk_error_code == "response_validation_failed"
    assert "secret-input" not in descriptor.error_message


def test_error_classifier_allows_retry_only_for_operation_policy() -> None:
    request = httpx.Request("POST", "https://api.example.test/resource")
    timeout = httpx.ReadTimeout("timed out", request=request)
    registry = build_default_registry()

    safe = classify_exception(timeout, registry.get("get_cards_v2"))
    mutation = classify_exception(timeout, registry.get("create_user"))

    assert safe.transient is True
    assert safe.retry_allowed is True
    assert mutation.transient is True
    assert mutation.retry_allowed is False
    assert mutation.retryable is False


def test_error_classifier_distinguishes_response_failures_from_input_validation() -> None:
    oversized = classify_exception(ResponseTooLargeError(maximum_bytes=1024))
    malformed = classify_exception(ResponseShapeError("unexpected payload"))
    programming_error = classify_exception(TypeError("internal mismatch"))

    assert oversized.sdk_error_code == "response_too_large"
    assert oversized.error_source == "response"
    assert malformed.sdk_error_code == "response_shape_invalid"
    assert programming_error.sdk_error_code == "sdk_internal_error"


def test_error_classifier_bounds_server_error_type() -> None:
    error = ValidationError(
        400,
        "invalid request",
        error_type="bad\r\n" + "x" * 1_000,
    )

    descriptor = classify_exception(error)

    assert descriptor.api_error_type is not None
    assert "\r" not in descriptor.api_error_type
    assert "\n" not in descriptor.api_error_type
    assert len(descriptor.api_error_type) <= 200


def test_request_audit_formatter_serializes_safe_error_fields() -> None:
    record = logging.LogRecord(
        "test",
        logging.ERROR,
        __file__,
        1,
        "API request audit",
        (),
        None,
    )
    record.request_audit = True
    record.event = "failed"
    record.operation = "auth_user"
    record.sdk_error_code = "operation_timeout"
    record.error_source = "sdk"
    record.exception_type = "OperationTimeoutError"
    record.error_message = "Превышен общий лимит времени операции"
    record.transient = True
    record.retry_allowed = True
    record.retryable = True
    record.http_status_code = None
    record.api_status_code = None
    record.api_error_type = None

    payload = json.loads(RequestAuditFormatter().format(record))

    assert payload["sdk_error_code"] == "operation_timeout"
    assert payload["error_message"] == "Превышен общий лимит времени операции"
    assert payload["transient"] is True
    assert payload["retry_allowed"] is True
    assert payload["http_status_code"] is None
    assert payload["api_status_code"] is None
