import os
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


@pytest.mark.parametrize(
    "build",
    [
        lambda: StaticAPIKeyProvider(""),
        lambda: StaticLoginPasswordProvider(login="", password="p"),
        lambda: StaticLoginPasswordProvider(login="l", password=""),
        lambda: StaticCredentialsProvider(api_key="", login="l", password="p"),
        lambda: StaticCredentialsProvider(api_key="k", login="l", password=""),
    ],
)
def test_empty_credentials_are_rejected(build: Callable[[], object]) -> None:
    with pytest.raises(SDKConfigurationError):
        build()


def test_credential_providers_do_not_reveal_secrets_in_repr() -> None:
    providers = [
        StaticAPIKeyProvider("key-secret"),
        StaticLoginPasswordProvider(login="login-secret", password="pass-secret"),
        StaticCredentialsProvider(
            api_key="key-secret", login="login-secret", password="pass-secret"
        ),
    ]

    for provider in providers:
        assert "secret" not in repr(provider)
