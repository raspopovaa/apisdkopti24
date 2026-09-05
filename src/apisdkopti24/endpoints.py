from __future__ import annotations

from dataclasses import dataclass
from string import Formatter
from urllib.parse import quote

from .policies import IDEMPOTENT_HTTP_METHODS, SAFE_HTTP_METHODS, RetryClass
from .service_base import PathParams


@dataclass(frozen=True, slots=True)
class RouteVariant:
    http_method: str
    endpoint: str
    api_version: str
    demo_available: bool
    name: str = "default"
    external_code: str | None = None
    billable: bool | None = None

    def __post_init__(self) -> None:
        if (self.external_code is None) != (self.billable is None):
            raise ValueError("external_code and billable must be configured together")
        if self.external_code is not None and not self.external_code:
            raise ValueError("external_code cannot be empty")

    def supports(self, version: str) -> bool:
        return self.api_version == version

    def render(self, path_params: PathParams | None = None) -> str:
        values = dict(path_params or {})
        fields: set[str] = set()
        for _, field_name, format_spec, conversion in Formatter().parse(self.endpoint):
            if field_name is None:
                continue
            if format_spec or conversion is not None:
                raise ValueError("Route templates cannot use conversions or format specifiers")
            fields.add(field_name)
        if set(values) != fields:
            missing = sorted(fields - set(values))
            unexpected = sorted(set(values) - fields)
            details = []
            if missing:
                details.append("missing: " + ", ".join(missing))
            if unexpected:
                details.append("unexpected: " + ", ".join(unexpected))
            raise ValueError(
                f"Invalid path parameters for route '{self.name}': " + "; ".join(details)
            )
        encoded: dict[str, str] = {}
        for name, value in values.items():
            raw_value = str(value)
            if raw_value in {".", ".."} or any(
                separator in raw_value for separator in ("/", "\\", "?", "#")
            ):
                raise ValueError(f"Unsafe path parameter: {name}")
            encoded[name] = quote(raw_value, safe="")
        return self.endpoint.format_map(encoded)


@dataclass(frozen=True, slots=True)
class EndpointSpec:
    name: str
    domain: str
    http_method: str
    endpoint: str
    supported_versions: tuple[str, ...]
    default_version: str
    demo_available: bool
    idempotent: bool
    requires_session: bool = True
    timeout_class: str = "default"
    retry_class: str = RetryClass.SAFE.value
    route_variants: tuple[RouteVariant, ...] = ()
    external_code: str | None = None
    billable: bool | None = None

    def __post_init__(self) -> None:
        if (self.external_code is None) != (self.billable is None):
            raise ValueError("external_code and billable must be configured together")
        if self.external_code is not None and not self.external_code:
            raise ValueError("external_code cannot be empty")

    def supports(self, version: str) -> bool:
        return version in self.supported_versions

    def iter_routes(self) -> tuple[RouteVariant, ...]:
        primary_route = RouteVariant(
            http_method=self.http_method,
            endpoint=self.endpoint,
            api_version=self.default_version,
            demo_available=self.demo_available,
            name="default",
            external_code=self.external_code,
            billable=self.billable,
        )
        return (primary_route, *self.route_variants)

    def resolve_route(
        self,
        *,
        api_version: str | None = None,
        route_name: str = "default",
    ) -> RouteVariant:
        version = api_version or self.default_version
        matches = [
            route
            for route in self.iter_routes()
            if route.name == route_name and route.supports(version)
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Operation '{self.name}' has no unique route "
                f"name={route_name!r} version={version!r}"
            )
        return matches[0]


def route(
    http_method: str,
    path: str,
    version: str,
    *,
    demo: bool,
    name: str,
    external_code: str | None = None,
    billable: bool | None = None,
) -> RouteVariant:
    return RouteVariant(
        http_method=http_method.upper(),
        endpoint=path,
        api_version=version,
        demo_available=demo,
        name=name,
        external_code=external_code,
        billable=billable,
    )


