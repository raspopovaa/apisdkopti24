from __future__ import annotations

from typing import Any, TypeAlias, cast

import httpx

from .error_recognition import api_status_code, build_api_error

DecodedPayload: TypeAlias = dict[str, Any] | list[Any] | str | int | float | bool | None


class ResponseDecoder:
    """Разобрать ответ и проверить HTTP-статус вместе со статусом конверта API."""

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
        mutation: bool = False,
    ) -> DecodedPayload:
        body = self.parse(response)

        if self._is_success(response.status_code, api_status_code(body)):
            return body

        raise build_api_error(
            status_code=response.status_code,
            body=body,
            endpoint=endpoint,
            method_name=method_name,
            http_status_code=response.status_code,
            mutation=mutation,
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
    def _is_success(http_status_code: int, api_status_code: int | None) -> bool:
        http_success = 200 <= http_status_code < 300
        api_success = api_status_code is None or 200 <= api_status_code < 300
        return http_success and api_success
