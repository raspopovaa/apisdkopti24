from __future__ import annotations

import asyncio
import ipaddress
import os
import random
import tempfile
import time
from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Any, Protocol, TypeVar, cast
from urllib.parse import urlsplit

import httpx

from .execution_budget import OperationBudget
from .logger import LoggerLike
from .logger import logger as default_logger
from .policies import (
    IDEMPOTENT_HTTP_METHODS,
    SAFE_HTTP_METHODS,
    ConcurrencyPolicy,
    RateLimitPolicy,
    RetryClass,
    RetryPolicy,
)
from .response import DecodedPayload, ResponseDecoder
from .runtime import Clock


class AsyncHTTPClient(Protocol):
    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response: ...

    def stream(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> AbstractAsyncContextManager[httpx.Response]: ...

    async def aclose(self) -> None: ...


AsyncSleep = Callable[[float], Awaitable[None]]
Jitter = Callable[[float], float]
ResultT = TypeVar("ResultT")
_RATE_LIMITED = object()


class AsyncTransport:
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
        logger: LoggerLike | None = None,
        clock: Clock | None = None,
        sleep: AsyncSleep = asyncio.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        jitter: Jitter | None = None,
    ):
        self.base_url = self._normalize_base_url(
            base_url,
            allow_insecure_http=allow_insecure_http,
        )
        self.client = http_client or httpx.AsyncClient(timeout=default_timeout)
        self._owns_http_client = http_client is None
        self.logger: LoggerLike = logger or default_logger
        self.response_decoder = response_decoder or ResponseDecoder(logger=self.logger)
        self.retry_policy = retry_policy or RetryPolicy()
        self.rate_limit_policy = rate_limit_policy or RateLimitPolicy()
        self.concurrency_policy = concurrency_policy or ConcurrencyPolicy()
        self._sleep = clock.sleep if clock is not None else sleep
        self._monotonic = clock.monotonic if clock is not None else monotonic
        self._jitter = jitter or (lambda cap: random.uniform(0.0, cap))
        self._rate_limit_lock = asyncio.Lock()
        self._auth_limit_lock = asyncio.Lock()
        self._concurrency_gate = asyncio.Semaphore(self.concurrency_policy.max_in_flight)
        self._last_request_started_at: float | None = None
        self._last_auth_request_started_at: float | None = None

    @staticmethod
    def _normalize_base_url(
        base_url: str,
        *,
        allow_insecure_http: bool = False,
    ) -> str:
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

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self.client.aclose()

    @staticmethod
    def _ensure_delay_fits(operation_budget: OperationBudget | None, delay: float) -> None:
        if operation_budget is not None:
            operation_budget.ensure_delay_fits(time.monotonic(), delay)

    async def _wait_for_rate_limit(self, operation_budget: OperationBudget | None) -> None:
        minimum_interval = self.rate_limit_policy.minimum_interval_seconds
        if minimum_interval <= 0:
            return
        async with self._rate_limit_lock:
            now = self._monotonic()
            if self._last_request_started_at is not None:
                wait_seconds = self._last_request_started_at + minimum_interval - now
                if wait_seconds > 0:
                    if operation_budget is not None:
                        operation_budget.ensure_delay_fits(now, wait_seconds)
                    await self._sleep(wait_seconds)
                    now = self._monotonic()
            self._last_request_started_at = now

    async def _wait_for_auth_limit(
        self,
        retry_class: str | RetryClass,
        operation_budget: OperationBudget | None,
    ) -> None:
        if RetryClass.normalize(retry_class) is not RetryClass.NETWORK_ONLY:
            return
        minimum_interval = self.retry_policy.auth_retry_min_interval_seconds
        if minimum_interval <= 0:
            return
        async with self._auth_limit_lock:
            now = self._monotonic()
            if self._last_auth_request_started_at is not None:
                wait_seconds = self._last_auth_request_started_at + minimum_interval - now
                if wait_seconds > 0:
                    if operation_budget is not None:
                        operation_budget.ensure_delay_fits(now, wait_seconds)
                    await self._sleep(wait_seconds)
                    now = self._monotonic()
            self._last_auth_request_started_at = now

    def _handle_response(
        self,
        resp: httpx.Response,
        endpoint: str,
        *,
        method_name: str | None = None,
    ) -> DecodedPayload:
        return self.response_decoder.decode(resp, endpoint, method_name=method_name)

    def _resolve_retry_settings(
        self,
        method: str,
        retry_class: str | RetryClass | None,
        idempotent: bool | None,
    ) -> tuple[str, str | RetryClass, int, int]:
        normalized_method = method.upper()
        resolved_retry_class = retry_class or (
            RetryClass.SAFE.value
            if normalized_method in SAFE_HTTP_METHODS
            else RetryClass.NEVER.value
        )
        resolved_idempotent = (
            normalized_method in IDEMPOTENT_HTTP_METHODS if idempotent is None else idempotent
        )
        return (
            normalized_method,
            resolved_retry_class,
            self.retry_policy.network_attempt_count(
                resolved_retry_class,
                normalized_method,
                idempotent=resolved_idempotent,
            ),
            self.retry_policy.rate_limit_attempt_count(
                resolved_retry_class,
                normalized_method,
                idempotent=resolved_idempotent,
            ),
        )

    async def _run_with_retries(
        self,
        *,
        method: str,
        method_name: str | None,
        retry_class: str | RetryClass | None,
        idempotent: bool | None,
        operation_budget: OperationBudget | None,
        attempt: Callable[[int, int, float | None], Awaitable[ResultT | object]],
    ) -> ResultT:
        (
            normalized_method,
            resolved_retry_class,
            network_attempts,
            rate_limit_attempts,
        ) = self._resolve_retry_settings(method, retry_class, idempotent)
        network_backoff_cap = self.retry_policy.initial_network_backoff(resolved_retry_class)

        for network_attempt in range(1, network_attempts + 1):
            try:
                for rate_attempt in range(1, rate_limit_attempts + 1):
                    await self._wait_for_rate_limit(operation_budget)
                    await self._wait_for_auth_limit(resolved_retry_class, operation_budget)
                    remaining = (
                        operation_budget.claim_attempt(self._monotonic())
                        if operation_budget is not None
                        else None
                    )
                    result = await attempt(rate_attempt, rate_limit_attempts, remaining)
                    if result is not _RATE_LIMITED:
                        return cast(ResultT, result)
                    base = self.retry_policy.rate_limit_backoff_seconds * rate_attempt
                    delay = self._jitter(base)
                    if operation_budget is not None:
                        operation_budget.ensure_delay_fits(self._monotonic(), delay)
                    self.logger.warning(
                        "Rate limit method=%s operation=%s attempt=%s/%s backoff=%.2fs",
                        normalized_method,
                        method_name or "unregistered",
                        rate_attempt,
                        rate_limit_attempts,
                        delay,
                    )
                    await self._sleep(delay)
                raise RuntimeError("Rate limit retry loop exhausted unexpectedly")
            except httpx.RequestError:
                if network_attempt >= network_attempts:
                    raise
                delay = self._jitter(network_backoff_cap)
                if operation_budget is not None:
                    operation_budget.ensure_delay_fits(self._monotonic(), delay)
                self.logger.warning(
                    "Network error method=%s operation=%s attempt=%s/%s backoff=%.2fs",
                    normalized_method,
                    method_name or "unregistered",
                    network_attempt,
                    network_attempts,
                    delay,
                )
                await self._sleep(delay)
                network_backoff_cap = min(
                    network_backoff_cap * 2,
                    self.retry_policy.network_backoff_max_seconds,
                )
        raise RuntimeError("Network retry loop exhausted unexpectedly")

    @staticmethod
    def _attempt_timeout(timeout: float | None, remaining: float | None) -> float | None:
        if remaining is None:
            return timeout
        if timeout is None:
            return remaining
        return min(timeout, remaining)

    async def request(
        self,
        method: str,
        endpoint: str,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        method_name: str | None = None,
        retry_class: str | RetryClass | None = None,
        idempotent: bool | None = None,
        operation_budget: OperationBudget | None = None,
        **kwargs: Any,
    ) -> DecodedPayload:
        url = self._build_url(api_version, endpoint)

        async def send(
            rate_attempt: int,
            rate_limit_attempts: int,
            remaining: float | None,
        ) -> DecodedPayload | object:
            async with self._concurrency_gate:
                response = await self.client.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self._attempt_timeout(timeout, remaining),
                    **kwargs,
                )
            self.logger.info(
                "HTTP method=%s operation=%s status=%s",
                method.upper(),
                method_name or "unregistered",
                response.status_code,
            )
            if response.status_code in {429, 509} and rate_attempt < rate_limit_attempts:
                return _RATE_LIMITED
            return self._handle_response(response, endpoint, method_name=method_name)

        return await self._run_with_retries(
            method=method,
            method_name=method_name,
            retry_class=retry_class,
            idempotent=idempotent,
            operation_budget=operation_budget,
            attempt=send,
        )

    async def request_stream(
        self,
        method: str,
        endpoint: str,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        *,
        timeout: float | None = None,
        method_name: str | None = None,
        retry_class: str | RetryClass | None = None,
        idempotent: bool | None = None,
        operation_budget: OperationBudget | None = None,
        **kwargs: Any,
    ) -> bytes:
        result = await self._download_stream(
            method,
            endpoint,
            api_version=api_version,
            headers=headers,
            timeout=timeout,
            method_name=method_name,
            retry_class=retry_class,
            idempotent=idempotent,
            operation_budget=operation_budget,
            destination=None,
            **kwargs,
        )
        if not isinstance(result, bytes):
            raise TypeError("Expected in-memory stream result")
        return result

    async def request_stream_to_file(
        self,
        method: str,
        endpoint: str,
        destination: str | Path,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        *,
        timeout: float | None = None,
        method_name: str | None = None,
        retry_class: str | RetryClass | None = None,
        idempotent: bool | None = None,
        operation_budget: OperationBudget | None = None,
        chunk_size: int = 64 * 1024,
        write_buffer_size: int = 1024 * 1024,
        **kwargs: Any,
    ) -> Path:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if write_buffer_size <= 0:
            raise ValueError("write_buffer_size must be greater than zero")
        result = await self._download_stream(
            method,
            endpoint,
            api_version=api_version,
            headers=headers,
            timeout=timeout,
            method_name=method_name,
            retry_class=retry_class,
            idempotent=idempotent,
            operation_budget=operation_budget,
            destination=Path(destination),
            chunk_size=chunk_size,
            write_buffer_size=write_buffer_size,
            **kwargs,
        )
        if not isinstance(result, Path):
            raise TypeError("Expected file stream result")
        return result

    async def _download_stream(
        self,
        method: str,
        endpoint: str,
        *,
        api_version: str,
        headers: Mapping[str, str] | None,
        timeout: float | None,
        method_name: str | None,
        retry_class: str | RetryClass | None,
        idempotent: bool | None,
        operation_budget: OperationBudget | None,
        destination: Path | None,
        chunk_size: int = 64 * 1024,
        write_buffer_size: int = 1024 * 1024,
        **kwargs: Any,
    ) -> bytes | Path:
        parsed = urlsplit(endpoint)
        if parsed.scheme or parsed.netloc:
            raise ValueError("stream endpoint must be relative to the configured base_url")
        url = self._build_url(api_version, endpoint)

        async def send(
            rate_attempt: int,
            rate_limit_attempts: int,
            remaining: float | None,
        ) -> bytes | Path | object:
            async with (
                self._concurrency_gate,
                self.client.stream(
                    method,
                    url,
                    headers=headers,
                    timeout=self._attempt_timeout(timeout, remaining),
                    **kwargs,
                ) as resp,
            ):
                if resp.status_code in {429, 509} and rate_attempt < rate_limit_attempts:
                    await resp.aread()
                    return _RATE_LIMITED
                content_type = resp.headers.get("content-type", "").lower()
                if not 200 <= resp.status_code < 300 or "json" in content_type:
                    content = await resp.aread()
                    self.response_decoder.decode_bytes(
                        resp,
                        content,
                        url,
                        method_name=method_name,
                    )
                    if destination is None:
                        return content
                    return await self._write_bytes_atomically(destination, content)
                if destination is None:
                    return await resp.aread()
                return await self._write_stream_atomically(
                    destination,
                    resp,
                    chunk_size=chunk_size,
                    write_buffer_size=write_buffer_size,
                )

        return await self._run_with_retries(
            method=method,
            method_name=method_name,
            retry_class=retry_class,
            idempotent=idempotent,
            operation_budget=operation_budget,
            attempt=send,
        )

    @staticmethod
    async def _write_bytes_atomically(destination: Path, content: bytes) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = AsyncTransport._temporary_path(destination)
        try:
            await asyncio.to_thread(temporary.write_bytes, content)
            await asyncio.to_thread(os.replace, temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        return destination

    @staticmethod
    async def _write_stream_atomically(
        destination: Path,
        response: httpx.Response,
        *,
        chunk_size: int,
        write_buffer_size: int,
    ) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = AsyncTransport._temporary_path(destination)
        try:
            with temporary.open("wb") as output:
                buffer = bytearray()
                async for chunk in response.aiter_bytes(chunk_size):
                    buffer.extend(chunk)
                    if len(buffer) >= write_buffer_size:
                        await asyncio.to_thread(output.write, bytes(buffer))
                        buffer.clear()
                if buffer:
                    await asyncio.to_thread(output.write, bytes(buffer))
            await asyncio.to_thread(os.replace, temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        return destination

    @staticmethod
    def _temporary_path(destination: Path) -> Path:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".part",
            delete=False,
        ) as temporary:
            return Path(temporary.name)
