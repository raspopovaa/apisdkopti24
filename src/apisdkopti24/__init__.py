from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from typing import Any

from .client import APIClient as APIClient

try:
    __version__ = distribution_version("apisdkopti24")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "APIClient",
    "APIError",
    "AccessDeniedError",
    "DuplicateConflictError",
    "NotAuthenticatedError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "APIKeyProvider",
    "APISettings",
    "APIEnvelope",
    "AsyncTransport",
    "AuthService",
    "CardGroupsService",
    "CardsService",
    "Clock",
    "ConnectionSettings",
    "ConcurrencyPolicy",
    "ContractsService",
    "ContractSelectionError",
    "APIConnectionError",
    "FileWriteError",
    "CredentialsProvider",
    "DefaultRequestExecutor",
    "DictionariesService",
    "EnvironmentCredentialsProvider",
    "EwalletService",
    "FinalPricesService",
    "InvitesService",
    "LimitsService",
    "MethodRegistry",
    "MethodSpec",
    "OperationBudget",
    "OperationExecutor",
    "Operation",
    "OperationTimeoutError",
    "RateLimitPolicy",
    "RegionLimitsService",
    "RetryBudgetExceededError",
    "RetryClass",
    "RetryPolicy",
    "ReportsService",
    "ResponseDecoder",
    "ResponseShapeError",
    "ResponseStatus",
    "ResponseTooLargeError",
    "RequestExecutor",
    "RequestContract",
    "RequestPreparationError",
    "RequestValidationError",
    "RestrictionsService",
    "SessionManager",
    "SessionContext",
    "SessionGate",
    "SessionMutator",
    "SessionRecovery",
    "ServiceContainer",
    "SessionState",
    "StaticCredentialsProvider",
    "StaticAPIKeyProvider",
    "StaticLoginPasswordProvider",
    "SDKConfigurationError",
    "SystemClock",
    "TemplatesService",
    "TimeoutPolicy",
    "TransactionsService",
    "UsersService",
    "VirtualCardsService",
    "__version__",
]

_EXPORTS = {
    "APIKeyProvider": (".service_base", "APIKeyProvider"),
    "APISettings": (".config", "APISettings"),
    "APIEnvelope": (".modeling", "APIEnvelope"),
    "AsyncTransport": (".transport", "AsyncTransport"),
    "AuthService": (".service_groups", "AuthService"),
    "CardGroupsService": (".service_groups", "CardGroupsService"),
    "CardsService": (".service_groups", "CardsService"),
    "Clock": (".runtime", "Clock"),
    "ConnectionSettings": (".config", "ConnectionSettings"),
    "ConcurrencyPolicy": (".policies", "ConcurrencyPolicy"),
    "ContractSelectionError": (".errors", "ContractSelectionError"),
    "APIConnectionError": (".errors", "APIConnectionError"),
    "APIError": (".errors", "APIError"),
    "AccessDeniedError": (".errors", "AccessDeniedError"),
    "DuplicateConflictError": (".errors", "DuplicateConflictError"),
    "NotAuthenticatedError": (".errors", "NotAuthenticatedError"),
    "NotFoundError": (".errors", "NotFoundError"),
    "RateLimitError": (".errors", "RateLimitError"),
    "ServerError": (".errors", "ServerError"),
    "ValidationError": (".errors", "ValidationError"),
    "FileWriteError": (".errors", "FileWriteError"),
    "ContractsService": (".service_groups", "ContractsService"),
    "CredentialsProvider": (".service_base", "CredentialsProvider"),
    "DefaultRequestExecutor": (".executor", "DefaultRequestExecutor"),
    "DictionariesService": (".service_groups", "DictionariesService"),
    "EnvironmentCredentialsProvider": (
        ".credentials",
        "EnvironmentCredentialsProvider",
    ),
    "EwalletService": (".service_groups", "EwalletService"),
    "FinalPricesService": (".service_groups", "FinalPricesService"),
    "InvitesService": (".service_groups", "InvitesService"),
    "LimitsService": (".service_groups", "LimitsService"),
    "MethodRegistry": (".registry", "MethodRegistry"),
    "MethodSpec": (".registry", "MethodSpec"),
    "OperationBudget": (".execution_budget", "OperationBudget"),
    "OperationExecutor": (".executor", "OperationExecutor"),
    "Operation": (".operations", "Operation"),
    "OperationTimeoutError": (".execution_budget", "OperationTimeoutError"),
    "RateLimitPolicy": (".policies", "RateLimitPolicy"),
    "RegionLimitsService": (".service_groups", "RegionLimitsService"),
    "RetryBudgetExceededError": (
        ".execution_budget",
        "RetryBudgetExceededError",
    ),
    "RetryClass": (".policies", "RetryClass"),
    "RetryPolicy": (".policies", "RetryPolicy"),
    "ReportsService": (".service_groups", "ReportsService"),
    "ResponseDecoder": (".response", "ResponseDecoder"),
    "ResponseShapeError": (".errors", "ResponseShapeError"),
    "ResponseStatus": (".modeling", "ResponseStatus"),
    "ResponseTooLargeError": (".errors", "ResponseTooLargeError"),
    "RequestExecutor": (".service_base", "RequestExecutor"),
    "RequestContract": (".requests", "RequestContract"),
    "RequestPreparationError": (".errors", "RequestPreparationError"),
    "RequestValidationError": (".errors", "RequestValidationError"),
    "RestrictionsService": (".service_groups", "RestrictionsService"),
    "SessionManager": (".session", "SessionManager"),
    "SessionContext": (".service_base", "SessionContext"),
    "SessionGate": (".service_base", "SessionGate"),
    "SessionMutator": (".service_base", "SessionMutator"),
    "SessionRecovery": (".service_base", "SessionRecovery"),
    "ServiceContainer": (".service_groups", "ServiceContainer"),
    "SessionState": (".session", "SessionState"),
    "StaticCredentialsProvider": (".credentials", "StaticCredentialsProvider"),
    "StaticAPIKeyProvider": (".credentials", "StaticAPIKeyProvider"),
    "StaticLoginPasswordProvider": (
        ".credentials",
        "StaticLoginPasswordProvider",
    ),
    "SDKConfigurationError": (".errors", "SDKConfigurationError"),
    "SystemClock": (".runtime", "SystemClock"),
    "TemplatesService": (".service_groups", "TemplatesService"),
    "TimeoutPolicy": (".config", "TimeoutPolicy"),
    "TransactionsService": (".service_groups", "TransactionsService"),
    "UsersService": (".service_groups", "UsersService"),
    "VirtualCardsService": (".service_groups", "VirtualCardsService"),
}


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute_name = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"Модуль {__name__!r} не имеет атрибута {name!r}") from exc

    module = import_module(module_name, __name__)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
