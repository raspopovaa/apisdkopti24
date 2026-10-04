"""Запись или проверка экспортированных файлов спецификаций."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path


def parse_check_flag(description: str) -> bool:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Не записывать файлы, а завершиться ошибкой, если они устарели.",
    )
    return bool(parser.parse_args().check)


def write_or_check(outputs: Mapping[Path, str], *, check: bool) -> None:
    """Записать файлы или, с ``check``, сравнить их с сохранёнными в репозитории."""
    if check:
        stale = [
            path
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            names = ", ".join(str(path) for path in stale)
            raise SystemExit(f"Экспорт устарел: {names}; запустите скрипт без --check")
        return
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
