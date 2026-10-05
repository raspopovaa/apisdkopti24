from __future__ import annotations

import io
import logging

import httpx
import pytest

from apisdkopti24.errors import NotAuthenticatedError, ServerError, ValidationError
from apisdkopti24.response import ResponseDecoder


def test_decoder_does_not_log_sensitive_error_payload() -> None:
    stream = io.StringIO()
    package_logger = logging.getLogger("apisdkopti24")
    capture = logging.StreamHandler(stream)
    response = httpx.Response(
        400,
        request=httpx.Request("POST", "https://example.invalid/v1/users"),
        json={
            "status": {
                "code": 400,
                "errors": [
                    {
                        "type": "validationFailed",
                        "message": "password=secret-value",
                    }
                ],
            }
        },
    )

    package_logger.addHandler(capture)
    try:
        with pytest.raises(ValidationError) as exc_info:
            ResponseDecoder().decode(response, "users")
    finally:
        package_logger.removeHandler(capture)

    assert exc_info.value.get_raw_payload()["status"]["errors"][0]["message"]
    assert stream.getvalue() == ""


def test_decoder_returns_binary_success_without_text_conversion() -> None:
    decoder = ResponseDecoder()
    content = b"%PDF-test"
    response = httpx.Response(
        200,
        headers={"content-type": "application/pdf"},
        content=content,
        request=httpx.Request("GET", "https://example.invalid/report"),
    )

    assert decoder.decode_bytes(response, content, "reports/job") == content


def test_decoder_detects_api_error_in_json_download_response() -> None:
    decoder = ResponseDecoder()
    response = httpx.Response(
        200,
        headers={"content-type": "application/json"},
        json={
            "status": {
                "code": 401,
                "errors": [{"type": "notAuthenticated", "message": "Session expired"}],
            }
        },
        request=httpx.Request("GET", "https://example.invalid/report"),
    )

    with pytest.raises(NotAuthenticatedError):
        decoder.decode_bytes(response, response.content, "reports/job")


def test_decoder_never_masks_http_error_with_successful_api_status() -> None:
    decoder = ResponseDecoder()
    response = httpx.Response(
        500,
        json={"status": {"code": 200}, "data": {"unexpected": True}},
        request=httpx.Request("GET", "https://example.invalid/cards"),
    )

    with pytest.raises(ServerError) as exc_info:
        decoder.decode(response, "cards")

    assert exc_info.value.http_status_code == 500
    assert exc_info.value.api_status_code == 200


def test_decoder_never_treats_server_error_as_expired_session() -> None:
    decoder = ResponseDecoder()
    response = httpx.Response(
        500,
        json={
            "status": {
                "code": 401,
                "errors": [{"type": "notAuthenticated", "message": "Conflicting status"}],
            }
        },
        request=httpx.Request("GET", "https://example.invalid/cards"),
    )

    with pytest.raises(ServerError) as exc_info:
        decoder.decode(response, "cards")

    assert exc_info.value.status_code == 500
    assert exc_info.value.http_status_code == 500
    assert exc_info.value.api_status_code == 401


@pytest.mark.parametrize("code", [True, False])
def test_boolean_status_code_is_not_treated_as_an_api_status(code: bool) -> None:
    # bool — подкласс int; раньше true давал APIError с кодом 200 при успешном HTTP.
    response = httpx.Response(200, json={"status": {"code": code}, "data": {}})

    assert ResponseDecoder().decode(response, "cards") == {"status": {"code": code}, "data": {}}
