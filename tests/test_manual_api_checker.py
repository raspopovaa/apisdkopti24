from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


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

    _, default_file, default_save, _ = checker.parse_cli_args(["--env-file", str(env_file)])
    _, custom_file, custom_save, _ = checker.parse_cli_args(
        ["--env-file", str(env_file), "--responses-file", str(tmp_path / "r.jsonl")]
    )
    _, _, disabled_save, _ = checker.parse_cli_args(
        ["--env-file", str(env_file), "--no-save-responses"]
    )

    assert default_file is None and default_save is True
    assert custom_file == (tmp_path / "r.jsonl").resolve() and custom_save is True
    assert disabled_save is False


def test_default_responses_file_is_next_to_logger_file(tmp_path) -> None:
    checker = load_checker()

    path = checker.default_responses_file(str(tmp_path / "logs" / "api.log"))

    assert path.parent == (tmp_path / "logs").resolve()
    assert path.name.startswith("responses-")
    assert path.suffix == ".jsonl"


def test_response_record_explains_inputs_and_fields(tmp_path) -> None:
    import json

    import httpx

    checker = load_checker()
    recorder = checker.ResponseRecorder(tmp_path / "responses.jsonl")
    checker.CURRENT_METHOD_NAME = "get_cards_v2"
    checker.CURRENT_INPUTS.clear()
    checker.CURRENT_INPUTS.update({"contract_id": "1-CONTRACT", "page": "1", "pin": "1234"})
    response = httpx.Response(
        200,
        json={"status": {"code": 200}, "data": {"result": [{"id": "1-CARD"}]}},
    )

    recorder.record_response(
        "get",
        "https://api.example.ru/vip/v2/cards",
        {"params": {"contract_id": "1-CONTRACT"}},
        response,
    )
    recorder.close()

    record = json.loads(recorder.path.read_text(encoding="utf-8"))
    inputs = record["input_parameters"]
    assert record["operation_description"]
    assert inputs["contract_id"]["value"] == "1-CONTRACT"
    assert inputs["contract_id"]["description"]
    assert inputs["page"]["description"] == "Номер страницы результата."
    assert inputs["pin"]["value"] == "***"
    fields = record["field_descriptions"]
    assert fields["status.code"]
    assert fields["data.result[].id"]
    assert fields["contract_id"]


def test_trace_hides_only_secrets_and_sms_code_in_requests() -> None:
    checker = load_checker()
    body = {
        "status": {"code": 403, "errors": [{"type": "accessDenied", "message": "Нельзя"}]},
        "data": {
            "result": [
                {
                    "id": "1-TX",
                    "card_id": "1-CARD",
                    "code": "1-GOODS",
                    "timestamp": "2024-04-15T20:09:05.000000Z",
                    "session_id": "secret-session",
                }
            ]
        },
    }

    shown = checker.sanitize_http_value(body)
    item = shown["data"]["result"][0]
    params = checker.sanitize_request_value(
        {"contract_id": "1-CONTRACT", "date_from": "2024-04-15", "api_key": "k"}
    )

    assert shown["status"]["code"] == 403
    assert item["id"] == "1-TX" and item["card_id"] == "1-CARD" and item["code"] == "1-GOODS"
    assert item["timestamp"] == "2024-04-15T20:09:05.000000Z"
    assert item["session_id"] == "***"
    assert params == {"contract_id": "1-CONTRACT", "date_from": "2024-04-15", "api_key": "***"}
    assert checker.body_preview({"json": {"card_id": "1", "code": "1234"}}) == {
        "card_id": "1",
        "code": "***",
    }


