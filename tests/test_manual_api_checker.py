from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_checker() -> ModuleType:
    path = Path(__file__).parents[1] / "examples" / "check_all_89_real_api.py"
    spec = importlib.util.spec_from_file_location("check_all_89_real_api", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_manual_check_has_request_and_model_metadata() -> None:
    checker = load_checker()
    method_names = {name for name, _ in checker.CHECKS}

    assert len(method_names) == 89
    assert method_names <= checker.build_request_matrix().keys()
    assert method_names <= checker.build_model_matrix().keys()


def test_request_example_uses_sanitized_host_and_headers(capsys) -> None:
    checker = load_checker()

    checker.print_request_example("get_documents")

    output = capsys.readouterr().out
    assert "GET https://api.example.ru/" in output
    assert "api_key=***" in output
    assert "session_id=***" in output
