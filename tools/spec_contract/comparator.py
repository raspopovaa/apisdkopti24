from __future__ import annotations

import inspect
import json
from decimal import Decimal
from pathlib import Path
from typing import Any, get_origin

from pydantic import ValidationError

from .models import (
    AuditIssue,
    AuditResult,
    ContractCatalog,
    FieldContract,
    OperationContract,
    Severity,
)
from .runtime import (
    format_annotation,
    request_model_usage,
    resolve_model_field,
    resolve_object,
    resolve_response_model,
    resolve_return_annotation,
    resolve_service_method,
    untyped_model_fields,
    unwrap_optional,
)
from .sanitizer import find_sensitive_values


def _base_api_type(value: str) -> str:
    normalized = value.strip().lower().replace("–", "-")
    for separator in (" ", "(", "/"):
        normalized = normalized.split(separator, 1)[0]
    return normalized


def _python_type_matches(api_type: str, annotation: Any) -> bool:
    annotation = unwrap_optional(annotation)
    origin = get_origin(annotation)
    normalized = _base_api_type(api_type)
    if annotation is Any:
        return True
    if normalized in {"mixed", "unknown", ""}:
        return True
    if normalized == "json":
        return origin in {list, dict, tuple} or inspect.isclass(annotation)
    if normalized == "string":
        return annotation is str or getattr(annotation, "__name__", "") in {"date", "datetime"}
    if normalized == "uint":
        return annotation is int
    if normalized == "float":
        return annotation in {float, int, Decimal}
    if normalized == "bool":
        return annotation is bool
    if normalized == "byte":
        return annotation in {bytes, str}
    return True


def _is_accepted(operation: OperationContract, path: str, code: str) -> bool:
    for decision in operation.decisions:
        if decision.path == path and decision.status == "accepted":
            return True
        if decision.path == f"{code}:{path}" and decision.status == "accepted":
            return True
    return False


def _issue(
    operation: OperationContract,
    *,
    code: str,
    severity: Severity,
    message: str,
    path: str | None = None,
    expected: str | None = None,
    actual: str | None = None,
    always_blocking: bool = False,
) -> AuditIssue:
    accepted = path is not None and _is_accepted(operation, path, code)
    blocking = always_blocking or (
        operation.verification == "verified" and severity == "error" and not accepted
    )
    return AuditIssue(
        code=code,
        severity=severity,
        message=message,
        operation=operation.name,
        path=path,
        expected=expected,
        actual=actual,
        blocking=blocking,
    )


def _compare_field(
    result: AuditResult,
    operation: OperationContract,
    response_model: type,
    field: FieldContract,
) -> None:
    resolved = resolve_model_field(response_model, field.path)
    if resolved is None:
        result.add(
            _issue(
                operation,
                code="missing_response_field",
                severity="error" if field.required else "warning",
                message="Поле спецификации отсутствует в Pydantic-модели ответа.",
                path=field.path,
                expected=field.api_type,
                actual="missing",
            )
        )
        return
    actual_type = format_annotation(resolved.annotation)
    if resolved.generic:
        result.add(
            _issue(
                operation,
                code="untyped_response_structure",
                severity="warning",
                message="Поле разрешается через Any или нетипизированный dict.",
                path=field.path,
                expected=field.api_type,
                actual=actual_type,
            )
        )
    if not _python_type_matches(field.api_type, resolved.annotation):
        result.add(
            _issue(
                operation,
                code="response_type_mismatch",
                severity="error",
                message="Тип спецификации не совпадает с Python-типом модели.",
                path=field.path,
                expected=field.api_type,
                actual=actual_type,
            )
        )
    if (
        field.required is not None
        and resolved.required is not None
        and field.required != resolved.required
    ):
        result.add(
            _issue(
                operation,
                code="response_required_mismatch",
                severity="error",
                message="Обязательность поля отличается от спецификации.",
                path=field.path,
                expected=str(field.required),
                actual=str(resolved.required),
            )
        )


def _audit_request_signature(
    result: AuditResult,
    operation: OperationContract,
    method: Any,
    field: FieldContract,
) -> None:
    name = field.path.split(".", 1)[0].removesuffix("[]")
    signature = inspect.signature(method)
    if name in signature.parameters:
        return
    result.add(
        _issue(
            operation,
            code="request_parameter_mapping_missing",
            severity="info",
            message="Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление.",
            path=field.path,
            expected=name,
            actual="not exposed by the same name",
        )
    )


