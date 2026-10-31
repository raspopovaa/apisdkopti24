from __future__ import annotations

import logging
from typing import Any, TypeVar

import pytest
from pydantic import ValidationError as PydanticValidationError

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.models.cards import CardsV2Query
from apisdkopti24.service_base import _BaseService
from apisdkopti24.services.cards import CardsService
from apisdkopti24.services.templates import TemplatesService
from apisdkopti24.session import SessionManager
from tests.service_support import RecordingRequestExecutor, StubSessionGate

ServiceT = TypeVar("ServiceT", bound=_BaseService)


def _service(service_type: type[ServiceT], executor: RecordingRequestExecutor) -> ServiceT:
    session = SessionManager()
    session.restore(session_id="session-1", contract_id="contract-1")
    factory: Any = service_type
    return factory(
        executor, session, StubSessionGate(), logging.getLogger("request-validation-test")
    )


@pytest.mark.asyncio
async def test_service_method_wraps_pydantic_error_into_request_validation_error() -> None:
    executor = RecordingRequestExecutor({})
    cards = _service(CardsService, executor)

    with pytest.raises(RequestValidationError, match="page") as caught:
        await cards.get_cards_v2(page=0)

    assert isinstance(caught.value.__cause__, PydanticValidationError)
    assert executor.calls == []


@pytest.mark.asyncio
async def test_iterator_wraps_pydantic_error_before_first_request() -> None:
    executor = RecordingRequestExecutor({})
    cards = _service(CardsService, executor)

    with pytest.raises(RequestValidationError, match="sort"):
        _ = [card async for card in cards.iter_cards_v2(sort="")]

    assert executor.calls == []


@pytest.mark.asyncio
async def test_request_validation_message_omits_rejected_value() -> None:
    secret_name = "секретное-имя-" + "x" * 300
    templates = _service(TemplatesService, RecordingRequestExecutor({}))

    with pytest.raises(RequestValidationError) as caught:
        await templates.create_template_limit(
            template_id="template-1",
            payload={"unexpected": secret_name},
        )

    assert secret_name not in str(caught.value)
    assert "\n" not in str(caught.value)


@pytest.mark.asyncio
async def test_response_model_errors_are_not_reported_as_request_errors() -> None:
    executor = RecordingRequestExecutor({"get_cards_v2": {"status": {"code": 200}}})
    cards = _service(CardsService, executor)

    with pytest.raises(PydanticValidationError):
        await cards.get_cards_v2(page=1)


def test_dto_constructed_directly_keeps_pydantic_error() -> None:
    with pytest.raises(PydanticValidationError):
        CardsV2Query(contract_id="contract-1", page=0)
