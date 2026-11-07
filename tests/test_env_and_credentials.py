import os
import secrets
from collections.abc import Callable
from pathlib import Path

import pytest

from apisdkopti24.credentials import (
    StaticAPIKeyProvider,
    StaticCredentialsProvider,
    StaticLoginPasswordProvider,
)
from apisdkopti24.env import load_env_file
from apisdkopti24.errors import SDKConfigurationError


def test_missing_env_file_is_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SDK_TEST_VALUE", raising=False)

    load_env_file(tmp_path / "absent.env")

    assert "SDK_TEST_VALUE" not in os.environ


def test_env_file_lines_are_parsed_like_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ("SDK_A", "SDK_B", "SDK_C"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("SDK_KEEP", "original")
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\n\nnot a pair\nexport SDK_A=1 # tail\nSDK_B=\"unclosed\nSDK_C='quoted'\nSDK_KEEP=new\n",
        encoding="utf-8",
    )

    load_env_file(env_file)

    assert os.environ["SDK_A"] == "1"
    assert os.environ["SDK_B"] == '"unclosed'
    assert os.environ["SDK_C"] == "quoted"
    assert os.environ["SDK_KEEP"] == "original"


# Значения генерируются: литералы в аргументах password сканеры считают утечкой секрета.
_FILLED = secrets.token_hex(4)
_EMPTY = ""


@pytest.mark.parametrize(
    "build",
    [
        lambda: StaticAPIKeyProvider(_EMPTY),
        lambda: StaticLoginPasswordProvider(login=_EMPTY, password=_FILLED),
        lambda: StaticLoginPasswordProvider(login=_FILLED, password=_EMPTY),
        lambda: StaticCredentialsProvider(api_key=_EMPTY, login=_FILLED, password=_FILLED),
        lambda: StaticCredentialsProvider(api_key=_FILLED, login=_FILLED, password=_EMPTY),
    ],
)
def test_empty_credentials_are_rejected(build: Callable[[], object]) -> None:
    with pytest.raises(SDKConfigurationError):
        build()


def test_credential_providers_do_not_reveal_secrets_in_repr() -> None:
    providers = [
        StaticAPIKeyProvider(_FILLED),
        StaticLoginPasswordProvider(login=_FILLED, password=_FILLED),
        StaticCredentialsProvider(api_key=_FILLED, login=_FILLED, password=_FILLED),
    ]

    for provider in providers:
        assert _FILLED not in repr(provider)
