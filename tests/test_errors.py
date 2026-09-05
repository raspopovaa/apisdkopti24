from api_client_opti24.errors import (
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
    assert exc.context.raw_payload == body
    assert exc.context.messages == ("Invalid contract_id",)


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
