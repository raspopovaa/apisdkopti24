from __future__ import annotations

from dataclasses import dataclass

from .authentication import AuthenticationCoordinator, DefaultAuthenticator
from .config import TimeoutPolicy
from .executor import DefaultRequestExecutor, OperationExecutor, Transport
from .logger import LoggerLike
from .registry import MethodRegistry
from .runtime import Clock
from .service_base import APIKeyProvider, CredentialsProvider
from .service_groups import ServiceContainer
from .services.auth import AuthService
from .session import SessionManager


@dataclass(frozen=True, slots=True)
class ClientRuntime:
    authentication: AuthenticationCoordinator
    request_executor: DefaultRequestExecutor
    services: ServiceContainer


def compose_client_runtime(
    *,
    api_key_provider: APIKeyProvider,
    credentials_provider: CredentialsProvider,
    transport: Transport,
    session_manager: SessionManager,
    registry: MethodRegistry,
    timeouts: TimeoutPolicy,
    max_attempts: int,
    logger: LoggerLike,
    clock: Clock,
) -> ClientRuntime:
    operation_executor = OperationExecutor(
        api_key_provider=api_key_provider,
        transport=transport,
        session_context=session_manager,
        registry=registry,
        timeouts=timeouts,
        max_attempts=max_attempts,
        logger=logger,
        clock=clock,
    )
    authenticator = DefaultAuthenticator(
        operation_executor,
        session_manager,
        credentials_provider,
        logger,
    )
    authentication = AuthenticationCoordinator(session_manager, authenticator)
    request_executor = DefaultRequestExecutor(
        operation_executor=operation_executor,
        session_gate=authentication,
        session_recovery=authentication,
        session_context=session_manager,
        logger=logger,
    )
    auth_service = AuthService(
        request_executor,
        session_manager,
        authentication,
        session_manager,
        authenticator,
        clock,
        logger,
    )
    services = ServiceContainer.create(
        request_executor=request_executor,
        session_context=session_manager,
        session_gate=authentication,
        logger=logger,
        auth=auth_service,
    )
    return ClientRuntime(authentication, request_executor, services)


__all__ = ["ClientRuntime", "compose_client_runtime"]
