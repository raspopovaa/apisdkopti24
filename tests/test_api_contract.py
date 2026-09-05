from pathlib import Path

from scripts.verify_api_contract import verify_api_contract


def test_sdk_matches_api_contract_v1_1_60() -> None:
    methods, request_models = verify_api_contract(Path("specifications/api-contract-v1.1.60.yaml"))

    assert methods == 91
    assert request_models >= 1
