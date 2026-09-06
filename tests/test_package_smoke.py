from __future__ import annotations

import inspect
import logging
from datetime import datetime

import pytest

import apisdkopti24 as sdk
from apisdkopti24 import APIClient, __version__
from apisdkopti24.config import APISettings, ConnectionSettings
from apisdkopti24.credentials import (
    StaticCredentialsProvider,
    StaticLoginPasswordProvider,
)
from apisdkopti24.registry import build_default_registry

SERVICE_TYPES = {
    "auth": "AuthService",
    "card_groups": "CardGroupsService",
    "cards": "CardsService",
    "contracts": "ContractsService",
    "dictionaries": "DictionariesService",
    "ewallet": "EwalletService",
    "final_prices": "FinalPricesService",
    "invites": "InvitesService",
    "limits": "LimitsService",
    "region_limits": "RegionLimitsService",
    "reports": "ReportsService",
    "restrictions": "RestrictionsService",
    "templates": "TemplatesService",
    "transactions": "TransactionsService",
    "users": "UsersService",
    "virtual_cards": "VirtualCardsService",
}

DOMAIN_SERVICES = {
    "auth": "auth",
    "card_group": "card_groups",
    "cards": "cards",
    "contract": "contracts",
    "dictionaries": "dictionaries",
    "ewallet": "ewallet",
    "final_prices": "final_prices",
    "invites": "invites",
    "limits": "limits",
    "region_limits": "region_limits",
    "reports": "reports",
    "restrictions": "restrictions",
    "templates": "templates",
    "transactions": "transactions",
    "users": "users",
    "virtual_cards": "virtual_cards",
}

DOCUMENTED_SCENARIOS = {
    "auth": "auth_user",
    "card_group": "set_card_group",
    "cards": "block_card",
    "contract": "order_invoice",
    "dictionaries": "get_azs_list_v2",
    "ewallet": "move_to_card",
    "final_prices": "get_final_prices",
    "invites": "create_invite",
    "limits": "set_limit",
    "region_limits": "set_region_limit",
    "reports": "order_report",
    "restrictions": "set_restriction",
    "templates": "create_template",
    "transactions": "get_transactions_v2",
    "users": "create_user",
    "virtual_cards": "release_virtual_card",
}


def test_package_root_exports_client() -> None:
    assert APIClient.__name__ == "APIClient"


def test_package_root_exports_version() -> None:
    assert __version__ == "3.2.0"


def test_settings_factory_is_available() -> None:
    assert callable(APISettings.from_env)


@pytest.mark.asyncio
async def test_client_exposes_all_composition_services_without_credentials(tmp_path) -> None:
    settings = APISettings(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        logger_file=str(tmp_path / "sdk.log"),
    )

    client = APIClient(settings=settings)

    for attribute_name, class_name in SERVICE_TYPES.items():
        service = getattr(client, attribute_name)
        assert isinstance(service, getattr(sdk, class_name))
        assert client not in vars(service).values()

    assert isinstance(client.services, sdk.ServiceContainer)
    assert not hasattr(client, "api_key")
    assert not hasattr(client, "login")
    assert not hasattr(client, "password")
    assert not hasattr(client.cards, "settings")
    assert not hasattr(client.cards, "transport")
    container_factory = inspect.signature(sdk.ServiceContainer.create)
    assert "credentials_provider" not in container_factory.parameters
    await client.aclose()


@pytest.mark.asyncio
async def test_credentials_provider_is_injected_only_into_auth_service(tmp_path) -> None:
    class TrackingCredentialsProvider:
        def __init__(self) -> None:
            self.calls = 0

        def get_credentials(self) -> tuple[str, str]:
            self.calls += 1
            return "injected-login", "injected-password"

    provider = TrackingCredentialsProvider()
    settings = APISettings(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="unused-login",
        password="unused-password",
        logger_file=str(tmp_path / "sdk.log"),
    )
    client = APIClient(settings=settings, credentials_provider=provider)

    for name in SERVICE_TYPES:
        if name != "auth":
            assert provider not in vars(getattr(client, name)).values()
    authenticator = next(
        value
        for value in vars(client.auth).values()
        if type(value).__name__ == "DefaultAuthenticator"
    )
    assert provider in vars(authenticator).values()
    assert provider.calls == 0

    await client.aclose()


@pytest.mark.asyncio
async def test_credentials_provider_does_not_require_placeholder_credentials() -> None:
    class ExternalCredentialsProvider:
        def get_credentials(self) -> tuple[str, str]:
            return "external-login", "external-password"

    client = APIClient(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        credentials_provider=ExternalCredentialsProvider(),
    )

    assert type(client.settings).__name__ == ConnectionSettings.__name__
    assert not hasattr(client.settings, "api_key")
    assert not hasattr(client.settings, "login")
    assert not hasattr(client.settings, "password")
    await client.aclose()


