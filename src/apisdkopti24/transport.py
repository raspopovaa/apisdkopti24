from __future__ import annotations

import asyncio
import ipaddress
import time
from collections.abc import Awaitable, Callable, Iterator, Mapping
from contextlib import AbstractAsyncContextManager, contextmanager, suppress
from datetime import datetime
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urlsplit

import httpx

from .downloads import BoundedResponseReader, DownloadResponseHandler
from .environments import resolve_rate_limit_policy
from .errors import (
    APIConnectionError,
    RequestPreparationError,
    ResponseShapeError,
    ResponseTooLargeError,
    SDKConfigurationError,
)
from .execution_budget import OperationTimeoutError
from .file_io import AtomicFileWriter, FileWriter
from .http_status import RATE_LIMIT_STATUS_CODES
from .logger import LoggerLike
from .logger import logger as default_logger
from .policies import ConcurrencyPolicy, RateLimitPolicy, RetryPolicy
from .requests import FileTarget, PreparedRequest
from .resilience import RATE_LIMITED, RateLimited, RateLimiter, RetryController
from .response import DecodedPayload, ResponseDecoder
from .runtime import Clock


class AsyncHTTPClient(Protocol):
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, object] | None = None,
        data: Mapping[str, object] | None = None,
        json: object = None,
        timeout: float | httpx.Timeout | None = None,
        follow_redirects: bool = False,
    ) -> httpx.Response: ...

    def stream(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, object] | None = None,
        data: Mapping[str, object] | None = None,
        json: object = None,
        timeout: float | httpx.Timeout | None = None,
        follow_redirects: bool = False,
    ) -> AbstractAsyncContextManager[httpx.Response]: ...

    async def aclose(self) -> None: ...


class _InjectedClock:
    def __init__(
        self,
        monotonic: Callable[[], float],
        sleep: Callable[[float], Awaitable[None]],
    ) -> None:
        self._monotonic = monotonic
        self._sleep = sleep

    def now(self) -> datetime:
        return datetime.now()

    def monotonic(self) -> float:
        return self._monotonic()

    async def sleep(self, seconds: float) -> None:
        await self._sleep(seconds)


CONNECTION_FAILURES = (httpx.ConnectError, httpx.ConnectTimeout)


