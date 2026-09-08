from dataclasses import asdict

from apisdkopti24.errors import (
    DuplicateConflictError,
    NotAuthenticatedError,
    RateLimitError,
    ValidationError,
    build_api_error,
)


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