@pytest.mark.asyncio
async def test_client_accepts_safe_settings_and_combined_credentials_provider(tmp_path) -> None:
    settings = ConnectionSettings(
        base_url="https://example.invalid/vip/",
        logger_file=str(tmp_path / "sdk.log"),
        request_log_file=str(tmp_path / "requests.jsonl"),
    )
    provider = StaticCredentialsProvider(
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
    )

    client = APIClient(settings=settings, credentials_provider=provider)

    assert client.settings is settings
    assert not hasattr(client.settings, "api_key")
    await client.aclose()


@pytest.mark.asyncio
async def test_client_keeps_dynamic_api_key_provider_live(tmp_path) -> None:
    class DynamicAPIKeyProvider:
        def __init__(self) -> None:
            self.value = "initial-key"

        def get_api_key(self) -> str:
            return self.value

    provider = DynamicAPIKeyProvider()
    client = APIClient(
        settings=ConnectionSettings(
            base_url="https://example.invalid/vip/",
            logger_file=str(tmp_path / "sdk.log"),
        ),
        api_key_provider=provider,
        credentials_provider=StaticLoginPasswordProvider(
            login="demo-login",
            password="demo-password",
        ),
    )

    operation = client.registry.get("auth_user")
    assert client.request_executor.preview_headers(operation)["api_key"] == "initial-key"
    provider.value = "rotated-key"
    assert client.request_executor.preview_headers(operation)["api_key"] == "rotated-key"
    assert not hasattr(client.authentication, "bind")
    await client.aclose()


@pytest.mark.asyncio
async def test_all_registered_methods_exist_only_on_domain_services(tmp_path) -> None:
    settings = APISettings(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        logger_file=str(tmp_path / "sdk.log"),
    )
    client = APIClient(settings=settings)

    for spec in build_default_registry().list_all():
        service = getattr(client, DOMAIN_SERVICES[spec.domain])
        assert callable(getattr(service, spec.name))
        assert not hasattr(client, spec.name)

    await client.aclose()


def test_registered_service_methods_have_docstrings_and_domain_scenarios() -> None:
    registry = build_default_registry()

    for spec in registry.list_all():
        service_type = getattr(sdk, SERVICE_TYPES[DOMAIN_SERVICES[spec.domain]])
        assert inspect.getdoc(getattr(service_type, spec.name)), spec.name

    for domain, operation_name in DOCUMENTED_SCENARIOS.items():
        service_type = getattr(sdk, SERVICE_TYPES[DOMAIN_SERVICES[domain]])
        docstring = inspect.getdoc(getattr(service_type, operation_name)) or ""
        assert "Типовой сценарий" in docstring, operation_name
        assert "Пример" in docstring, operation_name


def test_non_qr_mpc_public_service_parameters_are_keyword_only() -> None:
    legacy_positional_methods = {"delete_mpc", "reset_mpc"}
    for service_type_name in SERVICE_TYPES.values():
        service_type = getattr(sdk, service_type_name)
        for method_name, method in inspect.getmembers(
            service_type,
            predicate=inspect.iscoroutinefunction,
        ):
            if method_name.startswith("_") or method_name in legacy_positional_methods:
                continue
            parameters = list(inspect.signature(method).parameters.values())[1:]
            assert all(
                parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters
            ), f"{service_type_name}.{method_name}"


@pytest.mark.asyncio
async def test_client_accepts_logger_and_clock_without_configuring_log_file(tmp_path) -> None:
    class FrozenClock:
        def now(self) -> datetime:
            return datetime(2026, 7, 15, 12, 30, 0)

        def monotonic(self) -> float:
            return 0.0

        async def sleep(self, _seconds: float) -> None:
            return None

    log_path = tmp_path / "must-not-be-created.log"
    settings = APISettings(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        logger_file=str(log_path),
    )
    injected_logger = logging.getLogger(f"test-client-{id(settings)}")
    injected_logger.addHandler(logging.NullHandler())

    client = APIClient(
        settings=settings,
        logger=injected_logger,
        clock=FrozenClock(),
    )

    assert (
        client.request_executor.preview_headers(client.registry.get("auth_user"))["date_time"]
        == "2026-07-15 12:30:00"
    )
    assert all(getattr(client, name).logger is injected_logger for name in SERVICE_TYPES)
    assert not log_path.exists()
    await client.aclose()


@pytest.mark.asyncio
async def test_client_can_be_created_and_closed() -> None:
    client = APIClient(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
    )

    await client.aclose()


@pytest.mark.asyncio
async def test_client_accepts_settings_object(tmp_path) -> None:
    settings = APISettings(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
        logger_file=str(tmp_path / "sdk.log"),
    )

    client = APIClient(settings=settings)

    assert type(client.settings).__name__ == ConnectionSettings.__name__
    assert client.settings is not settings
    assert client.settings.base_url == settings.base_url
    assert not hasattr(client.settings, "api_key")
    await client.aclose()


def test_client_rejects_mixed_settings_and_credentials() -> None:
    settings = APISettings(
        base_url="https://example.invalid/vip/",
        api_key="demo-key",
        login="demo-login",
        password="demo-password",
    )

    with pytest.raises(ValueError, match="either settings or individual credentials"):
        APIClient(settings=settings, api_key="duplicate")
