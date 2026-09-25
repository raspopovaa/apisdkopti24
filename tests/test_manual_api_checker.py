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


def test_mask_secrets_hides_only_session_and_login_secrets() -> None:
    checker = load_checker()

    masked = checker.mask_secrets(
        {
            "data": {
                "session_id": "secret-session",
                "client_id": "1-CLIENT",
                "contracts": [{"id": "1-CONTRACT", "number": "N-1"}],
            },
            "Password": "secret-password",
        }
    )

    assert masked == {
        "data": {
            "session_id": "***",
            "client_id": "1-CLIENT",
            "contracts": [{"id": "1-CONTRACT", "number": "N-1"}],
        },
        "Password": "***",
    }


def test_response_recorder_saves_responses_and_known_values(tmp_path) -> None:
    import json
    import stat

    import httpx

    checker = load_checker()
    path = tmp_path / "out" / "responses.jsonl"
    recorder = checker.ResponseRecorder(path)
    checker.CURRENT_METHOD_NAME = "get_cards_v2"
    response = httpx.Response(
        200,
        json={"status": {"code": 200}, "data": {"result": [{"id": "1-CARD"}]}},
    )

    recorder.record_response(
        "get",
        "https://api.example.ru/vip/v2/cards",
        {"params": {"contract_id": "1-CONTRACT"}, "headers": {"api_key": "secret"}},
        response,
    )
    recorder.save_known_values({"card_id": "1-CARD", "session_id": "secret-session"})
    recorder.close()

    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["operation"] == "get_cards_v2"
    assert record["request"] == {
        "method": "GET",
        "url": "https://api.example.ru/vip/v2/cards",
        "params": {"contract_id": "1-CONTRACT"},
        "body": None,
    }
    assert "headers" not in record["request"]
    assert record["response"]["status"] == 200
    assert record["response"]["body"]["data"]["result"] == [{"id": "1-CARD"}]
    known = json.loads(recorder.known_values_path.read_text(encoding="utf-8"))
    assert known == {"card_id": "1-CARD", "session_id": "***"}
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(recorder.known_values_path.stat().st_mode) == 0o600


def test_cli_saves_responses_by_default_and_can_disable_it(tmp_path) -> None:
    checker = load_checker()
    env_file = tmp_path / ".env"
    env_file.write_text("API_BASE_URL=https://api.example.ru/vip/\n", encoding="utf-8")

    _, default_file = checker.parse_cli_args(["--env-file", str(env_file)])
    _, custom_file = checker.parse_cli_args(
        ["--env-file", str(env_file), "--responses-file", str(tmp_path / "r.jsonl")]
    )
    _, disabled = checker.parse_cli_args(["--env-file", str(env_file), "--no-save-responses"])

    assert default_file is not None
    assert default_file.parent == checker.DEFAULT_RESPONSES_DIR
    assert default_file.suffix == ".jsonl"
    assert custom_file == (tmp_path / "r.jsonl").resolve()
    assert disabled is None
