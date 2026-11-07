"""Единый список проверок проекта: их запускают разработчик и CI.

Запуск всех групп: ``uv run python scripts/quality_gate.py``.
Запуск отдельных групп: ``uv run python scripts/quality_gate.py lint types``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

CODE_PATHS = ("src", "tests", "scripts", "tools", "typecheck")
CHECKS: dict[str, tuple[tuple[str, ...], ...]] = {
    "lint": (
        ("ruff", "check", *CODE_PATHS),
        ("black", "--check", *CODE_PATHS),
    ),
    "types": (
        ("mypy", "src/apisdkopti24", "typecheck", "examples/methods"),
        ("mypy", "tests"),
        ("pyright", "src/apisdkopti24"),
        ("pyright", "--verifytypes", "apisdkopti24", "--ignoreexternal"),
    ),
    "tests": (("pytest", "--cov=apisdkopti24", "--cov-branch", "--cov-report=term-missing"),),
    "contracts": (
        ("python", "scripts/verify_external_contract.py", "specifications/api-methods.yaml"),
        ("python", "scripts/verify_api_contract.py", "specifications/api-contract-v1.1.60.yaml"),
        ("python", "scripts/audit_spec_contract.py", "--mode", "verified"),
        ("python", "scripts/generate_request_metadata.py", "--check"),
        ("python", "scripts/generate_method_examples.py", "--check"),
        ("python", "scripts/export_request_models.py", "--check"),
        ("python", "scripts/export_request_matrix.py", "--check"),
        ("python", "scripts/export_model_matrix.py", "--check"),
    ),
    "docs": (
        ("python", "scripts/generate_docs.py"),
        ("mkdocs", "build", "--strict"),
    ),
}


def run_groups(groups: list[str]) -> list[str]:
    """Выполнить группы по порядку и вернуть команды, завершившиеся ошибкой."""
    failed: list[str] = []
    for group in groups:
        for check in CHECKS[group]:
            command = " ".join(check)
            print(f"==> [{group}] {command}", flush=True)
            executable = sys.executable if check[0] == "python" else check[0]
            if subprocess.run((executable, *check[1:]), check=False).returncode != 0:
                failed.append(command)
    return failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Запустить проверки качества проекта")
    parser.add_argument("groups", nargs="*", help=f"группы проверок: {', '.join(CHECKS)}")
    groups = parser.parse_args().groups or list(CHECKS)
    unknown = sorted(set(groups) - set(CHECKS))
    if unknown:
        parser.error(f"неизвестные группы: {', '.join(unknown)}")

    failed = run_groups(groups)
    for command in failed:
        print(f"Не прошла проверка: {command}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
