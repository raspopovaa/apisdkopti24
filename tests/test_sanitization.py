import secrets

import pytest

from apisdkopti24.sanitization import REDACTED, sanitize_for_logging

_VALUE = secrets.token_hex(4)


def test_exception_is_replaced_without_its_message() -> None:
    sanitized = sanitize_for_logging(ValueError(f"api_key={_VALUE}"))

    assert _VALUE not in sanitized
    assert sanitized == "[подробности исключения скрыты]"


@pytest.mark.parametrize("value", [(f"token={_VALUE}", "ok"), {f"token={_VALUE}", "ok"}])
def test_collection_type_is_kept_and_items_are_scrubbed(value: tuple[str, ...] | set[str]) -> None:
    sanitized = sanitize_for_logging(value)

    assert type(sanitized) is type(value)
    assert set(sanitized) == {f"token={REDACTED}", "ok"}


def test_nested_sensitive_keys_are_redacted() -> None:
    sanitized = sanitize_for_logging({"data": [{"card_id": "1-ABC", "amount": 10}]})

    assert sanitized == {"data": [{"card_id": REDACTED, "amount": 10}]}
