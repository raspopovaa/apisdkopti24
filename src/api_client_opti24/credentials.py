from __future__ import annotations

import os
from pathlib import Path

from .env import load_env_file


class StaticAPIKeyProvider:
    __slots__ = ("__api_key",)

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.__api_key = api_key

    def __repr__(self) -> str:
        return f"{type(self).__name__}(api_key=***)"

    def get_api_key(self) -> str:
        return self.__api_key


class StaticLoginPasswordProvider:
    __slots__ = ("__login", "__password")

    def __init__(self, *, login: str, password: str) -> None:
        if not login or not password:
            raise ValueError("login and password are required")
        self.__login = login
        self.__password = password

    def __repr__(self) -> str:
        return f"{type(self).__name__}(login=***, password=***)"

    def get_credentials(self) -> tuple[str, str]:
        return self.__login, self.__password


class StaticCredentialsProvider:
    __slots__ = ("__api_key", "__login", "__password")

    def __init__(self, *, api_key: str, login: str, password: str) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        if not login or not password:
            raise ValueError("login and password are required")
        self.__api_key = api_key
        self.__login = login
        self.__password = password

    def __repr__(self) -> str:
        return f"{type(self).__name__}(api_key=***, login=***, password=***)"

    def get_api_key(self) -> str:
        return self.__api_key

    def get_credentials(self) -> tuple[str, str]:
        return self.__login, self.__password


class EnvironmentCredentialsProvider(StaticCredentialsProvider):
    @classmethod
    def from_env(
        cls,
        *,
        load_dotenv: bool = True,
        env_file: str | Path = ".env",
    ) -> EnvironmentCredentialsProvider:
        if load_dotenv:
            load_env_file(env_file)
        return cls(
            api_key=os.getenv("API_KEY", ""),
            login=os.getenv("API_LOGIN", ""),
            password=os.getenv("API_PASSWORD", ""),
        )


__all__ = [
    "EnvironmentCredentialsProvider",
    "StaticAPIKeyProvider",
    "StaticCredentialsProvider",
    "StaticLoginPasswordProvider",
]
