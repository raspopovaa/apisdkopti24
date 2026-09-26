import importlib.util
import sys
from pathlib import Path

import pytest

LIVE_CHECK_DIR = Path(__file__).resolve().parents[1] / "tools" / "live_check"


def _load(name: str):
    if str(LIVE_CHECK_DIR) not in sys.path:
        sys.path.insert(0, str(LIVE_CHECK_DIR))
    spec = importlib.util.spec_from_file_location(name, LIVE_CHECK_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_method_files_match_the_generator() -> None:
    generator = _load("_generate")

    outputs = generator.build_all()

    assert len(outputs) == 89
    stale = sorted(
        path.name
        for path, content in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    )
    assert stale == [], "запустите python tools/live_check/_generate.py --force"


def test_mask_hides_secrets_but_keeps_identifiers() -> None:
    common = _load("_common")

    masked = common.mask(
        {
            "api_key": "secret",
            "session_id": "session",
            "card_number": "7000000000000000",
            "card_id": "382359",
            "nested": [{"password": "secret", "contract_id": "1-AAA"}],
        }
    )

    assert masked == {
        "api_key": "***",
        "session_id": "***",
        "card_number": "***",
        "card_id": "382359",
        "nested": [{"password": "***", "contract_id": "1-AAA"}],
    }
    assert common.mask({"code": "1234"}, common.REQUEST_SECRET_KEYS) == {"code": "***"}


def test_overrides_replace_parameters_and_reject_unknown_names(monkeypatch) -> None:
    common = _load("_common")
    monkeypatch.setattr(
        common,
        "_DATA",
        {"overrides": {"get_info": {"period": "2026-09"}, "get_cards_v2": {"typo": 1}}},
    )

    assert common.apply_overrides("get_info", {"period": None}) == {"period": "2026-09"}
    assert common.apply_overrides("logoff", {}) == {}
    with pytest.raises(SystemExit, match="typo"):
        common.apply_overrides("get_cards_v2", {"page": None})


def test_importing_common_does_not_require_test_data() -> None:
    common = _load("_common")

    assert common._DATA is None or isinstance(common._DATA, dict)
