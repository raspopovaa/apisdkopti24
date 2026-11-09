"""Недокументированные поля из сохранённых ответов сервера разбираются в типизированные поля моделей."""

from __future__ import annotations

import json
from pathlib import Path

from apisdkopti24.models.cards import CardsListResponse
from apisdkopti24.models.contracts import ContractDataResponse
from apisdkopti24.models.dictionaries import AzsListV1Response
from apisdkopti24.models.limits import LimitsResponse
from apisdkopti24.models.reports import ReportV1JobListResponse

LIVE = Path(__file__).parent / "fixtures" / "live" / "1.1.60"


def load(name: str) -> dict[str, object]:
    return json.loads((LIVE / name).read_text(encoding="utf-8"))


def test_limit_names_are_model_fields() -> None:
    limits = LimitsResponse.model_validate(load("limits/get_limits.success.json")).data.result or []
    limit = limits[0]
    assert limit.productTypeName is not None
    assert limit.productTypeNameNormal is not None
    assert limit.sum is not None and limit.sum.currencyName is not None
    assert not limit.model_extra
    assert not limit.sum.model_extra


def test_contract_manager_and_flags_are_model_fields() -> None:
    data = ContractDataResponse.model_validate(
        load("contracts/get_contract_data.success.json")
    ).data
    assert data.manager is not None and data.manager.email is not None
    assert isinstance(data.is_best_price, bool)
    assert isinstance(data.contractData.phone_pay, bool)
    assert set(data.model_extra or {}) == {"manager_id", "parent_contract"}
    assert set(data.contractData.model_extra or {}) == {"segment"}


def test_cards_v1_and_azs_v1_and_report_jobs_fields() -> None:
    cards = (
        CardsListResponse.model_validate(load("cards/get_cards_v1.success.json")).data.result or []
    )
    card = cards[0]
    assert card.carrier is not None and card.sync_group_state is not None
    assert set(card.model_extra or {}) == {"group"}

    azs_data = AzsListV1Response.model_validate(
        load("dictionaries/get_azs_list_v1.success.json")
    ).data
    assert azs_data is not None
    azs = (azs_data.result or [])[0]
    assert azs.location is not None and azs.location.coordinates
    assert isinstance(azs.discount_flag, bool)

    jobs = ReportV1JobListResponse.model_validate(
        load("reports/get_report_job_list_v1.success.json")
    ).data
    assert jobs and isinstance(jobs[0].available_after, int) and jobs[0].contract_name
