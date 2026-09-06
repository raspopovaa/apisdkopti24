from __future__ import annotations

from dataclasses import dataclass
from string import Formatter
from typing import Generic, Literal, TypeVar, cast

from .endpoints import RouteVariant, endpoint_metadata
from .request_metadata import request_spec_for
from .requests import RequestContract

ResponseT = TypeVar("ResponseT", covariant=True)
ResponseKind = Literal["json", "bytes"]


@dataclass(frozen=True, slots=True)
class OperationSpec(Generic[ResponseT]):
    """Complete executable API contract for one SDK operation."""

    name: str
    response_type: type[ResponseT] | None
    domain: str
    http_method: str
    endpoint: str
    supported_versions: tuple[str, ...]
    default_version: str
    demo_available: bool
    idempotent: bool
    requires_session: bool = True
    timeout_class: str = "default"
    retry_class: str = "safe"
    route_variants: tuple[RouteVariant, ...] = ()
    external_code: str | None = None
    billable: bool | None = None
    response_kind: ResponseKind = "json"
    request: RequestContract = RequestContract()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("operation name cannot be empty")
        if self.response_kind == "json" and self.response_type is None:
            raise ValueError("JSON operation requires a response type")
        if (self.external_code is None) != (self.billable is None):
            raise ValueError("external_code and billable must be configured together")
        route_keys = [(route.name, route.api_version) for route in self.iter_routes()]
        if len(route_keys) != len(set(route_keys)):
            raise ValueError(f"Operation {self.name!r} contains duplicate named routes")
        if not self.supports(self.default_version):
            raise ValueError(f"Operation {self.name!r} does not support its default version")
        routes_have_path = {
            any(field is not None for _, field, _, _ in Formatter().parse(route.endpoint))
            for route in self.iter_routes()
        }
        if routes_have_path != {self.request.has_path}:
            raise ValueError(
                f"Operation {self.name!r} request path metadata does not match its routes"
            )

    def supports(self, version: str) -> bool:
        return version in self.supported_versions

    def iter_routes(self) -> tuple[RouteVariant, ...]:
        primary = RouteVariant(
            http_method=self.http_method,
            endpoint=self.endpoint,
            api_version=self.default_version,
            demo_available=self.demo_available,
            name="default",
            external_code=self.external_code,
            billable=self.billable,
        )
        return (primary, *self.route_variants)

    def resolve_route(
        self,
        *,
        api_version: str | None = None,
        route_name: str = "default",
    ) -> RouteVariant:
        version = api_version or self.default_version
        matches = [
            route
            for route in self.iter_routes()
            if route.name == route_name and route.supports(version)
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Operation {self.name!r} has no unique route "
                f"name={route_name!r} version={version!r}"
            )
        return matches[0]


def _bind_response(
    metadata: dict[str, object],
    response_type: type[ResponseT] | None,
    response_kind: ResponseKind,
) -> OperationSpec[ResponseT]:
    return OperationSpec(
        name=cast(str, metadata["name"]),
        response_type=response_type,
        response_kind=response_kind,
        domain=cast(str, metadata["domain"]),
        http_method=cast(str, metadata["http_method"]),
        endpoint=cast(str, metadata["endpoint"]),
        supported_versions=cast(tuple[str, ...], metadata["supported_versions"]),
        default_version=cast(str, metadata["default_version"]),
        demo_available=cast(bool, metadata["demo_available"]),
        idempotent=cast(bool, metadata["idempotent"]),
        requires_session=cast(bool, metadata["requires_session"]),
        timeout_class=cast(str, metadata["timeout_class"]),
        retry_class=cast(str, metadata["retry_class"]),
        route_variants=cast(tuple[RouteVariant, ...], metadata["route_variants"]),
        external_code=cast(str | None, metadata["external_code"]),
        billable=cast(bool | None, metadata["billable"]),
        request=request_spec_for(cast(str, metadata["name"])),
    )


def operation(name: str, response_type: type[ResponseT]) -> OperationSpec[ResponseT]:
    return _bind_response(endpoint_metadata(name), response_type, "json")


def binary_operation(name: str) -> OperationSpec[bytes]:
    return _bind_response(endpoint_metadata(name), None, "bytes")


Operation = OperationSpec

__all__ = ["Operation", "OperationSpec", "ResponseKind", "binary_operation", "operation"]
