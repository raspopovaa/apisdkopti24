from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version

from .audit_context import correlation_scope as correlation_scope
from .client import APIClient as APIClient
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
from .errors import DuplicateLoginError as DuplicateLoginError
from .errors import FileWriteError as FileWriteError
from .errors import InviteNotReadyError as InviteNotReadyError
from .errors import NotAuthenticatedError as NotAuthenticatedError
from .errors import NotFoundError as NotFoundError
from .errors import ObjectNotAccessibleError as ObjectNotAccessibleError
from .errors import Opti24Error as Opti24Error
from .errors import PaginationLimitError as PaginationLimitError
from .errors import PlanNotPaidError as PlanNotPaidError
from .errors import ProcessingRefusalError as ProcessingRefusalError
from .errors import RateLimitError as RateLimitError
from .errors import ReportFailedError as ReportFailedError
from .errors import ReportWaitTimeoutError as ReportWaitTimeoutError
from .errors import RequestPreparationError as RequestPreparationError
from .errors import RequestValidationError as RequestValidationError
from .errors import ResponseShapeError as ResponseShapeError
from .errors import ResponseTooLargeError as ResponseTooLargeError
from .errors import ResponseValidationError as ResponseValidationError
from .errors import SDKConfigurationError as SDKConfigurationError
from .errors import ServerError as ServerError
from .errors import ValidationError as ValidationError
from .errors import WafBlockedError as WafBlockedError
from .execution_budget import OperationBudget as OperationBudget
from .execution_budget import OperationTimeoutError as OperationTimeoutError
from .execution_budget import RetryBudgetExceededError as RetryBudgetExceededError
from .executor import DefaultRequestExecutor as DefaultRequestExecutor
from .executor import OperationExecutor as OperationExecutor
from .modeling import APIEnvelope as APIEnvelope
from .modeling import ResponseStatus as ResponseStatus
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
    "Opti24Error",
    "APIError",
    "AccessDeniedError",
    "DuplicateConflictError",
    "DuplicateLoginError",
    "InviteNotReadyError",
    "ObjectNotAccessibleError",
    "PlanNotPaidError",
    "ProcessingRefusalError",
    "ReportFailedError",
    "NotAuthenticatedError",
    "NotFoundError",
    "PaginationLimitError",
    "RateLimitError",
    "ReportWaitTimeoutError",
    "ServerError",
    "ValidationError",
    "WafBlockedError",
    "APIKeyProvider",
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
    "correlation_scope",
    "__version__",
]
