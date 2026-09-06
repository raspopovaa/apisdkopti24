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

from .execution_budget import OperationBudget
from .file_io import AtomicFileWriter, FileWriter
from .logger import LoggerLike
from .logger import logger as default_logger
from .policies import ConcurrencyPolicy, RateLimitPolicy, RetryClass, RetryPolicy
from .requests import FileTarget, PreparedRequest
from .resilience import RATE_LIMITED, RateLimited, RateLimiter, RetryController
from .response import DecodedPayload, ResponseDecoder
from .runtime import Clock
from .session import RequestContext


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
        self.rate_limit_policy = rate_limit_policy or RateLimitPolicy()
        self.concurrency_policy = concurrency_policy or ConcurrencyPolicy()
        self._clock = clock or _InjectedClock(monotonic, sleep)
        self._concurrency_gate = asyncio.Semaphore(self.concurrency_policy.max_in_flight)
        self._file_writer = file_writer or AtomicFileWriter()
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
        self._default_timeout = default_timeout

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

    def _legacy_request(
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
    ) -> PreparedRequest:
        budget = operation_budget or OperationBudget(
            deadline_at=self._clock.monotonic() + (timeout or self._default_timeout),
            max_attempts=max(
                1, self.retry_policy.network_attempts * self.retry_policy.rate_limit_attempts
            ),
        )
        return PreparedRequest(
            method=method,
            endpoint=endpoint,
            api_version=api_version,
            headers=dict(headers or {}),
            query={},
            form=None,
            json_body=None,
            timeout=timeout or self._default_timeout,
            method_name=method_name or "unregistered",
            retry_class=(retry_class.value if isinstance(retry_class, RetryClass) else retry_class)
            or "safe",
            idempotent=(
                (method.upper() in {"GET", "HEAD", "OPTIONS"}) if idempotent is None else idempotent
            ),
            request_context=RequestContext(None, None, 0),
            operation_budget=budget,
        )

    async def request(
        self,
        request: PreparedRequest | str,
        endpoint: str | None = None,
        *,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        method_name: str | None = None,
        retry_class: str | RetryClass | None = None,
        idempotent: bool | None = None,
        operation_budget: OperationBudget | None = None,
    ) -> dict[str, object]:
        prepared = (
            request
            if isinstance(request, PreparedRequest)
            else self._legacy_request(
                request,
                endpoint or "",
                api_version=api_version,
                headers=headers,
                timeout=timeout,
                method_name=method_name,
                retry_class=retry_class,
                idempotent=idempotent,
                operation_budget=operation_budget,
            )
        )

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
                )
            self.logger.info(
                "HTTP method=%s operation=%s status=%s",
                prepared.method.upper(),
                prepared.method_name,
                response.status_code,
            )
            if response.status_code in {429, 509} and rate_attempt < rate_attempts:
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
        request: PreparedRequest | str,
        endpoint: str | None = None,
        *,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        method_name: str | None = None,
        retry_class: str | RetryClass | None = None,
        idempotent: bool | None = None,
        operation_budget: OperationBudget | None = None,
    ) -> bytes:
        prepared = (
            request
            if isinstance(request, PreparedRequest)
            else self._legacy_request(
                request,
                endpoint or "",
                api_version=api_version,
                headers=headers,
                timeout=timeout,
                method_name=method_name,
                retry_class=retry_class,
                idempotent=idempotent,
                operation_budget=operation_budget,
            )
        )
        result = await self._download(prepared, None)
        if not isinstance(result, bytes):
            raise TypeError("Expected in-memory stream result")
        return result

    async def request_stream_to_file(
        self,
        request: PreparedRequest | str,
        endpoint_or_target: str | FileTarget,
        destination: str | Path | None = None,
        *,
        api_version: str = "v1",
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        method_name: str | None = None,
        retry_class: str | RetryClass | None = None,
        idempotent: bool | None = None,
        operation_budget: OperationBudget | None = None,
        chunk_size: int = 64 * 1024,
        write_buffer_size: int = 1024 * 1024,
    ) -> Path:
        if isinstance(request, PreparedRequest):
            if not isinstance(endpoint_or_target, FileTarget):
                raise TypeError("PreparedRequest requires a FileTarget")
            prepared = request
            target = endpoint_or_target
        else:
            if destination is None or isinstance(endpoint_or_target, FileTarget):
                raise TypeError("Legacy stream request requires endpoint and destination")
            prepared = self._legacy_request(
                request,
                endpoint_or_target,
                api_version=api_version,
                headers=headers,
                timeout=timeout,
                method_name=method_name,
                retry_class=retry_class,
                idempotent=idempotent,
                operation_budget=operation_budget,
            )
            target = FileTarget(Path(destination), chunk_size, write_buffer_size)
        result = await self._download(prepared, target)
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
                ) as response,
            ):
                if response.status_code in {429, 509} and rate_attempt < rate_attempts:
                    await response.aread()
                    return RATE_LIMITED
                content_type = response.headers.get("content-type", "").lower()
                if not 200 <= response.status_code < 300 or "json" in content_type:
                    content = await response.aread()
                    self.response_decoder.decode_bytes(
                        response,
                        content,
                        request.endpoint,
                        method_name=request.method_name,
                    )
                    if target is None:
                        return content
                    return await self._file_writer.write_bytes(target.destination, content)
                if target is None:
                    return await response.aread()
                return await self._file_writer.write_stream(
                    target.destination,
                    response.aiter_bytes(target.chunk_size),
                    write_buffer_size=target.write_buffer_size,
                )

        return await self._retry.execute(
            method=request.method,
            operation_name=request.method_name,
            retry_class=request.retry_class,
            idempotent=request.idempotent,
            budget=request.operation_budget,
            attempt=send,
        )


__all__ = ["AsyncHTTPClient", "AsyncTransport"]
