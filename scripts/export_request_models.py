from __future__ import annotations

import json
from pathlib import Path

from verify_api_contract import _request_models

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "specifications" / "request-models-v1.1.60.json"


def main() -> None:
    models = _request_models()
    OUTPUT.write_text(
        json.dumps(models, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Exported {len(models)} request models to {OUTPUT}")


if __name__ == "__main__":
    main()
