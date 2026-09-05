from __future__ import annotations

import json
from pathlib import Path

from tools.spec_contract.loader import load_catalog
from tools.spec_contract.sanitizer import find_sensitive_values, scan_text_file

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"


def test_spec_fixtures_are_valid_json_and_anonymized():
    catalog = load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)
    fixture_paths = {
        variant.fixture
        for operation in catalog.iter_operations()
        for variant in operation.variants
        if variant.fixture is not None
    }
    assert len(fixture_paths) >= 75

    for fixture_path in fixture_paths:
        assert fixture_path is not None
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        assert find_sensitive_values(payload) == []
        assert scan_text_file(fixture_path) == []


def test_corrected_fixture_does_not_hide_source_correction():
    catalog = load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)
    operation = catalog.operations["get_final_prices"]
    variant = operation.variants[0]

    assert variant.fixture is not None
    payload = json.loads(variant.fixture.read_text(encoding="utf-8"))
    assert "goods" in payload["data"]
    assert "gooods" not in payload["data"]
    assert any(correction["path"] == "data.gooods" for correction in variant.fixture_corrections)
