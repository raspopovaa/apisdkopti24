from __future__ import annotations

from dataclasses import dataclass, fields

from .logger import LoggerLike
from .service_base import (
    RequestExecutor,
    SessionContext,
    SessionGate,
)
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


@dataclass(frozen=True, slots=True)
class ServiceContainer:
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

    @classmethod
    def service_names(cls) -> frozenset[str]:
        return frozenset(field.name for field in fields(cls))

    @classmethod
    def create(
        cls,
        *,
        request_executor: RequestExecutor,
        session_context: SessionContext,
        session_gate: SessionGate,
        logger: LoggerLike,
        auth: AuthService,
    ) -> ServiceContainer:
        common = (request_executor, session_context, session_gate, logger)
        return cls(
            auth=auth,
            card_groups=CardGroupsService(*common),
            cards=CardsService(*common),
            contracts=ContractsService(*common),
            dictionaries=DictionariesService(*common),
            ewallet=EwalletService(*common),
            final_prices=FinalPricesService(*common),
            invites=InvitesService(*common),
            limits=LimitsService(*common),
            region_limits=RegionLimitsService(*common),
            reports=ReportsService(*common),
            restrictions=RestrictionsService(*common),
            templates=TemplatesService(*common),
            transactions=TransactionsService(*common),
            users=UsersService(*common),
            virtual_cards=VirtualCardsService(*common),
        )
