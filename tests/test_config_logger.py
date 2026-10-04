from __future__ import annotations

import importlib
import io
import json
import logging
import os
from pathlib import Path

import pytest

from apisdkopti24 import config as config_module
from apisdkopti24 import env as env_module
from apisdkopti24 import logger as logger_module
from apisdkopti24.credentials import (
    EnvironmentCredentialsProvider,
    StaticCredentialsProvider,
)
from apisdkopti24.errors import SDKConfigurationError

# Тесты совместимости намеренно создают устаревший APISettings.
pytestmark = pytest.mark.filterwarnings("ignore:APISettings устарел:DeprecationWarning")


def test_config_import_does_not_load_dotenv(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setattr(
        env_module, "load_env_file", lambda: (_ for _ in ()).throw(AssertionError())
    )

    importlib.reload(config_module)

    assert not hasattr(config_module, "API_KEY")


def test_settings_repr_redacts_credentials():
    settings = config_module.APISettings(
        base_url="https://example.invalid/vip/",
        api_key="secret-api-key",
        login="secret-login",
        password="secret-password",
    )

    rendered = repr(settings)

    assert "secret-api-key" not in rendered
    assert "secret-login" not in rendered
    assert "secret-password" not in rendered


def test_connection_settings_never_contain_credentials():
    settings = config_module.ConnectionSettings(base_url="https://example.invalid/vip/")

    assert not hasattr(settings, "api_key")
    assert not hasattr(settings, "login")
    assert not hasattr(settings, "password")


def test_static_credentials_provider_repr_is_redacted():
    provider = StaticCredentialsProvider(
        api_key="secret-api-key",
        login="secret-login",
        password="secret-password",
    )

    rendered = repr(provider)
    assert "secret-api-key" not in rendered
    assert "secret-login" not in rendered
    assert "secret-password" not in rendered


def test_environment_credentials_provider_reads_secrets(monkeypatch):
    monkeypatch.setenv("API_KEY", "env-api-key")
    monkeypatch.setenv("API_LOGIN", "env-login")
    monkeypatch.setenv("API_PASSWORD", "env-password")

    provider = EnvironmentCredentialsProvider.from_env(load_dotenv=False)

    assert provider.get_api_key() == "env-api-key"
    assert provider.get_credentials() == ("env-login", "env-password")


def test_from_env_loads_dotenv_when_requested(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)

    def fake_load_env_file(path: str | Path) -> None:
        assert path == ".env"
        os.environ["API_KEY"] = "loaded-from-env-file"

    monkeypatch.setattr(config_module, "load_env_file", fake_load_env_file)

    settings = config_module.APISettings.from_env()

    assert settings.api_key == "loaded-from-env-file"


def test_from_env_uses_explicit_env_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    captured_path = None

    def fake_load_env_file(path: str | Path) -> None:
        nonlocal captured_path
        captured_path = path

    monkeypatch.setattr(config_module, "load_env_file", fake_load_env_file)

    config_module.APISettings.from_env(env_file=env_file)

    assert captured_path == env_file


def test_from_env_loads_request_rate_limit(monkeypatch):
    monkeypatch.setenv("API_REQUESTS_PER_SECOND", "2")
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    settings = config_module.APISettings.from_env()

    assert settings.rate_limit_policy.requests_per_second == 2
    assert settings.rate_limit_policy.minimum_interval_seconds == 0.5


def test_from_env_loads_concurrency_limit(monkeypatch):
    monkeypatch.setenv("API_MAX_IN_FLIGHT", "7")
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    settings = config_module.ConnectionSettings.from_env()

    assert settings.concurrency_policy.max_in_flight == 7


def test_from_env_loads_json_response_limit(monkeypatch):
    monkeypatch.setenv("API_MAX_JSON_RESPONSE_BYTES", "4096")
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    settings = config_module.ConnectionSettings.from_env()

    assert settings.max_json_response_bytes == 4096


def test_from_env_loads_all_response_limits(monkeypatch):
    monkeypatch.setenv("API_MAX_IN_MEMORY_RESPONSE_BYTES", "8192")
    monkeypatch.setenv("API_MAX_ERROR_RESPONSE_BYTES", "2048")
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    settings = config_module.ConnectionSettings.from_env()

    assert settings.max_in_memory_response_bytes == 8192
    assert settings.max_error_response_bytes == 2048


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("API_MAX_IN_FLIGHT", "invalid", "API_MAX_IN_FLIGHT должен содержать целое число"),
        ("API_MAX_JSON_RESPONSE_BYTES", "0", "API_MAX_JSON_RESPONSE_BYTES должен быть больше нуля"),
        ("API_REQUESTS_PER_SECOND", "none", "API_REQUESTS_PER_SECOND должен содержать число"),
    ],
)
def test_from_env_reports_invalid_numeric_variable(monkeypatch, name, value, message):
    monkeypatch.setenv(name, value)
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    with pytest.raises(config_module.SDKConfigurationError, match=message):
        config_module.ConnectionSettings.from_env()


