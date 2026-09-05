from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for path in (PROJECT_ROOT, SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools.spec_contract import audit_catalog, load_catalog, write_reports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit API 1.1.60 contracts against SDK models")
    parser.add_argument(
        "--contract-root",
        type=Path,
        default=PROJECT_ROOT / "specifications" / "contracts" / "1.1.60",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "contract-audit",
    )
    parser.add_argument(
        "--mode",
        choices=("audit", "verified"),
        default="audit",
        help="audit always reports; verified fails on blocking findings",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = load_catalog(args.contract_root, repository_root=PROJECT_ROOT)
    result = audit_catalog(catalog)
    markdown_path, json_path = write_reports(result, args.output_dir)
    summary = result.summary()
    print("Contract audit: " + ", ".join(f"{name}={value}" for name, value in summary.items()))
    print(f"Markdown report: {markdown_path}")
    print(f"JSON report: {json_path}")
    infrastructure_codes = {
        "runtime_operation_not_normalized",
        "normalized_operation_not_in_runtime",
        "runtime_registry_unavailable",
        "service_method_unavailable",
        "fixture_missing",
        "fixture_invalid_json",
        "fixture_sensitive_value",
        "request_model_unavailable",
    }
    if any(issue.code in infrastructure_codes for issue in result.issues):
        return 1
    if args.mode == "verified" and result.has_blocking_issues:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
