from __future__ import annotations

import logging
from dataclasses import dataclass
from types import TracebackType
from typing import cast

from .authentication import AuthenticationCoordinator
from .composition import compose_client_runtime
from .config import APISettings, ConnectionSettings
from .credentials import (
    StaticAPIKeyProvider,
    StaticCredentialsProvider,
    StaticLoginPasswordProvider,
)
from .executor import DefaultRequestExecutor, Transport
from .logger import (
    LoggerLike,
    ManagedLogger,
    create_client_logger,
    ensure_sanitizing_filter,
)
from .registry import MethodRegistry, build_default_registry
from .runtime import Clock, SystemClock
from .service_base import APIKeyProvider, CredentialsProvider
from .service_groups import ServiceContainer, _ServiceFacade
from .session import SessionManager
from .transport import AsyncTransport


@dataclass(frozen=True, slots=True)
class _ResolvedClientInputs:
    settings: ConnectionSettings
    credentials_provider: CredentialsProvider
    api_key_provider: APIKeyProvider


class APIClient(_ServiceFacade):
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        login: str | None = None,
        password: str | None = None,
        *,
        settings: ConnectionSettings | APISettings | None = None,
        transport: Transport | None = None,
        session_manager: SessionManager | None = None,
        registry: MethodRegistry | None = None,
        logger: logging.Logger | None = None,
        clock: Clock | None = None,
        credentials_provider: CredentialsProvider | None = None,
        api_key_provider: APIKeyProvider | None = None,
    ) -> None:
        resolved = self._resolve_inputs(
            base_url=base_url,
            api_key=api_key,
            login=login,
            password=password,
            settings=settings,
            credentials_provider=credentials_provider,
            api_key_provider=api_key_provider,
        )
        self.settings: ConnectionSettings = resolved.settings
        self.__managed_logger: ManagedLogger | None = None
        self._owns_transport = transport is None
        self._closed = False

        if logger is not None:
            self.logger: LoggerLike = logger
            ensure_sanitizing_filter(logger)
        else:
            self.__managed_logger = create_client_logger(
                log_level=self.settings.log_level,
                logger_file=self.settings.logger_file,
                request_log_file=self.settings.request_log_file,
            )
            self.logger = self.__managed_logger.logger

        try:
            self.clock: Clock = clock or SystemClock()
            self.session_manager: SessionManager = session_manager or SessionManager()
            self.registry: MethodRegistry = registry or build_default_registry()
            self.transport: Transport = transport or AsyncTransport(
                self.settings.base_url,
                default_timeout=self.settings.timeouts.default,
                retry_policy=self.settings.retry_policy,
                rate_limit_policy=self.settings.rate_limit_policy,
                concurrency_policy=self.settings.concurrency_policy,
                allow_insecure_http=self.settings.allow_insecure_http,
                logger=self.logger,
                clock=self.clock,
            )
            runtime = compose_client_runtime(
                api_key_provider=resolved.api_key_provider,
                credentials_provider=resolved.credentials_provider,
                transport=self.transport,
                session_manager=self.session_manager,
                registry=self.registry,
                timeouts=self.settings.timeouts,
                max_attempts=self.settings.retry_policy.max_total_attempts,
                logger=self.logger,
                clock=self.clock,
            )
        except Exception:
            if self.__managed_logger is not None:
                self.__managed_logger.close()
            raise

        self.authentication: AuthenticationCoordinator = runtime.authentication
        self.request_executor: DefaultRequestExecutor = runtime.request_executor
        self.services: ServiceContainer = runtime.services

    @classmethod
    def _resolve_inputs(
        cls,
        *,
        base_url: str | None,
        api_key: str | None,
        login: str | None,
        password: str | None,
        settings: ConnectionSettings | APISettings | None,
        credentials_provider: CredentialsProvider | None,
        api_key_provider: APIKeyProvider | None,
    ) -> _ResolvedClientInputs:
        legacy_api_key: str | None = None
        legacy_login: str | None = None
        legacy_password: str | None = None
        if settings is None:
            if base_url is None:
                raise ValueError("Missing APIClient setting: base_url")
            connection_settings = ConnectionSettings(base_url=base_url)
            legacy_api_key = api_key
            legacy_login = login
            legacy_password = password
        elif any(value is not None for value in (base_url, api_key, login, password)):
            raise ValueError("Pass either settings or individual credentials, not both")
        elif isinstance(settings, APISettings):
            connection_settings = settings.connection_settings()
            legacy_api_key = settings.api_key
            legacy_login = settings.login
            legacy_password = settings.password
        else:
            connection_settings = settings

        resolved_credentials = credentials_provider
        if resolved_credentials is None:
            if not legacy_login or not legacy_password:
                raise ValueError(
                    "Missing authentication settings: login, password; "
                    "pass credentials_provider or legacy credentials"
                )
            if legacy_api_key:
                resolved_credentials = StaticCredentialsProvider(
                    api_key=legacy_api_key,
                    login=legacy_login,
                    password=legacy_password,
                )
            else:
                resolved_credentials = StaticLoginPasswordProvider(
                    login=legacy_login,
                    password=legacy_password,
                )
        resolved_api_key_provider = cls._resolve_api_key_provider(
            api_key_provider=api_key_provider,
            credentials_provider=resolved_credentials,
            legacy_api_key=legacy_api_key,
        )
        return _ResolvedClientInputs(
            settings=connection_settings,
            credentials_provider=resolved_credentials,
            api_key_provider=resolved_api_key_provider,
        )

    @staticmethod
    def _resolve_api_key_provider(
        *,
        api_key_provider: APIKeyProvider | None,
        credentials_provider: CredentialsProvider,
        legacy_api_key: str | None,
    ) -> APIKeyProvider:
        if api_key_provider is not None:
            return api_key_provider
        provider_method = getattr(credentials_provider, "get_api_key", None)
        if callable(provider_method):
            return cast(APIKeyProvider, credentials_provider)
        if legacy_api_key:
            return StaticAPIKeyProvider(legacy_api_key)
        raise ValueError(
            "Missing API key; pass api_key_provider or a combined credentials provider"
        )

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if self._owns_transport:
                await self.transport.aclose()
        finally:
            if self.__managed_logger is not None:
                self.__managed_logger.close()

    async def __aenter__(self) -> APIClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    @property
    def session_id(self) -> str | None:
        return self.session_manager.session_id

    @property
    def contract_id(self) -> str | None:
        return self.session_manager.contract_id

    def select_contract(self, *, contract_id: str) -> None:
        """Select the local contract context for lazy authentication and requests."""
        self.session_manager.select_contract(contract_id)

    def restore_session(self, *, session_id: str, contract_id: str) -> None:
        """Restore a trusted local session pair without a server round trip."""
        self.session_manager.restore(session_id=session_id, contract_id=contract_id)

    def clear_session(self) -> None:
        """Clear local session and contract state."""
        self.session_manager.clear()
