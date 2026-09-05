from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .models import AuditResult


def render_markdown(result: AuditResult) -> str:
    summary = result.summary()
    lines = [
        "# API 1.1.60 contract audit",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        *[f"| {name} | {value} |" for name, value in summary.items()],
        "",
    ]
    by_code = Counter(issue.code for issue in result.issues)
    lines.extend(
        [
            "## Findings by code",
            "",
            "| Code | Count |",
            "|---|---:|",
            *[f"| `{code}` | {count} |" for code, count in sorted(by_code.items())],
            "",
        ]
    )
    grouped: dict[str, list] = defaultdict(list)
    for issue in result.issues:
        grouped[issue.operation or "repository"].append(issue)
    lines.extend(["## Details", ""])
    for operation in sorted(grouped):
        lines.extend([f"### `{operation}`", ""])
        for issue in grouped[operation]:
            marker = "BLOCKING" if issue.blocking else issue.severity.upper()
            location = f" `{issue.path}`" if issue.path else ""
            details = []
            if issue.expected is not None:
                details.append(f"expected={issue.expected}")
            if issue.actual is not None:
                details.append(f"actual={issue.actual}")
            suffix = f" ({'; '.join(details)})" if details else ""
            lines.append(f"- **{marker}** `{issue.code}`{location}: {issue.message}{suffix}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_reports(result: AuditResult, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "spec-contract-report.md"
    json_path = output_dir / "spec-contract-report.json"
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "summary": result.summary(),
                "issues": [issue.as_dict() for issue in result.issues],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return markdown_path, json_path
