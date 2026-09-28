"""Ошибка модели ответа превращается в типизированное исключение SDK без значений из ответа."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError as PydanticValidationError

from apisdkopti24 import ResponseValidationError
from apisdkopti24.error_reporting import classify_exception
from apisdkopti24.executor import OperationExecutor
from apisdkopti24.modeling import BaseModel
from apisdkopti24.registry import build_default_registry

REGISTRY = build_default_registry()


def cards_v1_payload(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": {"code": 200},
        "data": {"total_count": 1, "result": [card]},
        "timestamp": 1,
    }


def test_response_model_mismatch_raises_typed_single_line_error() -> None:
    payload = cards_v1_payload({"id": "card-id", "number": "7000000000000000"})

    with pytest.raises(ResponseValidationError) as caught:
        OperationExecutor.decode_response(REGISTRY.get("get_cards_v1"), payload)

    error = caught.value
    text = str(error)
    assert isinstance(error, ValueError)
    assert isinstance(error.__cause__, PydanticValidationError)
    assert error.operation == "get_cards_v1"
    assert error.model_name == "CardsListResponse"
    assert ("data.result.0.contract_id", "missing") in error.problems
    assert error.problem_count == len(error.problems)
    assert "\n" not in text and "\r" not in text
    assert "7000000000000000" not in text
    assert "и ещё" in text


def test_response_validation_error_hides_values_and_bounds_server_keys() -> None:
    class Payload(BaseModel):
        counters: dict[str, int]

    hostile_key = "line\r\nbreak owner@example.org " + "x" * 500
    try:
        Payload.model_validate({"counters": {hostile_key: "secret-value"}})
    except PydanticValidationError as exc:
        error = ResponseValidationError.from_pydantic(
            exc, operation="get_example", model_name="Payload"
        )
    else:  # pragma: no cover - пример намеренно нарушает модель
        raise AssertionError("Модель должна отклонить значение")

    text = str(error)
    location, kind = error.problems[0]
    assert "secret-value" not in text
    assert "owner@example.org" not in text
    assert "\n" not in text and "\r" not in text
    assert len(location) <= 120
    assert kind == "int_parsing"


def test_response_validation_error_limits_stored_problems() -> None:
    class Payload(BaseModel):
        values: list[int]

    try:
        Payload.model_validate({"values": ["bad"] * 500})
    except PydanticValidationError as exc:
        error = ResponseValidationError.from_pydantic(exc, operation="op", model_name="Payload")
    else:  # pragma: no cover - пример намеренно нарушает модель
        raise AssertionError("Модель должна отклонить значения")

    assert error.problem_count == 500
    assert len(error.problems) == 50
    assert "и ещё 497" in str(error)
    assert len(str(error)) < 300


def test_response_validation_error_is_classified_for_audit() -> None:
    payload = cards_v1_payload({"id": "card-id"})
    try:
        OperationExecutor.decode_response(REGISTRY.get("get_cards_v1"), payload)
    except ResponseValidationError as error:
        descriptor = classify_exception(error, REGISTRY.get("get_cards_v1"))
    else:  # pragma: no cover - пример намеренно нарушает модель
        raise AssertionError("Ответ должен нарушать модель")

    assert descriptor.sdk_error_code == "response_validation_failed"
    assert descriptor.error_source == "response"
