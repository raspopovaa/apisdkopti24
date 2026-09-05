from __future__ import annotations

import json
from pathlib import Path

from tools.spec_contract import audit_catalog, load_catalog, write_reports

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"


def test_full_audit_generates_machine_and_human_readable_reports(tmp_path):
    catalog = load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)
    result = audit_catalog(catalog)
    markdown_path, json_path = write_reports(result, tmp_path)

    assert result.operation_count == 82
    assert result.verified_count == 3
    assert result.fixture_count >= 75
    assert markdown_path.exists()
    assert json_path.exists()

    markdown = markdown_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert "API 1.1.60 contract audit" in markdown
    assert payload["summary"]["operations"] == 82
    assert isinstance(payload["issues"], list)


def test_verified_contracts_have_no_blocking_findings():
    catalog = load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)
    result = audit_catalog(catalog)

    blocking_verified = [
        issue
        for issue in result.blocking_issues
        if issue.operation
        and catalog.operations.get(issue.operation)
        and catalog.operations[issue.operation].verification == "verified"
    ]
    assert blocking_verified == []
