import re
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"
IMMUTABLE_ACTION = re.compile(r"^\s*uses:\s*[^\s]+@(?P<revision>[0-9a-f]{40})(?:\s+#\s+.+)?\s*$")


def _workflow(name: str) -> dict[str, object]:
    return yaml.safe_load((WORKFLOW_ROOT / name).read_text(encoding="utf-8"))


def test_third_party_actions_are_pinned_to_full_commit_sha() -> None:
    unpinned: list[str] = []
    for workflow_path in sorted(WORKFLOW_ROOT.glob("*.yml")):
        for line_number, line in enumerate(
            workflow_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if "uses:" in line and not IMMUTABLE_ACTION.match(line):
                unpinned.append(f"{workflow_path.name}:{line_number}: {line.strip()}")

    assert unpinned == []


def test_pages_workflow_grants_privileges_only_to_jobs_that_need_them() -> None:
    workflow = _workflow("pages.yml")

    assert workflow["permissions"] == {"contents": "read"}
    jobs = workflow["jobs"]
    assert jobs["build"]["permissions"] == {"contents": "write"}
    assert jobs["deploy"]["permissions"] == {
        "contents": "read",
        "pages": "write",
        "id-token": "write",
    }


def test_python_workflows_use_frozen_uv_lock() -> None:
    for name in ("ci.yml", "docs.yml", "pages.yml", "testpypi.yml"):
        content = (WORKFLOW_ROOT / name).read_text(encoding="utf-8")
        assert "uv sync --frozen" in content


def test_ci_audits_runtime_dependencies() -> None:
    content = (WORKFLOW_ROOT / "ci.yml").read_text(encoding="utf-8")
    assert 'pip-audit==2.9.0' in content
    assert "pip-audit -r requirements-audit.txt" in content


def test_package_publication_is_manual_only() -> None:
    workflow = _workflow("testpypi.yml")

    assert workflow[True] == {"workflow_dispatch": None}
    assert "pull_request" not in workflow[True]
    assert workflow["jobs"]["build"]["if"] == "github.ref == 'refs/heads/main'"
    assert workflow["jobs"]["publish"]["if"] == "github.ref == 'refs/heads/main'"
    assert workflow["jobs"]["smoke-test"]["if"] == "github.ref == 'refs/heads/main'"
    assert workflow["jobs"]["publish-pypi"]["if"] == "github.ref == 'refs/heads/main'"
    checkout = workflow["jobs"]["build"]["steps"][0]
    assert checkout["with"]["ref"] == "${{ github.sha }}"


def test_pypi_promotes_the_testpypi_artifact_without_rebuilding() -> None:
    workflow = _workflow("testpypi.yml")
    jobs = workflow["jobs"]

    assert jobs["smoke-test"]["needs"] == "publish"
    assert jobs["publish-pypi"]["needs"] == "smoke-test"
    publish_steps = jobs["publish-pypi"]["steps"]
    assert publish_steps[0]["with"]["name"] == "python-package-distributions"
    assert all("build" not in str(step.get("run", "")) for step in publish_steps)
