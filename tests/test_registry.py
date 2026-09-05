import ast
import importlib
import json
import pkgutil
from pathlib import Path

import pytest

import api_client_opti24.services as service_package
from api_client_opti24.authentication import AUTH_USER
from api_client_opti24.contracts import serialize_registry_contract
from api_client_opti24.modeling import APIEnvelope, ResponseModel
from api_client_opti24.operations import Operation
from api_client_opti24.registry import (
    EndpointSpec,
    MethodRegistry,
    MethodSpec,
    RouteVariant,
    build_default_registry,
)

ENDPOINT_CONTRACT_PATH = Path(__file__).with_name("contracts") / "endpoints.json"


def test_registry_covers_all_declared_endpoints():
    registry = build_default_registry()

    assert len(registry.list_all()) == 89
    assert all(spec.name != "list_qr_mpc" for spec in registry.list_all())
    assert MethodSpec is EndpointSpec


def test_registry_matches_versioned_endpoint_contract_snapshot():
    expected = json.loads(ENDPOINT_CONTRACT_PATH.read_text(encoding="utf-8"))

    assert serialize_registry_contract(build_default_registry()) == expected


def test_registry_contains_default_versions_for_supported_methods():
    registry = build_default_registry()

    auth_spec = registry.get("auth_user")
    cards_spec = registry.get("get_cards_v2")

    assert auth_spec.default_version == "v1"
    assert auth_spec.supported_versions == ("v1",)
    assert cards_spec.default_version == "v2"
    assert cards_spec.supported_versions == ("v2",)


def test_registry_can_resolve_method_by_endpoint_and_version():
    registry = build_default_registry()

    spec = registry.find_by_endpoint("cards", "v2")

    assert spec is not None
    assert spec.name == "get_cards_v2"
    assert spec.domain == "cards"


def test_registry_contains_parameterized_and_stream_endpoints():
    registry = build_default_registry()

    card_drivers = registry.get("get_card_drivers")
    report_file = registry.get("download_report_file")

    assert card_drivers.endpoint == "cards/{card_id}/drivers"
    assert card_drivers.http_method == "GET"
    assert report_file.endpoint == "reports/jobs/{job_id}"
    assert report_file.supported_versions == ("v2",)


def test_registry_resolves_alias_routes_for_invites_and_templates():
    registry = build_default_registry()

    invite_free = registry.find_by_endpoint("invites_free", "v2", http_method="POST")
    prolong_free = registry.find_by_endpoint(
        "invites/{invite_id}/prolong_free",
        "v2",
        http_method="POST",
    )
    update_template_limit = registry.find_by_endpoint(
        "vc/templates/{template_id}/limits/{limit_id}",
        "v2",
        http_method="PUT",
    )

    assert invite_free is not None
    assert invite_free.name == "create_invite"
    assert prolong_free is not None
    assert prolong_free.name == "prolong_invite"
    assert update_template_limit is not None
    assert update_template_limit.name == "update_template_limit"


def test_registry_contains_demo_flags_for_demo_restricted_methods():
    registry = build_default_registry()

    assert registry.get("get_cards_v1").demo_available is True
    assert registry.get("get_cards_by_group").demo_available is False
    assert registry.get("create_invite").demo_available is False
    assert registry.get("get_mpc_qr_list").demo_available is False


def test_registry_disables_network_retry_for_write_methods():
    registry = build_default_registry()

    assert registry.get("get_cards_v2").retry_class == "safe"
    assert registry.get("order_invoice").retry_class == "never"
    assert registry.get("auth_user").retry_class == "network_only"


def test_registry_contains_explicit_auth_metadata():
    registry = build_default_registry()

    auth = registry.get("auth_user")

    assert auth.http_method == "POST"
    assert auth.endpoint == "authUser"
    assert auth.requires_session is False


def test_registry_routes_render_only_exact_safe_path_parameters():
    route = build_default_registry().get("get_card_drivers").resolve_route()

    assert route.render({"card_id": "card 1"}) == "cards/card%201/drivers"
    with pytest.raises(ValueError, match="missing: card_id"):
        route.render()
    with pytest.raises(ValueError, match="unexpected: extra"):
        route.render({"card_id": "card-1", "extra": "value"})
    with pytest.raises(ValueError, match="Unsafe path parameter"):
        route.render({"card_id": "../admin"})


