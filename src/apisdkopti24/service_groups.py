from __future__ import annotations

from typing import get_type_hints

from .logger import LoggerLike
from .protocols import RequestExecutor, SessionContext, SessionGate
from .runtime import Clock
from .services.auth import AuthService
from .services.card_group import CardGroupsService
from .services.cards import CardsService
from .services.contract import ContractsService
from .services.dictionaries import DictionariesService
from .services.ewallet import EwalletService
from .services.final_prices import FinalPricesService
from .services.invites import InvitesService
from .services.limits import LimitsService
from .services.region_limits import RegionLimitsService
from .services.reports import ReportsService
from .services.restrictions import RestrictionsService
from .services.templates import TemplatesService
from .services.transactions import TransactionsService
from .services.users import UsersService
from .services.virtual_cards import VirtualCardsService


class ServiceAttributes:
    """Сервисы клиента: единственный список для контейнера и фасада ``APIClient``."""

    auth: AuthService
    card_groups: CardGroupsService
    cards: CardsService
    contracts: ContractsService
    dictionaries: DictionariesService
    ewallet: EwalletService
    final_prices: FinalPricesService
    invites: InvitesService
    limits: LimitsService
    region_limits: RegionLimitsService
    reports: ReportsService
    restrictions: RestrictionsService
    templates: TemplatesService
    transactions: TransactionsService
    users: UsersService
    virtual_cards: VirtualCardsService


class ServiceContainer(ServiceAttributes):
    def __init__(self, **services: object) -> None:
        if set(services) != self.service_names():
            raise TypeError("ServiceContainer принимает ровно по одному значению на каждый сервис")
        for name, service in services.items():
            setattr(self, name, service)

    @classmethod
    def service_names(cls) -> frozenset[str]:
        return frozenset(get_type_hints(ServiceAttributes))

    @classmethod
    def create(
        cls,
        *,
        request_executor: RequestExecutor,
        session_context: SessionContext,
        session_gate: SessionGate,
        logger: LoggerLike,
        auth: AuthService,
        clock: Clock | None = None,
    ) -> ServiceContainer:
        common = (request_executor, session_context, session_gate, logger)
        service_types = get_type_hints(ServiceAttributes)
        instances = {
            name: auth if name == "auth" else service_type(*common)
            for name, service_type in service_types.items()
        }
        # Ожиданию отчёта нужны внедрённые часы клиента, остальным сервисам — нет.
        # Без часов ReportsService берёт системные, как до появления параметра.
        instances["reports"] = ReportsService(*common, clock=clock)
        return cls(**instances)
