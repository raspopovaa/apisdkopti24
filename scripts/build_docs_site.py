from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    print(f"Built documentation site in {PROJECT_ROOT / 'site'}")


if __name__ == "__main__":
    main()
