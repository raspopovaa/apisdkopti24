from __future__ import annotations

from typing import Any, TypeAlias, cast

import httpx

from .errors import build_api_error
from .logger import LoggerLike
from .logger import logger as default_logger

DecodedPayload: TypeAlias = dict[str, Any] | list[Any] | str | int | float | bool | None


class ResponseDecoder:
    def __init__(self, *, logger: LoggerLike | None = None) -> None:
        self._logger = logger or default_logger

    def parse(self, response: httpx.Response) -> DecodedPayload:
        try:
            return cast(DecodedPayload, response.json())
        except (ValueError, UnicodeDecodeError):
            return response.text

    def decode(
        self,
        response: httpx.Response,
        endpoint: str,
        *,
        method_name: str | None = None,
    ) -> DecodedPayload:
        body = self.parse(response)
        api_status_code, error_type = self._extract_status(body)

        if self._is_success(response.status_code, api_status_code):
            return body

        self._logger.error(
            "API request failed operation=%s http_status=%s api_status=%s error_type=%s",
            method_name or "unregistered",
            response.status_code,
            api_status_code,
            error_type,
        )
        raise build_api_error(
            status_code=response.status_code,
            body=body,
            endpoint=endpoint,
            method_name=method_name,
            http_status_code=response.status_code,
        )

    def decode_bytes(
        self,
        response: httpx.Response,
        content: bytes,
        endpoint: str,
        *,
        method_name: str | None = None,
    ) -> bytes:
        content_type = response.headers.get("content-type", "").lower()
        if 200 <= response.status_code < 300 and "json" not in content_type:
            return content
        self.decode(response, endpoint, method_name=method_name)
        return content

    @staticmethod
    def _extract_status(body: DecodedPayload) -> tuple[int | None, str | None]:
        if not isinstance(body, dict):
            return None, None
        status = body.get("status")
        if not isinstance(status, dict):
            return None, None
        raw_code = status.get("code")
        code = raw_code if isinstance(raw_code, int) else None
        errors = status.get("errors")
        if not isinstance(errors, list) or not errors or not isinstance(errors[0], dict):
            return code, None
        raw_type = errors[0].get("type")
        return code, raw_type if isinstance(raw_type, str) else None

    @staticmethod
    def _is_success(http_status_code: int, api_status_code: int | None) -> bool:
        http_success = 200 <= http_status_code < 300
        api_success = api_status_code is None or 200 <= api_status_code < 300
        return http_success and api_success