def test_services_call_their_explicit_registry_operation() -> None:
    service_directory = Path("src/api_client_opti24/services")
    operations: set[str] = set()

    for service_file in service_directory.glob("*.py"):
        tree = ast.parse(service_file.read_text(encoding="utf-8"))
        bindings = {
            target.id: statement.value.args[0].value
            for statement in tree.body
            if isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance((target := statement.targets[0]), ast.Name)
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Name)
            and statement.value.func.id in {"operation", "binary_operation"}
            and statement.value.args
            and isinstance(statement.value.args[0], ast.Constant)
        }
        for function in (node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)):
            calls = [
                node
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"_request", "_request_stream", "_request_stream_to_file"}
            ]
            if not calls:
                continue
            assert len(calls) == 1, f"{service_file.name}:{function.name} must execute once"
            operation_arg = calls[0].args[0]
            assert isinstance(operation_arg, ast.Name)
            operation_name = bindings[operation_arg.id]
            expected_name = function.name.removesuffix("_to")
            assert operation_name == expected_name
            assert all(keyword.arg != "headers" for keyword in calls[0].keywords)
            operations.add(operation_name)

    authentication_tree = ast.parse(
        Path("src/api_client_opti24/authentication.py").read_text(encoding="utf-8")
    )
    authenticator = next(
        node
        for node in ast.walk(authentication_tree)
        if isinstance(node, ast.ClassDef) and node.name == "DefaultAuthenticator"
    )
    authenticate = next(
        node
        for node in authenticator.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "authenticate"
    )
    auth_calls = [
        node
        for node in ast.walk(authenticate)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "execute"
    ]
    assert len(auth_calls) == 1
    assert isinstance(auth_calls[0].args[0], ast.Name)
    assert auth_calls[0].args[0].id == "AUTH_USER"
    operations.add("auth_user")

    assert operations == {spec.name for spec in build_default_registry().list_all()}


def test_typed_operations_cover_registry_and_use_response_models() -> None:
    registry = build_default_registry()
    operations = {AUTH_USER.name: AUTH_USER}
    for module_info in pkgutil.iter_modules(service_package.__path__):
        module = importlib.import_module(f"{service_package.__name__}.{module_info.name}")
        for value in vars(module).values():
            if isinstance(value, Operation):
                operations[value.name] = value

    assert set(operations) == {spec.name for spec in registry.list_all()}
    for name, typed_operation in operations.items():
        if typed_operation.response_kind == "bytes":
            assert typed_operation.response_type is None
            continue
        response_type = typed_operation.response_type
        assert response_type is not None
        assert issubclass(response_type, ResponseModel)
        if registry.get(name).domain != "virtual_cards":
            assert issubclass(response_type, APIEnvelope)


def test_external_metadata_is_declared_inline_with_endpoint_routes() -> None:
    endpoint_source = Path("src/api_client_opti24/endpoints.py").read_text(encoding="utf-8")
    tree = ast.parse(endpoint_source)
    endpoint_catalog = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "ENDPOINT_SPECS"
            for target in node.targets
        )
    )
    assert isinstance(endpoint_catalog.value, ast.Tuple)

    external_codes: set[str] = set()
    for endpoint_call in endpoint_catalog.value.elts:
        assert isinstance(endpoint_call, ast.Call)
        metadata_calls = [
            node
            for node in ast.walk(endpoint_call)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"endpoint", "route"}
            and {keyword.arg for keyword in node.keywords} >= {"external_code", "billable"}
        ]
        assert metadata_calls, "Each operation must declare external metadata inline"
        for call in metadata_calls:
            external_code = next(
                keyword.value for keyword in call.keywords if keyword.arg == "external_code"
            )
            assert isinstance(external_code, ast.Constant)
            external_codes.add(external_code.value)

    assert len(external_codes) == 91
    assert "_EXTERNAL_BINDINGS" not in endpoint_source
    assert "_apply_external_bindings" not in endpoint_source


def test_registry_rejects_duplicate_method_names():
    spec = MethodSpec(
        name="duplicate",
        domain="test",
        http_method="GET",
        endpoint="first",
        supported_versions=("v1",),
        default_version="v1",
        demo_available=True,
        idempotent=True,
    )
    registry = MethodRegistry()
    registry.register(spec)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(spec)


def test_endpoint_spec_preserves_legacy_optional_positional_order() -> None:
    spec = MethodSpec(
        "legacy-constructor",
        "test",
        "GET",
        "items",
        ("v1",),
        "v1",
        True,
        True,
        False,
        "bulk",
        "never",
        (),
    )

    assert spec.requires_session is False
    assert spec.timeout_class == "bulk"
    assert spec.retry_class == "never"
    assert spec.external_code is None
    assert spec.billable is None


def test_registry_rejects_duplicate_named_routes():
    spec = MethodSpec(
        name="duplicate-routes",
        domain="test",
        http_method="GET",
        endpoint="items",
        supported_versions=("v1",),
        default_version="v1",
        demo_available=True,
        idempotent=True,
        route_variants=(RouteVariant("GET", "other-items", "v1", True, "default"),),
    )

    with pytest.raises(ValueError, match="duplicate named routes"):
        MethodRegistry().register(spec)
