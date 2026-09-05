from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import (
    ContractCatalog,
    ContractDecision,
    ContractManifest,
    FieldContract,
    OperationContract,
    VariantContract,
)

_ALLOWED_VERIFICATION = {"provisional", "verified", "accepted", "unsupported", "excluded"}
_ALLOWED_RESPONSE_KINDS = {"pydantic", "mapping", "binary"}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Cannot load YAML contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"YAML contract must contain an object: {path}")
    return value


def _field(value: dict[str, Any], *, location: str) -> FieldContract:
    path = value.get("path")
    api_type = value.get("api_type")
    if not isinstance(path, str) or not path:
        raise ValueError(f"Missing field path at {location}")
    if not isinstance(api_type, str) or not api_type:
        raise ValueError(f"Missing api_type for {path} at {location}")
    required = value.get("required")
    if required is not None and not isinstance(required, bool):
        raise ValueError(f"required must be bool or null for {path} at {location}")
    return FieldContract(
        path=path,
        api_type=api_type,
        required=required,
        description=str(value.get("description") or ""),
    )


def _decision(value: dict[str, Any], *, location: str) -> ContractDecision:
    path = value.get("path")
    status = value.get("status")
    reason = value.get("reason")
    if not all(isinstance(item, str) and item for item in (path, status, reason)):
        raise ValueError(f"Invalid decision at {location}")
    return ContractDecision(
        path=path,
        status=status,
        reason=reason,
        spec_type=value.get("spec_type"),
        model_type=value.get("model_type"),
    )


def _variant(value: dict[str, Any], *, repository_root: Path, location: str) -> VariantContract:
    route_name = value.get("route_name")
    if not isinstance(route_name, str) or not route_name:
        raise ValueError(f"Missing route_name at {location}")
    fixture_value = value.get("fixture")
    fixture = repository_root / fixture_value if isinstance(fixture_value, str) else None
    return VariantContract(
        route_name=route_name,
        source_section=str(value.get("source_section") or ""),
        request_line=str(value.get("request_line") or ""),
        request_parameters=tuple(
            _field(item, location=f"{location}.request_parameters")
            for item in value.get("request_parameters", [])
        ),
        response_fields=tuple(
            _field(item, location=f"{location}.response_fields")
            for item in value.get("response_fields", [])
        ),
        fixture=fixture,
        fixture_status=str(value.get("fixture_status") or "unavailable"),
        fixture_corrections=tuple(value.get("fixture_corrections", [])),
        fixture_note=value.get("fixture_note"),
    )


def load_catalog(contract_root: Path, *, repository_root: Path | None = None) -> ContractCatalog:
    contract_root = contract_root.resolve()
    repository_root = (repository_root or contract_root.parents[2]).resolve()
    manifest_value = _load_yaml(contract_root / "manifest.yaml")
    source = manifest_value.get("source")
    if not isinstance(source, dict):
        raise ValueError("Manifest source must be an object")
    source_version = source.get("version")
    if source_version != "1.1.60":
        raise ValueError(f"Unexpected contract source version: {source_version!r}")

    domain_files = manifest_value.get("domain_files", [])
    if not isinstance(domain_files, list) or not all(
        isinstance(item, str) for item in domain_files
    ):
        raise ValueError("Manifest domain_files must be a string list")

    common_response_fields = tuple(
        _field(item, location="manifest.common_response_fields")
        for item in manifest_value.get("common_response_fields", [])
    )
    manifest = ContractManifest(
        root=contract_root,
        schema_version=int(manifest_value.get("schema_version", 0)),
        source=source,
        domain_files=tuple(domain_files),
        excluded_operations=frozenset(manifest_value.get("excluded_operations", [])),
        expected_operation_count=int(manifest_value.get("expected_operation_count", 0)),
        common_response_fields=common_response_fields,
    )

    operations: dict[str, OperationContract] = {}
    for filename in manifest.domain_files:
        domain_path = contract_root / filename
        domain_value = _load_yaml(domain_path)
        domain = domain_value.get("domain")
        if not isinstance(domain, str) or not domain:
            raise ValueError(f"Missing domain in {domain_path}")
        raw_operations = domain_value.get("operations")
        if not isinstance(raw_operations, dict):
            raise ValueError(f"operations must be an object in {domain_path}")
        for operation_name, raw_operation in raw_operations.items():
            if operation_name in operations:
                raise ValueError(f"Duplicate operation contract: {operation_name}")
            if operation_name in manifest.excluded_operations:
                raise ValueError(f"Excluded operation must not be normalized: {operation_name}")
            if not isinstance(raw_operation, dict):
                raise ValueError(f"Operation {operation_name} must be an object")
            verification = raw_operation.get("verification")
            if verification not in _ALLOWED_VERIFICATION:
                raise ValueError(
                    f"Unsupported verification status {verification!r} for {operation_name}"
                )
            response_kind = raw_operation.get("response_kind", "pydantic")
            if response_kind not in _ALLOWED_RESPONSE_KINDS:
                raise ValueError(
                    f"Unsupported response kind {response_kind!r} for {operation_name}"
                )
            variants_value = raw_operation.get("variants", [])
            if not isinstance(variants_value, list) or not variants_value:
                raise ValueError(f"Operation {operation_name} must contain variants")
            variants = tuple(
                _variant(
                    item,
                    repository_root=repository_root,
                    location=f"{filename}.{operation_name}.variants",
                )
                for item in variants_value
            )
            route_names = [variant.route_name for variant in variants]
            if len(route_names) != len(set(route_names)):
                raise ValueError(f"Duplicate route variant for {operation_name}")
            operations[operation_name] = OperationContract(
                name=operation_name,
                summary=str(raw_operation.get("summary") or ""),
                verification=verification,
                service=str(raw_operation.get("service") or domain),
                request_model=raw_operation.get("request_model"),
                response_kind=response_kind,
                variants=variants,
                decisions=tuple(
                    _decision(item, location=f"{filename}.{operation_name}.decisions")
                    for item in raw_operation.get("decisions", [])
                ),
                source_decisions=tuple(
                    _decision(item, location=f"{filename}.{operation_name}.source_decisions")
                    for item in raw_operation.get("source_decisions", [])
                ),
            )

    if len(operations) != manifest.expected_operation_count:
        raise ValueError(
            "Normalized operation count does not match manifest: "
            f"expected {manifest.expected_operation_count}, got {len(operations)}"
        )
    return ContractCatalog(manifest=manifest, operations=operations)