def test_from_env_requires_explicit_insecure_http_opt_in(monkeypatch):
    monkeypatch.setenv("API_ALLOW_INSECURE_HTTP", "true")
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    settings = config_module.APISettings.from_env()

    assert settings.allow_insecure_http is True


def test_client_logger_uses_append_mode_and_sanitizes_files(tmp_path):
    log_path = tmp_path / "sdk.log"
    request_path = tmp_path / "requests.jsonl"
    log_path.write_text("existing\n", encoding="utf-8")

    managed = logger_module.create_client_logger(
        log_level="INFO",
        logger_file=str(log_path),
        request_log_file=str(request_path),
    )

    assert any(isinstance(handler, logging.FileHandler) for handler in managed.logger.handlers)

    managed.logger.info("api_key=%s password=%s", "secret-key", "secret-pass")
    managed.close()

    content = log_path.read_text(encoding="utf-8")

    assert content.startswith("existing\n")
    assert "secret-key" not in content
    assert "secret-pass" not in content
    assert "***" in content
    assert request_path.read_text(encoding="utf-8") == ""


def test_injected_logger_receives_sanitizing_filter():
    stream = io.StringIO()
    injected_logger = logging.getLogger(f"bound-logger-{id(stream)}")
    injected_logger.handlers.clear()
    injected_logger.propagate = False
    injected_logger.setLevel(logging.INFO)
    injected_logger.addHandler(logging.StreamHandler(stream))

    logger_module.ensure_sanitizing_filter(injected_logger)
    injected_logger.info("card_id=%s", "sensitive-card-id")

    assert "sensitive-card-id" not in stream.getvalue()
    assert "***" in stream.getvalue()


def test_request_audit_log_is_jsonl_and_contains_no_endpoint_values(tmp_path):
    managed = logger_module.create_client_logger(
        log_level="INFO",
        logger_file=str(tmp_path / "sdk.log"),
        request_log_file=str(tmp_path / "requests.jsonl"),
    )

    managed.logger.info(
        "Аудит запроса API",
        extra={
            "request_audit": True,
            "event": "started",
            "operation": "get_card_drivers",
            "api_version": "v1",
            "route_name": "default",
            "http_method": "GET",
            "recovered": False,
        },
    )
    managed.close()

    payload = json.loads((tmp_path / "requests.jsonl").read_text(encoding="utf-8"))
    assert payload["operation"] == "get_card_drivers"
    assert payload["http_method"] == "GET"
    assert "endpoint" not in payload


def test_closing_one_client_logger_does_not_close_another(tmp_path):
    first = logger_module.create_client_logger(
        log_level="INFO",
        logger_file=str(tmp_path / "first.log"),
        request_log_file=str(tmp_path / "first.jsonl"),
    )
    second = logger_module.create_client_logger(
        log_level="INFO",
        logger_file=str(tmp_path / "second.log"),
        request_log_file=str(tmp_path / "second.jsonl"),
    )

    first.close()
    second.logger.info("still active")
    second.close()

    assert "still active" in (tmp_path / "second.log").read_text(encoding="utf-8")


