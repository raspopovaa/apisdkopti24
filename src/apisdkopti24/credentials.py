from __future__ import annotations

import asyncio
import math
import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from types import TracebackType

from .env import load_env_file
from .errors import SDKConfigurationError
from .logger import LoggerLike
from .logger import logger as default_logger


class StaticAPIKeyProvider:
    __slots__ = ("__api_key",)

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise SDKConfigurationError("Необходимо указать api_key")
        self.__api_key = api_key

    def __repr__(self) -> str:
        return f"{type(self).__name__}(api_key=***)"

    def get_api_key(self) -> str:
        return self.__api_key


class StaticLoginPasswordProvider:
    __slots__ = ("__login", "__password")

    def __init__(self, *, login: str, password: str) -> None:
        if not login or not password:
            raise SDKConfigurationError("Необходимо указать login и password")
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
            raise SDKConfigurationError("Необходимо указать api_key")
        if not login or not password:
            raise SDKConfigurationError("Необходимо указать login и password")
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


class RefreshingAPIKeyProvider:
    """Ключ API в памяти с периодическим обновлением из внешнего источника.

    SDK вызывает ``get_api_key()`` перед каждым запросом, поэтому новый ключ
    начинает действовать со следующего запроса без пересоздания клиента.
    ``get_api_key()`` не обращается к сети и диску: ключ получает асинхронная
    функция ``fetch_api_key`` — при ``start()`` и затем раз в ``ttl_seconds``.
    После ротации, которую выполняет само приложение, вызовите
    ``set_api_key()`` или ``await refresh()``, чтобы не ждать конца интервала.
    """

    __slots__ = (
        "__fetch_api_key",
        "__ttl_seconds",
        "__sleep",
        "__logger",
        "__api_key",
        "__refresher",
        "__start_lock",
        "__last_refresh_failed",
    )

    def __init__(
        self,
        fetch_api_key: Callable[[], Awaitable[str]],
        *,
        ttl_seconds: float,
        logger: LoggerLike | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if not math.isfinite(ttl_seconds) or ttl_seconds <= 0:
            raise SDKConfigurationError("ttl_seconds должен быть положительным конечным числом")
        self.__fetch_api_key = fetch_api_key
        self.__ttl_seconds = ttl_seconds
        self.__sleep = sleep
        self.__logger = logger or default_logger
        self.__api_key = ""
        self.__refresher: asyncio.Task[None] | None = None
        # Между проверкой __refresher и созданием задачи есть await refresh(): без
        # блокировки параллельные start() запускали бы вторую, неостанавливаемую задачу.
        self.__start_lock = asyncio.Lock()
        self.__last_refresh_failed = False

    def __repr__(self) -> str:
        return f"{type(self).__name__}(api_key=***, ttl_seconds={self.__ttl_seconds})"

    @property
    def last_refresh_failed(self) -> bool:
        """Последнее фоновое обновление не удалось; действует прежний ключ."""
        return self.__last_refresh_failed

    def get_api_key(self) -> str:
        if not self.__api_key:
            raise SDKConfigurationError(
                "Ключ API ещё не получен: вызовите await provider.start() или "
                "await provider.refresh() до первого запроса"
            )
        return self.__api_key

    def set_api_key(self, api_key: str) -> None:
        """Сразу заменить ключ, например сразу после ротации в личном кабинете."""
        if not api_key:
            raise SDKConfigurationError("Необходимо указать api_key")
        self.__api_key = api_key
        self.__last_refresh_failed = False

    async def refresh(self) -> None:
        """Получить ключ из источника; при ошибке прежний ключ не меняется."""
        self.set_api_key(await self.__fetch_api_key())

    async def start(self) -> None:
        """Получить первый ключ и запустить фоновое обновление."""
        async with self.__start_lock:
            if self.__refresher is not None:
                return
            await self.refresh()
            self.__refresher = asyncio.create_task(self.__refresh_periodically())

    async def aclose(self) -> None:
        """Остановить фоновое обновление; последний ключ остаётся доступен."""
        refresher, self.__refresher = self.__refresher, None
        if refresher is None:
            return
        refresher.cancel()
        try:
            await refresher
        except asyncio.CancelledError:
            if not refresher.cancelled():
                raise

    async def __aenter__(self) -> RefreshingAPIKeyProvider:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def __refresh_periodically(self) -> None:
        while True:
            await self.__sleep(self.__ttl_seconds)
            try:
                await self.refresh()
            # Источник ключа — код приложения с неизвестным набором исключений;
            # фоновую задачу нельзя ронять: до следующей попытки работает прежний ключ.
            except Exception as error:  # noqa: BLE001
                self.__last_refresh_failed = True
                self.__logger.warning(
                    "Не удалось обновить ключ API (%s); действует прежний ключ",
                    type(error).__name__[:100],
                )
            else:
                self.__last_refresh_failed = False


__all__ = [
    "EnvironmentCredentialsProvider",
    "RefreshingAPIKeyProvider",
    "StaticAPIKeyProvider",
    "StaticCredentialsProvider",
    "StaticLoginPasswordProvider",
]
