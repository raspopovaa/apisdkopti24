from __future__ import annotations

import os
from pathlib import Path


def _parse_value(raw_value: str) -> str:
    """Значение строки .env: кавычки снимаются, комментарий в конце строки отбрасывается."""
    value = raw_value.strip()
    if value[:1] in {"'", '"'}:
        closing = value.find(value[0], 1)
        if closing != -1:
            return value[1:closing]
    # Как в python-dotenv: у значения без кавычек « #» и всё после — комментарий.
    for index, char in enumerate(value):
        if char == "#" and (index == 0 or value[index - 1] in {" ", "\t"}):
            return value[:index].rstrip()
    return value


def load_env_file(path: str | Path = ".env", *, override: bool = False) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        # Строки вида «export KEY=value» позволяют использовать тот же файл в shell.
        if key.startswith("export ") or key.startswith("export\t"):
            key = key[len("export") :].strip()
        value = _parse_value(value)

        if override or key not in os.environ:
            os.environ[key] = value
