from __future__ import annotations

import importlib
import io
import json
import logging
import os
from pathlib import Path

from api_client_opti24 import config as config_module
from api_client_opti24 import env as env_module
from api_client_opti24 import logger as logger_module
from api_client_opti24.credentials import (
    EnvironmentCredentialsProvider,
    StaticCredentialsProvider,
)


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
        "API request audit",
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
