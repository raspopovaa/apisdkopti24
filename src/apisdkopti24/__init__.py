from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from typing import TYPE_CHECKING, Any

from .client import APIClient as APIClient

# Анализаторы типов не исполняют модульный __getattr__ и без этих импортов видят
# ленивые экспорты как Any. Во время выполнения модули по-прежнему грузятся лениво.
if TYPE_CHECKING:
    from .config import APISettings as APISettings
    from .config import ConnectionSettings as ConnectionSettings
    from .config import TimeoutPolicy as TimeoutPolicy
    from .credentials import EnvironmentCredentialsProvider as EnvironmentCredentialsProvider
    from .credentials import RefreshingAPIKeyProvider as RefreshingAPIKeyProvider
    from .credentials import StaticAPIKeyProvider as StaticAPIKeyProvider
    from .credentials import StaticCredentialsProvider as StaticCredentialsProvider
    from .credentials import StaticLoginPasswordProvider as StaticLoginPasswordProvider
    from .errors import AccessDeniedError as AccessDeniedError
    from .errors import APIConnectionError as APIConnectionError
    from .errors import APIError as APIError
    from .errors import APINetworkError as APINetworkError
    from .errors import APIResponseTimeoutError as APIResponseTimeoutError
    from .errors import ContractSelectionError as ContractSelectionError
    from .errors import DuplicateConflictError as DuplicateConflictError
    from .errors import FileWriteError as FileWriteError
    from .errors import NotAuthenticatedError as NotAuthenticatedError
    from .errors import NotFoundError as NotFoundError
    from .errors import RateLimitError as RateLimitError
    from .errors import RequestPreparationError as RequestPreparationError
    from .errors import RequestValidationError as RequestValidationError
    from .errors import ResponseShapeError as ResponseShapeError
    from .errors import ResponseTooLargeError as ResponseTooLargeError
    from .errors import ResponseValidationError as ResponseValidationError
    from .errors import SDKConfigurationError as SDKConfigurationError
    from .errors import ServerError as ServerError
    from .errors import ValidationError as ValidationError
    from .execution_budget import OperationBudget as OperationBudget
    from .execution_budget import OperationTimeoutError as OperationTimeoutError
    from .execution_budget import RetryBudgetExceededError as RetryBudgetExceededError
    from .executor import DefaultRequestExecutor as DefaultRequestExecutor
    from .executor import OperationExecutor as OperationExecutor
    from .modeling import APIEnvelope as APIEnvelope
    from .modeling import ResponseStatus as ResponseStatus
    from .operations import Operation as Operation
    from .policies import ConcurrencyPolicy as ConcurrencyPolicy
    from .policies import RateLimitPolicy as RateLimitPolicy
    from .policies import RetryClass as RetryClass
    from .policies import RetryPolicy as RetryPolicy
    from .registry import MethodRegistry as MethodRegistry
    from .registry import MethodSpec as MethodSpec
    from .requests import RequestContract as RequestContract
    from .response import ResponseDecoder as ResponseDecoder
    from .runtime import Clock as Clock
    from .runtime import SystemClock as SystemClock
    from .service_base import APIKeyProvider as APIKeyProvider
    from .service_base import CredentialsProvider as CredentialsProvider
    from .service_base import RequestExecutor as RequestExecutor
    from .service_base import SessionContext as SessionContext
    from .service_base import SessionGate as SessionGate
    from .service_base import SessionMutator as SessionMutator
    from .service_base import SessionRecovery as SessionRecovery
    from .service_groups import ServiceContainer as ServiceContainer
    from .services.auth import AuthService as AuthService
    from .services.card_group import CardGroupsService as CardGroupsService
    from .services.cards import CardsService as CardsService
    from .services.contract import ContractsService as ContractsService
    from .services.dictionaries import DictionariesService as DictionariesService
    from .services.ewallet import EwalletService as EwalletService
    from .services.final_prices import FinalPricesService as FinalPricesService
    from .services.invites import InvitesService as InvitesService
    from .services.limits import LimitsService as LimitsService
    from .services.region_limits import RegionLimitsService as RegionLimitsService
    from .services.reports import ReportsService as ReportsService
    from .services.restrictions import RestrictionsService as RestrictionsService
    from .services.templates import TemplatesService as TemplatesService
    from .services.transactions import TransactionsService as TransactionsService
    from .services.users import UsersService as UsersService
    from .services.virtual_cards import VirtualCardsService as VirtualCardsService
    from .session import SessionManager as SessionManager
    from .session import SessionState as SessionState
    from .transport import AsyncTransport as AsyncTransport

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
    "APINetworkError",
    "APIResponseTimeoutError",
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
    "RefreshingAPIKeyProvider",
    "RetryPolicy",
    "ReportsService",
    "ResponseDecoder",
    "ResponseShapeError",
    "ResponseValidationError",
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
    "APINetworkError": (".errors", "APINetworkError"),
    "APIResponseTimeoutError": (".errors", "APIResponseTimeoutError"),
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
    "ResponseValidationError": (".errors", "ResponseValidationError"),
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
    "RefreshingAPIKeyProvider": (".credentials", "RefreshingAPIKeyProvider"),
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
