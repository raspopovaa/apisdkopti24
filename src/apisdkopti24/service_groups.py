from __future__ import annotations

from dataclasses import dataclass

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


class _ServiceFacade:
    services: ServiceContainer

    @property
    def auth(self) -> AuthService:
        return self.services.auth

    @property
    def card_groups(self) -> CardGroupsService:
        return self.services.card_groups

    @property
    def cards(self) -> CardsService:
        return self.services.cards

    @property
    def contracts(self) -> ContractsService:
        return self.services.contracts

    @property
    def dictionaries(self) -> DictionariesService:
        return self.services.dictionaries

    @property
    def ewallet(self) -> EwalletService:
        return self.services.ewallet

    @property
    def final_prices(self) -> FinalPricesService:
        return self.services.final_prices

    @property
    def invites(self) -> InvitesService:
        return self.services.invites

    @property
    def limits(self) -> LimitsService:
        return self.services.limits

    @property
    def region_limits(self) -> RegionLimitsService:
        return self.services.region_limits

    @property
    def reports(self) -> ReportsService:
        return self.services.reports

    @property
    def restrictions(self) -> RestrictionsService:
        return self.services.restrictions

    @property
    def templates(self) -> TemplatesService:
        return self.services.templates

    @property
    def transactions(self) -> TransactionsService:
        return self.services.transactions

    @property
    def users(self) -> UsersService:
        return self.services.users

    @property
    def virtual_cards(self) -> VirtualCardsService:
        return self.services.virtual_cards
