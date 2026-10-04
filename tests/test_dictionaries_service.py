"""Справочники и АЗС: проверки параметров до входа и запроса."""

import logging
from typing import Any

import pytest

from apisdkopti24.errors import RequestValidationError
from apisdkopti24.services.dictionaries import DictionariesService
from apisdkopti24.session import SessionManager
from tests.service_support import RecordingRequestExecutor


class _CountingGate:
    def __init__(self) -> None:
        self.calls = 0

    async def ensure_authenticated(self) -> str:
        self.calls += 1
        return "session-id"


def _service(
    responses: dict[str, dict[str, Any]] | None = None,
) -> tuple[DictionariesService, RecordingRequestExecutor, _CountingGate]:
    executor = RecordingRequestExecutor(responses or {})
    gate = _CountingGate()
    service = DictionariesService(
        executor, SessionManager(), gate, logging.getLogger("dictionaries-test")
    )
    return service, executor, gate


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "paging",
    [{"page": 1}, {"on_page": 1000}],
    ids=["page-only", "on-page-only"],
)
async def test_azs_v2_requires_page_and_on_page_together(paging: dict[str, int]) -> None:
    service, executor, gate = _service()

    with pytest.raises(RequestValidationError, match="page и on_page"):
        await service.get_azs_list_v2(**paging)

    assert gate.calls == 0
    assert executor.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("paging", [{}, {"page": 2, "on_page": 1000}], ids=["none", "both"])
async def test_azs_v2_accepts_both_or_no_paging_parameters(paging: dict[str, int]) -> None:
    response = {"status": {"code": 200}, "data": {"total_count": 0, "result": []}}
    service, executor, _ = _service({"get_azs_list_v2": response})

    await service.get_azs_list_v2(**paging)

    assert executor.calls[0][1]["query"] == (paging or None)


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["", "  "])
async def test_get_dictionary_rejects_empty_name_before_login(name: str) -> None:
    service, executor, gate = _service()

    with pytest.raises(RequestValidationError, match="name"):
        await service.get_dictionary(name=name)

    assert gate.calls == 0
    assert executor.calls == []
