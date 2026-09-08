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
    assert "permissions" not in jobs["build"]
    assert jobs["deploy"]["permissions"] == {
        "contents": "read",
        "pages": "write",
        "id-token": "write",
    }
