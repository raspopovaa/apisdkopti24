from api_client_opti24.utils import sanitize_for_logging, scrub, to_json_param


def test_sanitize_for_logging_redacts_sensitive_keys():
    sanitized = sanitize_for_logging(
        {
            "api_key": "super-secret",
            "nested": {"password": "very-secret", "plain": "ok"},
            "items": [{"session_id": "SESSION-1"}],
            "card_id": "CARD-1",
        }
    )

    assert sanitized["api_key"] == "***"
    assert sanitized["nested"]["password"] == "***"
    assert sanitized["nested"]["plain"] == "ok"
    assert sanitized["items"][0]["session_id"] == "***"
    assert sanitized["card_id"] == "***"


def test_scrub_redacts_inline_sensitive_values():
    text = "mobile=79999999999 email=test@example.com password=hunter2"

    scrubbed = scrub(text)

    assert "79999999999" not in scrubbed
    assert "test@example.com" not in scrubbed
    assert "hunter2" not in scrubbed


def test_to_json_param_preserves_json_format():
    payload = {"role": "Driver", "flags": [True, False]}

    serialized = to_json_param(payload)

    assert serialized == '{"role":"Driver","flags":[true,false]}'
