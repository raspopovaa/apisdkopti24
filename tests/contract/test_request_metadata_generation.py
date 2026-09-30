from pathlib import Path

from scripts.generate_request_metadata import (
    ENDPOINTS,
    REQUESTS,
    SOURCE,
    render_endpoints,
    render_request_metadata,
)


def test_runtime_request_metadata_matches_normalized_source() -> None:
    assert REQUESTS.read_text(encoding="utf-8") == render_request_metadata(SOURCE)
    endpoints = ENDPOINTS.read_text(encoding="utf-8")
    assert endpoints == render_endpoints(endpoints, SOURCE)


def test_normalized_operation_metadata_is_not_a_test_fixture() -> None:
    assert Path("specifications/operation-catalog.json").resolve() == SOURCE
