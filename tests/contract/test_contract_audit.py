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
    assert result.verified_count == 64
    assert result.fixture_count >= 75
    assert markdown_path.exists()
    assert json_path.exists()

    markdown = markdown_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert "Аудит контрактов API 1.1.60" in markdown
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


def test_sdk_path_mapping_resolves_arguments_model_fields_and_credentials():
    from tools.spec_contract.comparator import _sdk_path_resolves
    from tools.spec_contract.runtime import resolve_service_method

    set_limit = resolve_service_method("limits", "set_limit")
    create_invite = resolve_service_method("invites", "create_invite")
    auth_user = resolve_service_method("auth", "auth_user")

    assert _sdk_path_resolves(set_limit, "limits")
    assert _sdk_path_resolves(set_limit, "limits[].productGroup")
    assert _sdk_path_resolves(set_limit, "limits[].term.time.from")
    assert _sdk_path_resolves(create_invite, "data.contracts[].template_id")
    assert _sdk_path_resolves(auth_user, "@credentials.login")

    assert not _sdk_path_resolves(set_limit, "limit")
    assert not _sdk_path_resolves(set_limit, "limits[].term.time.number")
    assert not _sdk_path_resolves(auth_user, "@credentials.api_key")


def test_every_request_parameter_is_mapped_to_the_sdk():
    catalog = load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)
    result = audit_catalog(catalog)

    codes = {issue.code for issue in result.issues}
    assert "request_parameter_mapping_missing" not in codes
    assert "request_parameter_mapping_invalid" not in codes