class AsyncTransport:
    """HTTP-адаптер с отдельными политиками повторов, ограничений и записи файлов."""

    def __init__(
        self,
        base_url: str,
        default_timeout: float = 30.0,
        *,
        http_client: AsyncHTTPClient | None = None,
        retry_policy: RetryPolicy | None = None,
        rate_limit_policy: RateLimitPolicy | None = None,
        concurrency_policy: ConcurrencyPolicy | None = None,
        allow_insecure_http: bool = False,
        response_decoder: ResponseDecoder | None = None,
        file_writer: FileWriter | None = None,
        retry_controller: RetryController | None = None,
        logger: LoggerLike | None = None,
        clock: Clock | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        jitter: Callable[[float], float] | None = None,
        max_json_response_bytes: int = 16 * 1024 * 1024,
        max_in_memory_response_bytes: int = 64 * 1024 * 1024,
        max_error_response_bytes: int = 1024 * 1024,
    ) -> None:
        self.base_url = self._normalize_base_url(
            base_url,
            allow_insecure_http=allow_insecure_http,
        )
        self._host = urlsplit(self.base_url).hostname or self.base_url
        self.client = http_client or httpx.AsyncClient(timeout=default_timeout)
        self._owns_http_client = http_client is None
        self.logger = logger or default_logger
        self.response_decoder = response_decoder or ResponseDecoder(logger=self.logger)
        self.retry_policy = retry_policy or RetryPolicy()
        configured_rate_limit = rate_limit_policy or RateLimitPolicy()
        self.rate_limit_policy = resolve_rate_limit_policy(self.base_url, configured_rate_limit)
        self.concurrency_policy = concurrency_policy or ConcurrencyPolicy()
        if max_json_response_bytes < 1:
            raise SDKConfigurationError("max_json_response_bytes должен быть больше нуля")
        if max_in_memory_response_bytes < 1:
            raise SDKConfigurationError("max_in_memory_response_bytes должен быть больше нуля")
        if max_error_response_bytes < 1:
            raise SDKConfigurationError("max_error_response_bytes должен быть больше нуля")
        self._max_json_response_bytes = max_json_response_bytes
        self._max_error_response_bytes = max_error_response_bytes
        self._response_reader = BoundedResponseReader()
        self._clock = clock or _InjectedClock(monotonic, sleep)
        self._concurrency_gate = asyncio.Semaphore(self.concurrency_policy.max_in_flight)
        self._file_writer = file_writer or AtomicFileWriter()
        self._download_handler = DownloadResponseHandler(
            decoder=self.response_decoder,
            file_writer=self._file_writer,
            max_in_memory_response_bytes=max_in_memory_response_bytes,
            max_error_response_bytes=max_error_response_bytes,
        )
        limiter = RateLimiter(
            request_interval=self.rate_limit_policy.minimum_interval_seconds,
            auth_interval=self.retry_policy.auth_retry_min_interval_seconds,
            clock=self._clock,
        )
        self._retry = retry_controller or RetryController(
            policy=self.retry_policy,
            limiter=limiter,
            clock=self._clock,
            logger=self.logger,
            jitter=jitter,
        )

    @staticmethod
    def _normalize_base_url(base_url: str, *, allow_insecure_http: bool = False) -> str:
        normalized = base_url.strip()
        if not normalized:
            raise SDKConfigurationError(
                "base_url не задан; укажите API_BASE_URL в .env или передайте base_url явно"
            )
        parsed = urlsplit(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SDKConfigurationError(
                "base_url должен быть абсолютным URL, начинающимся с http:// или https://; "
                f"получено {base_url!r}"
            )
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise SDKConfigurationError(
                "base_url не должен содержать учётные данные, строку запроса или фрагмент"
            )
        if (
            parsed.scheme == "http"
            and not allow_insecure_http
            and not AsyncTransport._is_loopback_host(parsed.hostname)
        ):
            raise SDKConfigurationError(
                "base_url должен использовать https:// для удалённых узлов; "
                "allow_insecure_http=True допустим только в контролируемой тестовой среде"
            )
        return normalized.rstrip("/") + "/"

    @staticmethod
    def _is_loopback_host(hostname: str | None) -> bool:
        if hostname is None:
            return False
        if hostname.lower() == "localhost":
            return True
        try:
            return ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            return False

    def _build_url(self, api_version: str, endpoint: str) -> str:
        return f"{self.base_url}{api_version}/{endpoint.lstrip('/')}"

    def _handle_response(
        self,
        response: httpx.Response,
        endpoint: str,
        *,
        method_name: str | None = None,
    ) -> DecodedPayload:
        return self.response_decoder.decode(response, endpoint, method_name=method_name)

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self.client.aclose()

    @staticmethod
    def _attempt_timeout(
        timeout: float | None,
        remaining: float | None,
        connect_timeout: float | None = None,
    ) -> float | httpx.Timeout | None:
        if remaining is not None:
            timeout = remaining if timeout is None else min(timeout, remaining)
        if connect_timeout is None:
            return timeout
        # Недоступный хост обычно молча отбрасывает пакеты: без отдельного лимита
        # на подключение каждая попытка ждала бы полный timeout чтения.
        connect = connect_timeout if timeout is None else min(connect_timeout, timeout)
        return httpx.Timeout(timeout, connect=connect)

    async def request(
        self,
        request: PreparedRequest,
    ) -> dict[str, object]:
        prepared = request

        async def send(
            rate_attempt: int,
            rate_attempts: int,
            remaining: float | None,
        ) -> DecodedPayload | RateLimited:
            async with (
                self._concurrency_gate,
                self.client.stream(
                    prepared.method,
                    self._build_url(prepared.api_version, prepared.endpoint),
                    headers=prepared.headers,
                    params=cast(Mapping[str, str | int | float | bool | None], prepared.query)
                    or None,
                    data=prepared.form,
                    json=prepared.json_body,
                    timeout=self._attempt_timeout(
                        prepared.timeout, remaining, prepared.connect_timeout
                    ),
                    follow_redirects=False,
                ) as streamed_response,
            ):
                self.logger.info(
                    "Ответ HTTP: метод=%s операция=%s статус=%s",
                    prepared.method.upper(),
                    prepared.method_name,
                    streamed_response.status_code,
                )
                if (
                    streamed_response.status_code in RATE_LIMIT_STATUS_CODES
                    and rate_attempt < rate_attempts
                ):
                    with suppress(ResponseTooLargeError):
                        await self._response_reader.read(
                            streamed_response,
                            self._max_error_response_bytes,
                        )
                    return RATE_LIMITED
                content = await self._response_reader.read(
                    streamed_response,
                    self._max_json_response_bytes,
                )
                decoded_headers = httpx.Headers(streamed_response.headers)
                for header_name in ("content-encoding", "content-length", "transfer-encoding"):
                    decoded_headers.pop(header_name, None)
                response = httpx.Response(
                    streamed_response.status_code,
                    headers=decoded_headers,
                    content=content,
                    request=streamed_response.request,
                )
                return self.response_decoder.decode(
                    response,
                    prepared.endpoint,
                    method_name=prepared.method_name,
                )

        with self._connection_failures():
            payload = await self._retry.execute(
                method=prepared.method,
                operation_name=prepared.method_name,
                retry_class=prepared.retry_class,
                idempotent=prepared.idempotent,
                budget=prepared.operation_budget,
                attempt=send,
            )
        if not isinstance(payload, dict):
            raise ResponseShapeError("Ожидался ответ API в виде объекта JSON")
        return payload

    async def request_stream(
        self,
        request: PreparedRequest,
    ) -> bytes:
        result = await self._download(request, None)
        if not isinstance(result, bytes):
            raise ResponseShapeError("Ожидался результат потоковой загрузки в память")
        return result

    async def request_stream_to_file(
        self,
        request: PreparedRequest,
        target: FileTarget,
    ) -> Path:
        result = await self._download(request, target)
        if not isinstance(result, Path):
            raise ResponseShapeError("Ожидался результат потоковой загрузки в файл")
        return result

    async def _download(
        self,
        request: PreparedRequest,
        target: FileTarget | None,
    ) -> bytes | Path:
        parsed = urlsplit(request.endpoint)
        if parsed.scheme or parsed.netloc:
            raise RequestPreparationError(
                "Путь потоковой загрузки должен быть относительным к настроенному base_url"
            )

        async def send(
            rate_attempt: int,
            rate_attempts: int,
            remaining: float | None,
        ) -> bytes | Path | RateLimited:
            async with (
                self._concurrency_gate,
                self.client.stream(
                    request.method,
                    self._build_url(request.api_version, request.endpoint),
                    headers=request.headers,
                    params=cast(Mapping[str, str | int | float | bool | None], request.query)
                    or None,
                    data=request.form,
                    json=request.json_body,
                    timeout=self._attempt_timeout(
                        request.timeout, remaining, request.connect_timeout
                    ),
                    follow_redirects=False,
                ) as response,
            ):
                if response.status_code in RATE_LIMIT_STATUS_CODES and rate_attempt < rate_attempts:
                    return RATE_LIMITED
                return await self._download_handler.handle(response, request, target)

        with self._connection_failures():
            return await self._retry.execute(
                method=request.method,
                operation_name=request.method_name,
                retry_class=request.retry_class,
                idempotent=request.idempotent,
                budget=request.operation_budget,
                attempt=send,
            )

    @contextmanager
    def _connection_failures(self) -> Iterator[None]:
        """Заменить отказ подключения к серверу API на APIConnectionError.

        Отказ может прийти напрямую от httpx или как причина OperationTimeoutError,
        если общий лимит времени операции истёк между попытками подключения.
        """
        try:
            yield
        except CONNECTION_FAILURES as error:
            raise APIConnectionError(self._host) from error
        except OperationTimeoutError as error:
            if isinstance(error.__cause__, CONNECTION_FAILURES):
                raise APIConnectionError(self._host) from error
            raise


__all__ = ["AsyncHTTPClient", "AsyncTransport"]
