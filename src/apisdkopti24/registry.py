from __future__ import annotations

import importlib
import pkgutil

from .endpoints import EndpointSpec, RouteVariant
from .operations import OperationSpec

MethodSpec = OperationSpec


class MethodRegistry:
    def __init__(self, specs: dict[str, OperationSpec[object]] | None = None) -> None:
        self._specs = dict(specs or {})

    def register(self, spec: OperationSpec[object]) -> None:
        if spec.name in self._specs:
            raise ValueError(f"Method '{spec.name}' is already registered")
        route_keys = [(route.name, route.api_version) for route in spec.iter_routes()]
        if len(route_keys) != len(set(route_keys)):
            raise ValueError(f"Method '{spec.name}' contains duplicate named routes")
        if not spec.supports(spec.default_version):
            raise ValueError(f"Method '{spec.name}' default version is not listed as supported")
        self._specs[spec.name] = spec

    def get(self, name: str) -> OperationSpec[object]:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"Method '{name}' is not registered") from exc

    def find_by_endpoint(
        self,
        endpoint: str,
        version: str,
        http_method: str | None = None,
    ) -> OperationSpec[object] | None:
        normalized_method = http_method.upper() if http_method is not None else None
        matches = [
            spec
            for spec in self._specs.values()
            if any(
                route.endpoint == endpoint
                and route.supports(version)
                and (normalized_method is None or route.http_method == normalized_method)
                for route in spec.iter_routes()
            )
        ]
        if not matches:
            return None
        return sorted(
            matches,
            key=lambda spec: (
                not spec.idempotent,
                spec.http_method != "GET",
                spec.name,
            ),
        )[0]

    def list_domain(self, domain: str) -> tuple[OperationSpec[object], ...]:
        return tuple(spec for spec in self._specs.values() if spec.domain == domain)

    def list_all(self) -> tuple[OperationSpec[object], ...]:
        return tuple(self._specs.values())


def build_default_registry() -> MethodRegistry:
    from . import services
    from .authentication import AUTH_USER

    declared: dict[str, OperationSpec[object]] = {AUTH_USER.name: AUTH_USER}
    for module_info in pkgutil.iter_modules(services.__path__):
        module = importlib.import_module(f"{services.__name__}.{module_info.name}")
        for candidate in vars(module).values():
            if isinstance(candidate, OperationSpec):
                declared[candidate.name] = candidate

    registry = MethodRegistry()
    for spec in declared.values():
        registry.register(spec)
    return registry


__all__ = [
    "EndpointSpec",
    "MethodRegistry",
    "MethodSpec",
    "OperationSpec",
    "RouteVariant",
    "build_default_registry",
]
