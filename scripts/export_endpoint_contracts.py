from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from api_client_opti24.contracts import serialize_registry_contract
from api_client_opti24.registry import build_default_registry


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the endpoint contract snapshot")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    contract = serialize_registry_contract(build_default_registry())
    args.output.write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
