import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


# Переменные окружения, которые читает SDK. Экспортированный .env разработчика или
# настройки облачной среды не должны менять результат тестов.
SDK_ENVIRONMENT_VARIABLES = (
    "API_ALLOW_INSECURE_HTTP",
    "API_BASE_URL",
    "API_KEY",
    "API_LOGIN",
    "API_MAX_ERROR_RESPONSE_BYTES",
    "API_MAX_IN_FLIGHT",
    "API_MAX_IN_MEMORY_RESPONSE_BYTES",
    "API_MAX_JSON_RESPONSE_BYTES",
    "API_PASSWORD",
    "API_REQUESTS_PER_SECOND",
    "LOGGER_FILE",
    "LOG_LEVEL",
    "REQUEST_LOG_FILE",
)


@pytest.fixture(autouse=True)
def isolated_sdk_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in SDK_ENVIRONMENT_VARIABLES:
        monkeypatch.delenv(name, raising=False)
