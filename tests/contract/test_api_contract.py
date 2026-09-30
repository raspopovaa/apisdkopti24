import json
from pathlib import Path

from scripts.verify_api_contract import _request_models, verify_api_contract


def test_sdk_matches_api_contract_v1_1_60() -> None:
    methods, request_models = verify_api_contract(Path("specifications/api-contract-v1.1.60.yaml"))

    assert methods == 91
    assert request_models >= 1


def test_generated_request_model_catalog_is_current() -> None:
    path = Path("specifications/request-models-v1.1.60.json")
    assert json.loads(path.read_text(encoding="utf-8")) == _request_models()
