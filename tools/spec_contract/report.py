from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .models import AuditResult


def render_markdown(result: AuditResult) -> str:
    summary = result.summary()
    lines = [
        "# Аудит контрактов API 1.1.60",
        "",
        "## Сводка",
        "",
        "| Показатель | Значение |",
        "|---|---:|",
        *[f"| {name} | {value} |" for name, value in summary.items()],
        "",
    ]
    by_code = Counter(issue.code for issue in result.issues)
    lines.extend(
        [
            "## Замечания по коду",
            "",
            "| Код | Количество |",
            "|---|---:|",
            *[f"| `{code}` | {count} |" for code, count in sorted(by_code.items())],
            "",
        ]
    )
    grouped: dict[str, list] = defaultdict(list)
    for issue in result.issues:
        grouped[issue.operation or "repository"].append(issue)
    lines.extend(["## Подробности", ""])
    for operation in sorted(grouped):
        lines.extend([f"### `{operation}`", ""])
        for issue in grouped[operation]:
            marker = (
                "БЛОКИРУЕТ"
                if issue.blocking
                else {"error": "ОШИБКА", "warning": "ПРЕДУПРЕЖДЕНИЕ", "info": "ИНФОРМАЦИЯ"}[
                    issue.severity
                ]
            )
            location = f" `{issue.path}`" if issue.path else ""
            details = []
            if issue.expected is not None:
                details.append(f"ожидалось={issue.expected}")
            if issue.actual is not None:
                details.append(f"получено={issue.actual}")
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