def _write_previous_run(path: Path) -> None:
    import json

    records = [
        {
            "operation": "auth_user",
            "input_parameters": {"Введите": {"value": "1-CONTRACT", "description": None}},
            "request": {"method": "POST", "url": "https://api.example.ru/vip/v1/authUser"},
            "response": {"status": 200, "body": {"status": {"code": 200}}},
        },
        {
            "operation": "get_cards_v2",
            "input_parameters": {
                "page": {"value": "2", "description": None},
                "pin": {"value": "***", "description": None},
            },
            "request": {"method": "GET", "url": "https://api.example.ru/vip/v2/cards"},
            "response": {
                "status": 200,
                "body": {"status": {"code": 200}, "data": {"result": [{"id": "1-CARD"}]}},
            },
        },
        {
            "operation": "check_purchase",
            "input_parameters": {},
            "request": {
                "method": "GET",
                "url": "https://api.example.ru/vip/v1/getDictionary",
                "params": {"name": "Goods"},
            },
            "response": {
                "status": 200,
                "body": {"status": {"code": 200}, "data": {"result": [{"code": "G-1"}]}},
            },
        },
    ]
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    path.write_text("\n".join(lines) + '\n{"operation": "cut', encoding="utf-8")


def test_previous_run_values_become_defaults(tmp_path) -> None:
    checker = load_checker()
    previous = tmp_path / "responses.jsonl"
    _write_previous_run(previous)
    state: dict[str, object] = {}
    checker.CURRENT_STATE = state

    stats = checker.load_previous_responses(previous, state)

    assert stats == {"records": 3, "skipped": 1}
    assert state["card_id"] == "1-CARD"
    assert state["contract_id"] == "1-CONTRACT"
    assert state["reference_data"]["goods_code"] == "G-1"
    assert "dictionary:Goods" in state["reference_data"]
    checker.CURRENT_METHOD_NAME = "auth_user"
    assert checker.previous_input("Введите ID договора") == "1-CONTRACT"
    checker.CURRENT_METHOD_NAME = "get_cards_v2"
    assert checker.previous_input("page") == "2"
    assert checker.previous_input("pin") is None


def test_cli_accepts_previous_run_file(tmp_path) -> None:
    checker = load_checker()
    env_file = tmp_path / ".env"
    env_file.write_text("API_BASE_URL=https://api.example.ru/vip/\n", encoding="utf-8")
    previous = tmp_path / "responses.jsonl"
    previous.write_text("", encoding="utf-8")

    *_, from_responses = checker.parse_cli_args(
        ["--env-file", str(env_file), "--from-responses", str(previous)]
    )

    assert from_responses == previous.resolve()


def load_auto_runner() -> ModuleType:
    path = Path(__file__).parents[1] / "examples" / "check_all_89_auto.py"
    spec = importlib.util.spec_from_file_location("check_all_89_auto", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_auto_runner_fills_known_values_without_input(tmp_path, monkeypatch) -> None:
    auto = load_auto_runner()
    checker = auto.load_checker()
    previous = tmp_path / "responses.jsonl"
    _write_previous_run(previous)
    state: dict[str, object] = {}
    checker.CURRENT_STATE = state
    checker.load_previous_responses(previous, state)
    auto.install_auto_answers(checker, mutations="skip", no_prompt=True)
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("input() не должен вызываться"))
    checker.CURRENT_METHOD_NAME = "get_cards_v2"
    checker.CURRENT_INPUTS.clear()

    assert checker.ask_value("page") == "2"
    assert checker.ask_value("card_id", default=state["card_id"]) == "1-CARD"
    assert checker.ask_value("q", required=False) is None
    assert checker.ask_bool("with_send", default=True) is True
    assert checker.CURRENT_INPUTS == {"page": "2", "card_id": "1-CARD", "with_send": True}
    with pytest.raises(checker.SkipMethod):
        checker.ask_value("user_id")
    checker.prompt_before_call(mutating=False)
    with pytest.raises(checker.SkipMethod):
        checker.prompt_before_call(mutating=True)


def test_auto_runner_passes_other_arguments_to_checker() -> None:
    auto = load_auto_runner()

    args, rest = auto.parse_auto_args(
        ["--mutations", "skip", "--env-file", ".env", "--from-responses", "r.jsonl"]
    )

    assert args.mutations == "skip" and args.no_prompt is False
    assert rest == ["--env-file", ".env", "--from-responses", "r.jsonl"]
