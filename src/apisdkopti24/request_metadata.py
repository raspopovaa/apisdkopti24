from __future__ import annotations

from .requests import BodyKind, ContractLocation, RequestSpec

_PATH = frozenset(
    [
        "attach_card",
        "attach_contracts",
        "check_purchase",
        "confirm_mpc",
        "create_template_georestriction",
        "create_template_limit",
        "create_template_restriction",
        "delete_invite",
        "delete_mpc",
        "delete_template",
        "delete_template_georestriction",
        "delete_template_limit",
        "delete_template_restriction",
        "delete_user",
        "detach_card",
        "detach_contracts",
        "download_report_file",
        "generate_payment_qr",
        "get_card_drivers",
        "get_card_transactions_v2",
        "get_final_prices",
        "get_template_georestrictions",
        "get_template_limits",
        "get_template_restrictions",
        "get_transaction_detail",
        "init_mpc",
        "prolong_invite",
        "resend_invite",
        "reset_mpc",
        "reset_pin",
        "update_mpc",
        "update_template",
        "update_template_georestriction",
        "update_template_limit",
        "update_template_restriction",
        "verify_pin",
    ]
)
_QUERY = frozenset(
    [
        "download_report_file_v1",
        "get_azs_list_v1",
        "get_azs_list_v2",
        "get_card_detail",
        "get_card_drivers",
        "get_card_groups",
        "get_card_transactions_v2",
        "get_cards_by_group",
        "get_cards_v1",
        "get_cards_v2",
        "get_contract_data",
        "get_dictionary",
        "get_documents",
        "get_info",
        "get_invites",
        "get_limits",
        "get_mpc_qr_list",
        "get_payments",
        "get_region_limits",
        "get_restrictions",
        "get_templates",
        "get_transaction_detail",
        "get_transactions_v1",
        "get_transactions_v2",
        "get_users",
        "order_report_v1",
        "verify_pin",
    ]
)
_FORM = frozenset(
    [
        "attach_card",
        "auth_user",
        "block_card",
        "check_purchase",
        "confirm_mpc",
        "create_template",
        "create_user",
        "create_virtual_card",
        "delete_invite",
        "delete_template",
        "delete_template_georestriction",
        "delete_template_limit",
        "delete_template_restriction",
        "delete_user",
        "detach_card",
        "generate_payment_qr",
        "get_final_prices",
        "init_mpc",
        "move_to_card",
        "move_to_contract",
        "order_cards",
        "order_invoice",
        "release_virtual_card",
        "remove_card_group",
        "remove_limit",
        "remove_region_limit",
        "remove_restriction",
        "reset_mpc",
        "reset_pin",
        "set_card_comment",
        "set_card_group",
        "set_card_product",
        "set_cards_to_group",
        "set_limit",
        "set_region_limit",
        "set_restriction",
        "update_mpc",
        "update_template",
    ]
)
_JSON = frozenset(
    [
        "attach_contracts",
        "create_invite",
        "create_template_georestriction",
        "create_template_limit",
        "create_template_restriction",
        "detach_contracts",
        "order_documents_email",
        "order_report",
        "update_template_georestriction",
        "update_template_limit",
        "update_template_restriction",
    ]
)
_CONTRACT_HEADER = frozenset(
    [
        "block_card",
        "check_purchase",
        "confirm_mpc",
        "create_template",
        "create_template_georestriction",
        "create_template_limit",
        "create_template_restriction",
        "delete_mpc",
        "generate_payment_qr",
        "get_card_detail",
        "get_card_drivers",
        "get_card_groups",
        "get_card_transactions_v2",
        "get_cards_by_group",
        "get_cards_v1",
        "get_cards_v2",
        "get_contract_data",
        "get_documents",
        "get_final_prices",
        "get_invoices",
        "get_limits",
        "get_mpc_qr_list",
        "get_payments",
        "get_region_limits",
        "get_restrictions",
        "get_templates",
        "get_transaction_detail",
        "get_transactions_v1",
        "get_transactions_v2",
        "init_mpc",
        "move_to_card",
        "move_to_contract",
        "order_cards",
        "order_documents_email",
        "order_invoice",
        "order_report_v1",
        "remove_card_group",
        "remove_limit",
        "remove_region_limit",
        "remove_restriction",
        "reset_mpc",
        "reset_pin",
        "set_card_comment",
        "set_card_group",
        "set_card_product",
        "set_cards_to_group",
        "set_limit",
        "set_region_limit",
        "set_restriction",
        "update_mpc",
        "update_template",
        "update_template_georestriction",
        "update_template_limit",
        "update_template_restriction",
        "verify_pin",
    ]
)

# Operations for which the corporate/QR specifications explicitly carry
# contract_id in the request payload in addition to the common contract header.
_CONTRACT_QUERY = frozenset(
    [
        "get_card_detail",
        "get_card_groups",
        "get_cards_by_group",
        "get_cards_v1",
        "get_contract_data",
        "get_limits",
        "get_mpc_qr_list",
        "get_payments",
        "get_region_limits",
        "get_restrictions",
        "get_templates",
        "get_transactions_v1",
        "get_users",
    ]
)
_CONTRACT_FORM = frozenset(
    [
        "create_template",
        "create_virtual_card",
        "set_card_group",
        "set_limit",
        "set_region_limit",
        "set_restriction",
    ]
)
_CONTRACT_JSON = frozenset(
    [
        "create_template_georestriction",
        "create_template_limit",
        "create_template_restriction",
        "update_template_georestriction",
        "update_template_limit",
        "update_template_restriction",
    ]
)


def request_spec_for(name: str) -> RequestSpec:
    body_kind: BodyKind = "json" if name in _JSON else "form" if name in _FORM else "none"
    locations: set[ContractLocation] = set()
    if name in _CONTRACT_HEADER:
        locations.add("header")
    if name in _CONTRACT_QUERY:
        locations.add("query")
    if name in _CONTRACT_FORM:
        locations.add("form")
    if name in _CONTRACT_JSON:
        locations.add("json")
    return RequestSpec(
        has_path=name in _PATH,
        has_query=name in _QUERY,
        body_kind=body_kind,
        contract_locations=frozenset(locations),
    )


__all__ = ["request_spec_for"]
