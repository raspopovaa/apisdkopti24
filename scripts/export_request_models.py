from __future__ import annotations

import json
from pathlib import Path

from export_files import parse_check_flag, write_or_check
from verify_api_contract import _request_models

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "specifications" / "request-models-v1.1.60.json"


def main() -> None:
    check = parse_check_flag("Экспортировать каталог моделей запросов")
    models = _request_models()
    content = json.dumps(models, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    write_or_check({OUTPUT: content}, check=check)
    action = "Актуален каталог" if check else "Экспортировано"
    print(f"{action} {len(models)} моделей запросов: {OUTPUT}")


if __name__ == "__main__":
    main()