def endpoint(
    name: str,
    domain: str,
    http_method: str,
    path: str,
    version: str,
    *,
    demo: bool = True,
    timeout: str = "default",
    retry: str | None = None,
    requires_session: bool = True,
    variants: tuple[RouteVariant, ...] = (),
    external_code: str | None = None,
    billable: bool | None = None,
) -> EndpointSpec:
    normalized_method = http_method.upper()
    retry_class = retry or (
        RetryClass.SAFE.value if normalized_method in SAFE_HTTP_METHODS else RetryClass.NEVER.value
    )
    return EndpointSpec(
        name=name,
        domain=domain,
        http_method=normalized_method,
        endpoint=path,
        supported_versions=tuple(
            dict.fromkeys((version, *(item.api_version for item in variants)))
        ),
        default_version=version,
        demo_available=demo,
        idempotent=normalized_method in IDEMPOTENT_HTTP_METHODS,
        requires_session=requires_session,
        timeout_class=timeout,
        retry_class=retry_class,
        route_variants=variants,
        external_code=external_code,
        billable=billable,
    )


ENDPOINT_SPECS = (
    endpoint(
        "attach_card",
        "users",
        "POST",
        "users/{user_id}/attachCard",
        "v2",
        external_code="users_attach_card",
        billable=True,
    ),
    endpoint(
        "attach_contracts",
        "users",
        "POST",
        "users/{user_id}/attachContracts",
        "v2",
        external_code="users_attach_contracts",
        billable=True,
    ),
    endpoint(
        "auth_user",
        "auth",
        "POST",
        "authUser",
        "v1",
        timeout="auth",
        retry="network_only",
        requires_session=False,
        external_code="authuser",
        billable=False,
    ),
    endpoint(
        "block_card", "cards", "POST", "blockCard", "v1", external_code="blockcard", billable=True
    ),
    endpoint(
        "check_purchase",
        "final_prices",
        "POST",
        "cards/{card_id}/checkPurchase",
        "v2",
        demo=False,
        external_code="check_purchase",
        billable=False,
    ),
    endpoint(
        "confirm_mpc",
        "virtual_cards",
        "POST",
        "cards/{card_id}/confirmMPC",
        "v2",
        demo=False,
        external_code="confirm_mpc",
        billable=False,
    ),
    endpoint(
        "create_invite",
        "invites",
        "POST",
        "invites",
        "v2",
        demo=False,
        variants=(
            route(
                "POST",
                "invites_free",
                "v2",
                demo=True,
                name="without_send",
                external_code="invites_post_free",
                billable=False,
            ),
        ),
        external_code="invites_post",
        billable=True,
    ),
    endpoint(
        "create_template",
        "templates",
        "POST",
        "vc/templates",
        "v2",
        external_code="vc_templates_post",
        billable=True,
    ),
    endpoint(
        "create_template_georestriction",
        "templates",
        "POST",
        "vc/templates/{template_id}/georestrictions",
        "v2",
        external_code="vc_templates_georestrictions_post",
        billable=True,
    ),
    endpoint(
        "create_template_limit",
        "templates",
        "POST",
        "vc/templates/{template_id}/limits",
        "v2",
        external_code="vc_templates_limits_post",
        billable=True,
    ),
    endpoint(
        "create_template_restriction",
        "templates",
        "POST",
        "vc/templates/{template_id}/restrictions",
        "v2",
        external_code="vc_templates_restrictions_post",
        billable=True,
    ),
    endpoint(
        "create_user", "users", "POST", "users", "v2", external_code="users_post", billable=True
    ),
    endpoint(
        "create_virtual_card",
        "virtual_cards",
        "POST",
        "cards",
        "v2",
        demo=False,
        external_code="cards_post",
        billable=True,
    ),
    endpoint(
        "delete_invite",
        "invites",
        "DELETE",
        "invites/{invite_id}",
        "v2",
        variants=(
            route(
                "POST",
                "invites/{invite_id}",
                "v2",
                demo=True,
                name="post_override",
            ),
        ),
        external_code="invites_delete",
        billable=False,
    ),
    endpoint(
        "delete_mpc",
        "virtual_cards",
        "POST",
        "cards/{card_id}/deleteMPC",
        "v2",
        demo=False,
        external_code="delete_mpc",
        billable=False,
    ),
    endpoint(
        "delete_template",
        "templates",
        "DELETE",
        "vc/templates/{template_id}",
        "v2",
        variants=(
            route(
                "POST",
                "vc/templates/{template_id}",
                "v2",
                demo=True,
                name="post_override",
            ),
        ),
        external_code="vc_templates_delete",
        billable=True,
    ),
    endpoint(
        "delete_template_georestriction",
        "templates",
        "DELETE",
        "vc/templates/{template_id}/georestrictions/{georestriction_id}",
        "v2",
        variants=(
            route(
                "DELETE",
                "vc/templates/{template_id}/georestrictions/{georestrictions_id}",
                "v2",
                demo=True,
                name="plural_id",
                external_code="vc_templates_georestrictions_delete",
                billable=True,
            ),
            route(
                "POST",
                "vc/templates/{template_id}/georestrictions/{georestriction_id}",
                "v2",
                demo=True,
                name="post_override",
            ),
        ),
    ),
    endpoint(
        "delete_template_limit",
        "templates",
        "DELETE",
        "vc/templates/{template_id}/limits/{limit_id}",
        "v2",
        variants=(
            route(
                "POST",
                "vc/templates/{template_id}/limits/{limit_id}",
                "v2",
                demo=True,
                name="post_override",
            ),
        ),
        external_code="vc_templates_limits_delete",
        billable=True,
    ),
    endpoint(
        "delete_template_restriction",
        "templates",
        "DELETE",
        "vc/templates/{template_id}/restrictions/{restriction_id}",
        "v2",
        variants=(
            route(
                "DELETE",
                "vc/templates/{template_id}/restrictions/{restrictions_id}",
                "v2",
                demo=True,
                name="plural_id",
                external_code="vc_templates_restrictions_delete",
                billable=True,
            ),
            route(
                "POST",
                "vc/templates/{template_id}/restrictions/{restriction_id}",
                "v2",
                demo=True,
                name="post_override",
            ),
        ),
    ),
    endpoint(
        "delete_user",
        "users",
        "DELETE",
        "users/{user_id}",
        "v2",
        variants=(route("POST", "users/{user_id}", "v2", demo=True, name="post_override"),),
        external_code="users_delete",
        billable=True,
    ),
    endpoint(
        "detach_card",
        "users",
        "POST",
        "users/{user_id}/detachCard",
        "v2",
        external_code="users_detach_card",
        billable=True,
    ),
    endpoint(
        "detach_contracts",
        "users",
        "POST",
        "users/{user_id}/detachContracts",
        "v2",
        external_code="users_detach_contracts",
        billable=True,
    ),
    endpoint(
        "download_report_file",
        "reports",
        "GET",
        "reports/jobs/{job_id}",
        "v2",
        demo=False,
        timeout="read_heavy",
        external_code="reports_jobs_file",
        billable=True,
    ),
    endpoint(
        "download_report_file_v1",
        "reports",
        "GET",
        "getReportFile",
        "v1",
        demo=False,
        timeout="read_heavy",
        external_code="getreportfile",
        billable=True,
    ),
    endpoint(
        "generate_payment_qr",
        "virtual_cards",
        "POST",
        "cards/{card_id}/pay",
        "v2",
        demo=False,
        external_code="pay",
        billable=False,
    ),
    endpoint(
        "get_azs_filters",
        "dictionaries",
        "GET",
        "azs/filters",
        "v2",
        demo=False,
        timeout="read_heavy",
        external_code="filters",
        billable=False,
    ),
    endpoint(
        "get_azs_list_v1",
        "dictionaries",
        "GET",
        "AZS",
        "v1",
        timeout="read_heavy",
        external_code="azs",
        billable=False,
    ),
    endpoint(
        "get_azs_list_v2",
        "dictionaries",
        "GET",
        "azs",
        "v2",
        demo=False,
        timeout="read_heavy",
        external_code="poi",
        billable=False,
    ),
    endpoint(
        "get_card_detail",
        "cards",
        "GET",
        "cards",
        "v1",
        timeout="read_heavy",
        external_code="cards_detail",
        billable=True,
    ),
    endpoint(
        "get_card_drivers",
        "cards",
        "GET",
        "cards/{card_id}/drivers",
        "v2",
        timeout="read_heavy",
        external_code="cards_drivers",
        billable=True,
    ),
    endpoint(
        "get_card_groups",
        "card_group",
        "GET",
        "cardGroups",
        "v1",
        timeout="read_heavy",
        external_code="cardgroups",
        billable=False,
    ),
    endpoint(
        "get_card_transactions_v2",
        "transactions",
        "GET",
        "cards/{card_id}/transactions",
        "v2",
        timeout="read_heavy",
        external_code="card_transactions",
        billable=True,
    ),
    endpoint(
        "get_cards_by_group",
        "cards",
        "GET",
        "cards",
        "v1",
        demo=False,
        timeout="read_heavy",
        external_code="cards_group",
        billable=False,
    ),
    endpoint(
        "get_cards_v1",
        "cards",
        "GET",
        "cards",
        "v1",
        timeout="read_heavy",
        external_code="cards",
        billable=True,
    ),
    endpoint(
        "get_cards_v2",
        "cards",
        "GET",
        "cards",
        "v2",
        timeout="read_heavy",
        external_code="cards_cache",
        billable=False,
    ),
    endpoint(
        "get_contract_data",
        "contract",
        "GET",
        "getPartContractData",
        "v1",
        timeout="read_heavy",
        external_code="getpartcontractdata",
        billable=True,
    ),
    endpoint(
        "get_dictionary",
        "dictionaries",
        "GET",
        "getDictionary",
        "v1",
        timeout="read_heavy",
        external_code="getdictionary",
        billable=False,
    ),
    endpoint(
        "get_documents",
        "contract",
        "GET",
        "documents",
        "v2",
        demo=False,
        timeout="read_heavy",
        external_code="documents_get",
        billable=False,
    ),
    endpoint(
        "get_final_prices",
        "final_prices",
        "POST",
        "cards/{card_id}/calculatePrices",
        "v2",
        demo=False,
        external_code="calculate_prices",
        billable=False,
    ),
    endpoint(
        "get_info",
        "auth",
        "GET",
        "info",
        "v1",
        timeout="read_heavy",
        external_code="info",
        billable=False,
    ),
    endpoint(
        "get_invites",
        "invites",
        "GET",
        "invites",
        "v2",
        timeout="read_heavy",
        external_code="invites_get",
        billable=False,
    ),
    endpoint(
        "get_invoices",
        "contract",
        "GET",
        "invoices",
        "v2",
        timeout="read_heavy",
        external_code="invoices",
        billable=False,
    ),
    endpoint(
        "get_limits",
        "limits",
        "GET",
        "limit",
        "v1",
        timeout="read_heavy",
        external_code="limit",
        billable=False,
    ),
    endpoint(
        "get_mpc_qr_list",
        "virtual_cards",
        "GET",
        "MPC",
        "v2",
        demo=False,
        timeout="read_heavy",
        external_code="mpc",
        billable=False,
    ),
    endpoint(
        "get_payments",
        "contract",
        "GET",
        "getPayments",
        "v1",
        timeout="read_heavy",
        external_code="getpayments",
        billable=True,
    ),
    endpoint(
        "get_region_limits",
        "region_limits",
        "GET",
        "regionLimit",
        "v1",
        timeout="read_heavy",
        external_code="regionlimit",
        billable=True,
    ),
    endpoint(
        "get_report_job_list_v1",
        "reports",
        "GET",
        "getReportJobList",
        "v1",
        timeout="read_heavy",
        external_code="getreportjoblist",
        billable=False,
    ),
    endpoint(
        "get_report_jobs",
        "reports",
        "GET",
        "reports/jobs",
        "v2",
        timeout="read_heavy",
        external_code="reports_jobs",
        billable=False,
    ),
    endpoint(
        "get_reports",
        "reports",
        "GET",
        "reports",
        "v2",
        timeout="read_heavy",
        external_code="reports_get",
        billable=False,
    ),
    endpoint(
        "get_restrictions",
        "restrictions",
        "GET",
        "restriction",
        "v1",
        timeout="read_heavy",
        external_code="restriction",
        billable=True,
    ),
    endpoint(
        "get_template_georestrictions",
        "templates",
        "GET",
        "vc/templates/{template_id}/georestrictions",
        "v2",
        timeout="read_heavy",
        external_code="vc_templates_georestrictions_get",
        billable=False,
    ),
    endpoint(
        "get_template_limits",
        "templates",
        "GET",
        "vc/templates/{template_id}/limits",
        "v2",
        timeout="read_heavy",
        external_code="vc_templates_limits_get",
        billable=False,
    ),
    endpoint(
        "get_template_restrictions",
        "templates",
        "GET",
        "vc/templates/{template_id}/restrictions",
        "v2",
        timeout="read_heavy",
        external_code="vc_templates_restrictions_get",
        billable=False,
    ),
    endpoint(
        "get_templates",
        "templates",
        "GET",
        "vc/templates",
        "v2",
        timeout="read_heavy",
        external_code="vc_templates_get",
        billable=False,
    ),
    endpoint(
        "get_transaction_detail",
        "transactions",
        "GET",
        "transactions/{transaction_id}",
        "v2",
        timeout="read_heavy",
        external_code="transaction_detail",
        billable=False,
    ),
    endpoint(
        "get_transactions_v1",
        "transactions",
        "GET",
        "transactions",
        "v1",
        demo=False,
        timeout="read_heavy",
        external_code="transactions",
        billable=True,
    ),
    endpoint(
        "get_transactions_v2",
        "transactions",
        "GET",
        "transactions",
        "v2",
        timeout="read_heavy",
        external_code="contract_transactions",
        billable=True,
    ),
    endpoint(
        "get_users",
        "users",
        "GET",
        "users",
        "v2",
        timeout="read_heavy",
        external_code="users_get",
        billable=False,
    ),
    endpoint(
        "init_mpc",
        "virtual_cards",
        "POST",
        "cards/{card_id}/initMPC",
        "v2",
        demo=False,
        external_code="init_mpc",
        billable=False,
    ),
    endpoint("logoff", "auth", "GET", "logoff", "v1", external_code="logoff", billable=False),
    endpoint(
        "move_to_card",
        "ewallet",
        "POST",
        "moveToCard",
        "v1",
        external_code="movetocard",
        billable=True,
    ),
    endpoint(
        "move_to_contract",
        "ewallet",
        "POST",
        "moveToContract",
        "v1",
        external_code="movetocontract",
        billable=True,
    ),
    endpoint(
        "order_cards",
        "contract",
        "POST",
        "orderCards",
        "v2",
        demo=False,
        external_code="order_cards",
        billable=True,
    ),
    endpoint(
        "order_documents_email",
        "contract",
        "POST",
        "documents",
        "v2",
        demo=False,
        external_code="documents_post",
        billable=True,
    ),
    endpoint(
        "order_invoice",
        "contract",
        "POST",
        "invoice",
        "v2",
        demo=False,
        external_code="invoice",
        billable=False,
    ),
    endpoint(
        "order_report",
        "reports",
        "POST",
        "reports",
        "v2",
        external_code="reports_post",
        billable=True,
    ),
    endpoint(
        "order_report_v1",
        "reports",
        "GET",
        "reports",
        "v1",
        demo=False,
        external_code="reports",
        billable=True,
    ),
    endpoint(
        "prolong_invite",
        "invites",
        "POST",
        "invites/{invite_id}/prolong",
        "v2",
        demo=False,
        variants=(
            route(
                "POST",
                "invites/{invite_id}/prolong_free",
                "v2",
                demo=True,
                name="without_send",
                external_code="invites_prolong_free",
                billable=False,
            ),
        ),
        external_code="invites_prolong",
        billable=True,
    ),
    endpoint(
        "release_virtual_card",
        "virtual_cards",
        "POST",
        "cards/release",
        "v2",
        demo=False,
        external_code="release",
        billable=True,
    ),
    endpoint(
        "remove_card_group",
        "card_group",
        "POST",
        "removeCardGroup",
        "v1",
        external_code="removecardgroup",
        billable=True,
    ),
    endpoint(
        "remove_limit",
        "limits",
        "POST",
        "removeLimit",
        "v1",
        external_code="removelimit",
        billable=True,
    ),
    endpoint(
        "remove_region_limit",
        "region_limits",
        "POST",
        "removeRegionLimit",
        "v1",
        external_code="removeregionlimit",
        billable=True,
    ),
    endpoint(
        "remove_restriction",
        "restrictions",
        "POST",
        "removeRestriction",
        "v1",
        external_code="removerestriction",
        billable=True,
    ),
    endpoint(
        "resend_invite",
        "invites",
        "GET",
        "invites/{invite_id}/send",
        "v2",
        demo=False,
        external_code="invites_send",
        billable=True,
    ),
    endpoint(
        "reset_mpc",
        "virtual_cards",
        "POST",
        "cards/{card_id}/resetMPC",
        "v2",
        demo=False,
        external_code="reset_mpc",
        billable=False,
    ),
    endpoint(
        "reset_pin",
        "cards",
        "POST",
        "cards/{card_id}/resetPIN",
        "v2",
        demo=False,
        external_code="cards_reset_pin",
        billable=True,
    ),
    endpoint(
        "set_card_comment",
        "cards",
        "POST",
        "setCardComment",
        "v1",
        external_code="setcardcomment",
        billable=True,
    ),
    endpoint(
        "set_card_group",
        "card_group",
        "POST",
        "setCardGroup",
        "v1",
        external_code="setcardgroup",
        billable=True,
    ),
    endpoint(
        "set_card_product",
        "ewallet",
        "POST",
        "setCardProduct",
        "v1",
        external_code="setcardproduct",
        billable=True,
    ),
    endpoint(
        "set_cards_to_group",
        "card_group",
        "POST",
        "setCardsToGroup",
        "v1",
        external_code="setcardstogroup",
        billable=True,
    ),
    endpoint(
        "set_limit", "limits", "POST", "setLimit", "v1", external_code="setlimit", billable=True
    ),
    endpoint(
        "set_region_limit",
        "region_limits",
        "POST",
        "setRegionLimit",
        "v1",
        external_code="setregionlimit",
        billable=True,
    ),
    endpoint(
        "set_restriction",
        "restrictions",
        "POST",
        "setRestriction",
        "v1",
        demo=False,
        external_code="setrestriction",
        billable=True,
    ),
    endpoint(
        "update_mpc",
        "virtual_cards",
        "POST",
        "cards/{card_id}/updateMPC",
        "v2",
        demo=False,
        external_code="update_mpc",
        billable=False,
    ),
    endpoint(
        "update_template",
        "templates",
        "POST",
        "vc/templates/{template_id}",
        "v2",
        variants=(
            route(
                "PUT",
                "vc/templates/{template_id}",
                "v2",
                demo=True,
                name="put",
                external_code="vc_templates_put",
                billable=True,
            ),
        ),
    ),
    endpoint(
        "update_template_georestriction",
        "templates",
        "POST",
        "vc/templates/{template_id}/georestrictions/{georestriction_id}",
        "v2",
        variants=(
            route(
                "PUT",
                "vc/templates/{template_id}/georestrictions/{georestriction_id}",
                "v2",
                demo=True,
                name="put",
            ),
            route(
                "PUT",
                "vc/templates/{template_id}/georestrictions/{georestrictions_id}",
                "v2",
                demo=True,
                name="put_plural_id",
                external_code="vc_templates_georestrictions_put",
                billable=True,
            ),
        ),
    ),
    endpoint(
        "update_template_limit",
        "templates",
        "POST",
        "vc/templates/{template_id}/limits/{limit_id}",
        "v2",
        variants=(
            route(
                "PUT",
                "vc/templates/{template_id}/limits/{limit_id}",
                "v2",
                demo=True,
                name="put",
                external_code="vc_templates_limits_put",
                billable=True,
            ),
        ),
    ),
    endpoint(
        "update_template_restriction",
        "templates",
        "POST",
        "vc/templates/{template_id}/restrictions/{restriction_id}",
        "v2",
        variants=(
            route(
                "PUT",
                "vc/templates/{template_id}/restrictions/{restriction_id}",
                "v2",
                demo=True,
                name="put",
            ),
            route(
                "PUT",
                "vc/templates/{template_id}/restrictions/{restrictions_id}",
                "v2",
                demo=True,
                name="put_plural_id",
                external_code="vc_templates_restrictions_put",
                billable=True,
            ),
        ),
    ),
    endpoint(
        "verify_pin",
        "cards",
        "POST",
        "cards/{card_id}/verifyPIN",
        "v2",
        external_code="cards_verify_pin",
        billable=False,
    ),
)
