from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

VerificationStatus = Literal["provisional", "verified", "accepted", "unsupported", "excluded"]
Severity = Literal["info", "warning", "error"]
ResponseKind = Literal["pydantic", "mapping", "binary"]


@dataclass(frozen=True, slots=True)
class FieldContract:
    path: str
    api_type: str
    required: bool | None
    description: str


@dataclass(frozen=True, slots=True)
class ContractDecision:
    path: str
    status: str
    reason: str
    spec_type: str | None = None
    model_type: str | None = None


@dataclass(frozen=True, slots=True)
class VariantContract:
    route_name: str
    source_section: str
    request_line: str
    request_parameters: tuple[FieldContract, ...]
    response_fields: tuple[FieldContract, ...]
    fixture: Path | None
    fixture_status: str
    fixture_corrections: tuple[dict[str, str], ...] = ()
    fixture_note: str | None = None


@dataclass(frozen=True, slots=True)
class OperationContract:
    name: str
    summary: str
    verification: VerificationStatus
    service: str
    request_model: str | None
    response_kind: ResponseKind
    variants: tuple[VariantContract, ...]
    decisions: tuple[ContractDecision, ...] = ()
    source_decisions: tuple[ContractDecision, ...] = ()


@dataclass(frozen=True, slots=True)
class ContractManifest:
    root: Path
    schema_version: int
    source: dict[str, Any]
    domain_files: tuple[str, ...]
    excluded_operations: frozenset[str]
    expected_operation_count: int
    common_response_fields: tuple[FieldContract, ...]


@dataclass(frozen=True, slots=True)
class ContractCatalog:
    manifest: ContractManifest
    operations: dict[str, OperationContract]

    def iter_operations(self) -> tuple[OperationContract, ...]:
        return tuple(self.operations[name] for name in sorted(self.operations))


@dataclass(frozen=True, slots=True)
class AuditIssue:
    code: str
    severity: Severity
    message: str
    operation: str | None = None
    path: str | None = None
    expected: str | None = None
    actual: str | None = None
    blocking: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "operation": self.operation,
            "path": self.path,
            "expected": self.expected,
            "actual": self.actual,
            "blocking": self.blocking,
        }


@dataclass(slots=True)
class AuditResult:
    issues: list[AuditIssue] = field(default_factory=list)
    operation_count: int = 0
    fixture_count: int = 0
    verified_count: int = 0

    @property
    def blocking_issues(self) -> tuple[AuditIssue, ...]:
        return tuple(issue for issue in self.issues if issue.blocking)

    @property
    def has_blocking_issues(self) -> bool:
        return bool(self.blocking_issues)

    def add(self, issue: AuditIssue) -> None:
        self.issues.append(issue)

    def summary(self) -> dict[str, int]:
        return {
            "operations": self.operation_count,
            "verified_operations": self.verified_count,
            "fixtures": self.fixture_count,
            "issues": len(self.issues),
            "blocking_issues": len(self.blocking_issues),
            "errors": sum(issue.severity == "error" for issue in self.issues),
            "warnings": sum(issue.severity == "warning" for issue in self.issues),
            "info": sum(issue.severity == "info" for issue in self.issues),
        }
