from pathlib import Path

from scripts.generate_request_metadata import OUTPUT, SOURCE, render_request_metadata


def test_runtime_request_metadata_matches_normalized_source() -> None:
    assert OUTPUT.read_text(encoding="utf-8") == render_request_metadata(SOURCE)


def test_normalized_request_metadata_is_not_a_test_fixture() -> None:
    assert Path("specifications/request-matrix-v1.1.60.json").resolve() == SOURCE
