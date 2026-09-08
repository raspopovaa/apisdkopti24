from __future__ import annotations

import asyncio
import ipaddress
import time
from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urlsplit

import httpx

from .downloads import DownloadResponseHandler
from .environments import resolve_rate_limit_policy
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
        timeout: float | None = None,
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
        timeout: float | None = None,
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


class AsyncTransport:
    """HTTP adapter composed with independent resilience and file-writing policies."""

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
        max_in_memory_response_bytes: int = 64 * 1024 * 1024,
        max_error_response_bytes: int = 1024 * 1024,
    ) -> None:
        self.base_url = self._normalize_base_url(
            base_url,
            allow_insecure_http=allow_insecure_http,
        )
        self.client = http_client or httpx.AsyncClient(timeout=default_timeout)
        self._owns_http_client = http_client is None
        self.logger = logger or default_logger
        self.response_decoder = response_decoder or ResponseDecoder(logger=self.logger)
        self.retry_policy = retry_policy or RetryPolicy()
        configured_rate_limit = rate_limit_policy or RateLimitPolicy()
        self.rate_limit_policy = resolve_rate_limit_policy(self.base_url, configured_rate_limit)
        self.concurrency_policy = concurrency_policy or ConcurrencyPolicy()
        if max_in_memory_response_bytes < 1:
            raise ValueError("max_in_memory_response_bytes must be greater than zero")
        if max_error_response_bytes < 1:
            raise ValueError("max_error_response_bytes must be greater than zero")
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
            raise ValueError(
                "base_url is empty; set API_BASE_URL in .env or pass base_url explicitly"
            )
        parsed = urlsplit(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(
                "base_url must be an absolute URL starting with http:// or https://; "
                f"got {base_url!r}"
            )
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain credentials, query, or fragment")
        if (
            parsed.scheme == "http"
            and not allow_insecure_http
            and not AsyncTransport._is_loopback_host(parsed.hostname)
        ):
            raise ValueError(
                "base_url must use https:// for remote hosts; "
                "set allow_insecure_http=True only for controlled test environments"
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
    def _attempt_timeout(timeout: float | None, remaining: float | None) -> float | None:
        if remaining is None:
            return timeout
        return remaining if timeout is None else min(timeout, remaining)

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
            async with self._concurrency_gate:
                response = await self.client.request(
                    prepared.method,
                    self._build_url(prepared.api_version, prepared.endpoint),
                    headers=prepared.headers,
                    params=cast(Mapping[str, str | int | float | bool | None], prepared.query)
                    or None,
                    data=prepared.form,
                    json=prepared.json_body,
                    timeout=self._attempt_timeout(prepared.timeout, remaining),
                    follow_redirects=False,
                )
            self.logger.info(
                "HTTP method=%s operation=%s status=%s",
                prepared.method.upper(),
                prepared.method_name,
                response.status_code,
            )
            if response.status_code in RATE_LIMIT_STATUS_CODES and rate_attempt < rate_attempts:
                return RATE_LIMITED
            return self.response_decoder.decode(
                response,
                prepared.endpoint,
                method_name=prepared.method_name,
            )

        payload = await self._retry.execute(
            method=prepared.method,
            operation_name=prepared.method_name,
            retry_class=prepared.retry_class,
            idempotent=prepared.idempotent,
            budget=prepared.operation_budget,
            attempt=send,
        )
        if not isinstance(payload, dict):
            raise TypeError("Expected API response to be a JSON object")
        return payload

    async def request_stream(
        self,
        request: PreparedRequest,
    ) -> bytes:
        result = await self._download(request, None)
        if not isinstance(result, bytes):
            raise TypeError("Expected in-memory stream result")
        return result

    async def request_stream_to_file(
        self,
        request: PreparedRequest,
        target: FileTarget,
    ) -> Path:
        result = await self._download(request, target)
        if not isinstance(result, Path):
            raise TypeError("Expected file stream result")
        return result

    async def _download(
        self,
        request: PreparedRequest,
        target: FileTarget | None,
    ) -> bytes | Path:
        parsed = urlsplit(request.endpoint)
        if parsed.scheme or parsed.netloc:
            raise ValueError("stream endpoint must be relative to the configured base_url")

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
                    timeout=self._attempt_timeout(request.timeout, remaining),
                    follow_redirects=False,
                ) as response,
            ):
                if response.status_code in RATE_LIMIT_STATUS_CODES and rate_attempt < rate_attempts:
                    return RATE_LIMITED
                return await self._download_handler.handle(response, request, target)

        return await self._retry.execute(
            method=request.method,
            operation_name=request.method_name,
            retry_class=request.retry_class,
            idempotent=request.idempotent,
            budget=request.operation_budget,
            attempt=send,
        )


__all__ = ["AsyncHTTPClient", "AsyncTransport"]