def test_client_logger_writes_no_files_unless_configured(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    managed = logger_module.create_client_logger(log_level="INFO")
    managed.logger.info("без файлов")
    managed.close()

    assert managed.logger.name == logger_module.SHARED_CLIENT_LOGGER_NAME
    assert managed.handlers == ()
    assert list(tmp_path.iterdir()) == []


def test_closing_file_client_logger_releases_it_from_logging_registry(tmp_path):
    managed = logger_module.create_client_logger(
        log_level="INFO",
        logger_file=str(tmp_path / "sdk.log"),
    )
    name = managed.logger.name
    assert name in logging.Logger.manager.loggerDict

    managed.close()

    assert name not in logging.Logger.manager.loggerDict
    assert not (tmp_path / "requests.jsonl").exists()


def test_settings_do_not_enable_log_files_by_default(monkeypatch):
    monkeypatch.delenv("LOGGER_FILE", raising=False)
    monkeypatch.delenv("REQUEST_LOG_FILE", raising=False)
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    settings = config_module.ConnectionSettings.from_env()

    assert settings.logger_file is None
    assert settings.request_log_file is None


@pytest.mark.parametrize(
    "name",
    ["API_MAX_IN_FLIGHT", "API_REQUESTS_PER_SECOND", "API_MAX_JSON_RESPONSE_BYTES", "LOGGER_FILE"],
)
def test_empty_environment_values_mean_default(monkeypatch, name):
    monkeypatch.setenv(name, "  ")
    monkeypatch.setattr(config_module, "load_env_file", lambda _path: None)

    settings = config_module.ConnectionSettings.from_env()

    assert settings.concurrency_policy.max_in_flight == 20
    assert settings.rate_limit_policy.requests_per_second is None
    assert settings.max_json_response_bytes == 16 * 1024 * 1024
    assert settings.logger_file is None


def test_api_settings_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="APISettings устарел"):
        config_module.APISettings(base_url="https://api.example.ru/vip/", api_key="key")


def test_env_file_supports_inline_comments_and_export(tmp_path, monkeypatch) -> None:
    for name in ("API_KEY", "API_LOGIN", "API_PASSWORD", "API_BASE_URL"):
        # setenv запоминает исходное состояние, и после теста monkeypatch его вернёт.
        monkeypatch.setenv(name, "placeholder")
        monkeypatch.delenv(name)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "export API_BASE_URL=https://api.example.ru/vip/\n"
        "API_KEY=key-value  # ключ из портала\n"
        "API_LOGIN='login # not a comment'\n"
        "API_PASSWORD=pa#ss\n",
        encoding="utf-8",
    )

    env_module.load_env_file(env_file)

    assert os.environ["API_BASE_URL"] == "https://api.example.ru/vip/"
    assert os.environ["API_KEY"] == "key-value"
    assert os.environ["API_LOGIN"] == "login # not a comment"
    assert os.environ["API_PASSWORD"] == "pa#ss"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("on", True), ("TRUE", True), ("1", True), ("off", False), ("no", False), ("", False)],
)
def test_insecure_http_flag_accepts_common_spellings(monkeypatch, raw, expected) -> None:
    monkeypatch.setenv("API_BASE_URL", "https://api.example.ru/vip/")
    monkeypatch.setenv("API_ALLOW_INSECURE_HTTP", raw)

    settings = config_module.ConnectionSettings.from_env(load_dotenv=False)

    assert settings.allow_insecure_http is expected


def test_unknown_insecure_http_flag_and_log_level_are_rejected(monkeypatch) -> None:
    monkeypatch.setenv("API_BASE_URL", "https://api.example.ru/vip/")
    monkeypatch.setenv("API_ALLOW_INSECURE_HTTP", "maybe")
    with pytest.raises(SDKConfigurationError, match="API_ALLOW_INSECURE_HTTP"):
        config_module.ConnectionSettings.from_env(load_dotenv=False)

    monkeypatch.delenv("API_ALLOW_INSECURE_HTTP")
    monkeypatch.setenv("LOG_LEVEL", "DEBG")
    with pytest.raises(SDKConfigurationError, match="log_level"):
        config_module.ConnectionSettings.from_env(load_dotenv=False)


@pytest.mark.parametrize("log_level", ["WARNING", "ERROR", "CRITICAL"])
def test_request_audit_keeps_info_events_whatever_the_log_level(tmp_path, log_level):
    managed = logger_module.create_client_logger(
        log_level=log_level,
        logger_file=str(tmp_path / "sdk.log"),
        request_log_file=str(tmp_path / "requests.jsonl"),
    )

    managed.logger.info(
        "Аудит запроса API",
        extra={"request_audit": True, "event": "completed", "operation": "get_cards_v2"},
    )
    managed.logger.info("Обычное сообщение уровня INFO")
    managed.close()

    events = [
        json.loads(line)["event"]
        for line in (tmp_path / "requests.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert events == ["completed"]
    # Обычный журнал по-прежнему подчиняется log_level.
    assert (tmp_path / "sdk.log").read_text(encoding="utf-8") == ""
