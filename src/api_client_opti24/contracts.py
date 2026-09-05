from __future__ import annotations

from .registry import MethodRegistry


def serialize_registry_contract(registry: MethodRegistry) -> list[dict[str, object]]:
    return [
        {
            "name": spec.name,
            "domain": spec.domain,
            "default_version": spec.default_version,
            "supported_versions": list(spec.supported_versions),
            "idempotent": spec.idempotent,
            "requires_session": spec.requires_session,
            "timeout_class": spec.timeout_class,
            "retry_class": spec.retry_class,
            "routes": [
                {
                    "name": route.name,
                    "http_method": route.http_method,
                    "endpoint": route.endpoint,
                    "api_version": route.api_version,
                    "demo_available": route.demo_available,
                    "external_code": route.external_code,
                    "billable": route.billable,
                }
                for route in spec.iter_routes()
            ],
        }
        for spec in sorted(registry.list_all(), key=lambda item: item.name)
    ]


__all__ = ["serialize_registry_contract"]