def _audit_fixture(
    result: AuditResult,
    operation: OperationContract,
    response_model: type | None,
    fixture_path: Path,
) -> None:
    result.fixture_count += 1
    if not fixture_path.exists():
        result.add(
            _issue(
                operation,
                code="fixture_missing",
                severity="error",
                message=f"Fixture does not exist: {fixture_path}",
                always_blocking=True,
            )
        )
        return
    try:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result.add(
            _issue(
                operation,
                code="fixture_invalid_json",
                severity="error",
                message=str(exc),
                always_blocking=True,
            )
        )
        return
    for finding in find_sensitive_values(payload):
        result.add(
            _issue(
                operation,
                code="fixture_sensitive_value",
                severity="error",
                message=finding,
                always_blocking=True,
            )
        )
    if response_model is not None:
        try:
            response_model.model_validate(payload)
        except ValidationError as exc:
            result.add(
                _issue(
                    operation,
                    code="fixture_model_validation_failed",
                    severity="error",
                    message=str(exc),
                    actual=str(fixture_path),
                )
            )


def audit_catalog(catalog: ContractCatalog) -> AuditResult:
    result = AuditResult(operation_count=len(catalog.operations))
    result.verified_count = sum(
        operation.verification == "verified" for operation in catalog.operations.values()
    )

    try:
        from api_client_opti24.registry import build_default_registry

        runtime_operations = {spec.name for spec in build_default_registry().list_all()} - set(
            catalog.manifest.excluded_operations
        )
        normalized_operations = set(catalog.operations)
        for name in sorted(runtime_operations - normalized_operations):
            result.add(
                AuditIssue(
                    code="runtime_operation_not_normalized",
                    severity="error",
                    message="Runtime operation is absent from normalized specification contracts.",
                    operation=name,
                    blocking=True,
                )
            )
        for name in sorted(normalized_operations - runtime_operations):
            result.add(
                AuditIssue(
                    code="normalized_operation_not_in_runtime",
                    severity="error",
                    message="Normalized operation is absent from the runtime registry.",
                    operation=name,
                    blocking=True,
                )
            )
    except (ImportError, AttributeError, TypeError, ValueError) as exc:
        result.add(
            AuditIssue(
                code="runtime_registry_unavailable",
                severity="error",
                message=str(exc),
                blocking=True,
            )
        )

    for operation in catalog.iter_operations():
        try:
            method = resolve_service_method(operation.service, operation.name)
        except (ImportError, AttributeError, KeyError, TypeError, ValueError) as exc:
            result.add(
                _issue(
                    operation,
                    code="service_method_unavailable",
                    severity="error",
                    message=str(exc),
                    always_blocking=True,
                )
            )
            continue
        for variant in operation.variants:
            for field in variant.request_parameters:
                _audit_request_signature(result, operation, method, field)

        return_annotation = resolve_return_annotation(method)
        response_model = resolve_response_model(method)
        if operation.response_kind == "binary":
            if return_annotation is not bytes:
                result.add(
                    _issue(
                        operation,
                        code="binary_response_type_mismatch",
                        severity="error",
                        message="Binary operation must return bytes.",
                        expected="bytes",
                        actual=format_annotation(return_annotation),
                    )
                )
        elif operation.response_kind == "mapping":
            if get_origin(return_annotation) is not dict and return_annotation is not dict:
                result.add(
                    _issue(
                        operation,
                        code="mapping_response_type_mismatch",
                        severity="error",
                        message="Mapping operation must return a dict annotation.",
                        expected="dict",
                        actual=format_annotation(return_annotation),
                    )
                )
            result.add(
                _issue(
                    operation,
                    code="untyped_response_return",
                    severity="warning",
                    message="SDK returns a generic mapping; response fields are audited from the fixture only.",
                    actual=format_annotation(return_annotation),
                )
            )
            for variant in operation.variants:
                if variant.fixture is not None:
                    _audit_fixture(result, operation, None, variant.fixture)
        else:
            if response_model is None:
                result.add(
                    _issue(
                        operation,
                        code="response_model_missing",
                        severity="error",
                        message="Public SDK method does not expose a Pydantic response model annotation.",
                    )
                )
            else:
                for field in catalog.manifest.common_response_fields:
                    _compare_field(result, operation, response_model, field)
                for variant in operation.variants:
                    for field in variant.response_fields:
                        _compare_field(result, operation, response_model, field)
                    if variant.fixture is not None:
                        _audit_fixture(result, operation, response_model, variant.fixture)

        if operation.request_model:
            try:
                request_model = resolve_object(operation.request_model)
                usage = request_model_usage(method, request_model)
            except (ImportError, AttributeError, TypeError, ValueError) as exc:
                result.add(
                    _issue(
                        operation,
                        code="request_model_unavailable",
                        severity="error",
                        message=str(exc),
                        always_blocking=True,
                    )
                )
            else:
                if usage != "used-directly":
                    result.add(
                        _issue(
                            operation,
                            code="request_model_not_used",
                            severity="warning",
                            message="Request-модель объявлена в контракте, но не используется напрямую методом.",
                            actual=usage,
                        )
                    )

    for model_path, field_name, annotation in untyped_model_fields():
        result.add(
            AuditIssue(
                code="sdk_untyped_model_field",
                severity="info",
                message="Pydantic-модель содержит Any или dict с Any.",
                path=f"{model_path}.{field_name}",
                actual=annotation,
                blocking=False,
            )
        )
    return result
