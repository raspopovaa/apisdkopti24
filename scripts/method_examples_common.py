"""Общие пути, константы и реестр генератора учебных примеров.

Модуль генератора scripts/generate_method_examples.py; отдельно не запускается.
"""

from pathlib import Path

import black
from documentation_generator import (
    load_metadata,
)

from apisdkopti24.registry import build_default_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = PROJECT_ROOT / "examples" / "methods"


DOCS_DIR = PROJECT_ROOT / "docs" / "examples"


DATA_TYPES_DIR = PROJECT_ROOT / "docs" / "data-types"


FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "spec" / "1.1.60"


DOCS_SITE_URL = "https://raspopovaa.github.io/apisdkopti24/latest/"


BASE_URL = "https://api-demo.opti-24.ru/vip/"


# Договор из фикстуры authUser; пример выбирает его так же, как API_CONTRACT_ID.
CONTRACT_ID = "1-T000025"


SECRET_HEADERS = frozenset({"api_key", "session_id"})


# Значения этих полей запроса на страницах заменяются на «***», как в журналах SDK.
SECRET_FIELDS = frozenset({"password", "pin", "new_pin", "device_id"})


SHOWN_HEADERS = ("api_key", "session_id", "contract_id", "date_time", "content-type")


MAX_LIST_ITEMS = 2


BLACK_MODE = black.Mode(line_length=100, string_normalization=False)


REGISTRY = build_default_registry()


CONTRACTS_DIR = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"


API_CONTRACT = PROJECT_ROOT / "specifications" / "api-contract-v1.1.60.yaml"


QR_CONTRACT = PROJECT_ROOT / "specifications" / "api-qr-contract-v1.0.4.yaml"


COMPATIBILITY_DOC = PROJECT_ROOT / "docs" / "spec-compatibility.md"


DOC_METADATA = load_metadata()


# Общий конверт ответа описан один раз в «Типах данных», в таблицах метода не повторяется.
ENVELOPE_MODELS = frozenset({"ResponseStatus"})


# Параметр метода SDK называется иначе, чем поле запроса API.
PARAMETER_ALIASES = {"card_ids": "card_id"}


# То же для отдельных методов: (метод, параметр SDK) -> поле API.
METHOD_PARAMETER_ALIASES = {("set_card_group", "group_id"): "id"}


def api_parameter_name(method_name: str, parameter_name: str) -> str:
    return METHOD_PARAMETER_ALIASES.get(
        (method_name, parameter_name), PARAMETER_ALIASES.get(parameter_name, parameter_name)
    )
