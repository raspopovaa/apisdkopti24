from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_PATH = Path(__file__).resolve().parent
if str(SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PATH))

from documentation_generator import *  # noqa: F403

if __name__ == "__main__":
    main()  # noqa: F405
