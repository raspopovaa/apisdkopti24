from __future__ import annotations

import argparse
import importlib
import inspect
import pkgutil
import re
import sys
import types
from collections import Counter
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

import yaml
from pydantic import BaseModel as PydanticBaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from api_client_opti24.modeling import StrictRequestModel
from api_client_opti24.registry import build_default_registry
from api_client_opti24.service_groups import ServiceContainer

EXPECTED_SOURCE_VERSION = "1.1.60"
EXPECTED_ENVELOPE_FIELDS = ["status", "data", "timestamp"]
LEGACY_POSITIONAL_OPERATIONS = {"delete_mpc", "reset_mpc"}
ALLOWED_UNDOCUMENTED_OPERATIONS = {
    "confirm_mpc",
    "generate_payment_qr",
    "get_mpc_qr_list",
    "init_mpc",
    "update_mpc",
}
ALLOWED_SDK_PARAMETER_MIGRATIONS = {
    ("set_limit", "limits"): (
        "list[LimitRequestItem | collections.abc.Mapping[str, Any]]",
        "list[LimitRequestItem]",
    ),
    ("set_region_limit", "region_limits"): (
        "list[RegionLimitRequestItem | collections.abc.Mapping[str, Any]]",
        "list[RegionLimitRequestItem]",
    ),
    ("set_restriction", "restrictions"): (
        "list[RestrictionRequestItem | collections.abc.Mapping[str, Any]]",
        "list[RestrictionRequestItem]",
    ),
}
DOMAIN_SERVICE = {
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


class APIContractMismatchError(AssertionError):
    pass


def _annotation_name(annotation: Any) -> str:
    if annotation is inspect.Parameter.empty:
        return "Any"
    if annotation is None or annotation is type(None):
        return "None"
    if annotation is Any:
        return "Any"
    origin = get_origin(annotation)
    arguments = get_args(annotation)
    if origin in {Union, types.UnionType}:
        return " | ".join(_annotation_name(item) for item in arguments)
    if origin is Literal:
        return "Literal[" + ", ".join(repr(item) for item in arguments) + "]"
    if origin is list:
        return f"list[{_annotation_name(arguments[0])}]"
    if origin is dict:
        return f"dict[{_annotation_name(arguments[0])}, {_annotation_name(arguments[1])}]"
    if origin is tuple:
        return "tuple[" + ", ".join(_annotation_name(item) for item in arguments) + "]"
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation).replace("typing.", "")


def _default_value(parameter: inspect.Parameter) -> object:
    if parameter.default is inspect.Parameter.empty:
        return None
    value = parameter.default
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _validation_aliases(field: Any, name: str) -> list[str]:
    validation_alias = field.validation_alias
    if validation_alias is None:
        return [field.alias or name]
    if isinstance(validation_alias, str):
        return [validation_alias]
    choices = getattr(validation_alias, "choices", None)
    if choices is not None:
        return [str(choice) for choice in choices]
    return [str(validation_alias)]


def _load_contract(path: Path) -> dict[str, Any]:
    raw_text = path.read_text(encoding="utf-8")
    credential_patterns = (
        r"GPN\.[A-Za-z0-9.-]+",
        r"eyJ[A-Za-z0-9._-]{40,}",
        r"auto-generated-pas",
        r"sha512 password:\s*[0-9a-fA-F]{128}",
    )
    if any(re.search(pattern, raw_text) for pattern in credential_patterns):
        raise APIContractMismatchError("The API contract contains an unsanitized credential")
    document = yaml.safe_load(raw_text)
    if not isinstance(document, dict) or document.get("schema_version") != 2:
        raise APIContractMismatchError("Unsupported or missing contract schema_version")
    source = document.get("source")
    if not isinstance(source, dict) or source.get("version") != EXPECTED_SOURCE_VERSION:
        raise APIContractMismatchError("The API contract must reference specification v1.1.60")
    if source.get("stored_in_repository") is not False:
        raise APIContractMismatchError("The source DOCX must remain outside the repository")
    return document


def _actual_parameters(method: Any) -> list[dict[str, object]]:
    signature = inspect.signature(method)
    hints = get_type_hints(method)
    parameters = []
    for name, parameter in signature.parameters.items():
        if name == "self":
            continue
        parameters.append(
            {
                "name": name,
                "type": _annotation_name(hints.get(name, parameter.annotation)),
                "required": parameter.default is inspect.Parameter.empty,
                "keyword_only": parameter.kind is inspect.Parameter.KEYWORD_ONLY,
                "default": _default_value(parameter),
            }
        )
    return parameters


def _parameters_match(
    operation_name: str,
    actual: list[dict[str, object]],
    expected: object,
) -> bool:
    if actual == expected:
        return True
    if not isinstance(expected, list) or len(actual) != len(expected):
        return False

    for actual_parameter, expected_parameter in zip(actual, expected, strict=True):
        if not isinstance(expected_parameter, dict):
            return False
        if actual_parameter == expected_parameter:
            continue

        differing_keys = {
            key
            for key in set(actual_parameter) | set(expected_parameter)
            if actual_parameter.get(key) != expected_parameter.get(key)
        }
        if differing_keys != {"type"}:
            return False

        parameter_name = actual_parameter.get("name")
        expected_type = expected_parameter.get("type")
        actual_type = actual_parameter.get("type")
        if not all(
            isinstance(value, str) for value in (parameter_name, expected_type, actual_type)
        ):
            return False
        if ALLOWED_SDK_PARAMETER_MIGRATIONS.get((operation_name, parameter_name)) != (
            expected_type,
            actual_type,
        ):
            return False

    return True


def _actual_response(method: Any) -> dict[str, object]:
    signature = inspect.signature(method)
    return_type = get_type_hints(method).get("return", signature.return_annotation)
    if return_type is bytes:
        return {"kind": "binary", "model": None, "fields": []}
    if inspect.isclass(return_type) and issubclass(return_type, PydanticBaseModel):
        return {
            "kind": "model",
            "model": return_type.__name__,
            "fields": list(return_type.model_fields),
        }
    return {"kind": "other", "model": _annotation_name(return_type), "fields": []}


def _request_models() -> dict[str, list[dict[str, object]]]:
    models_package = importlib.import_module("api_client_opti24.models")
    result: dict[str, list[dict[str, object]]] = {}
    for module_info in pkgutil.iter_modules(models_package.__path__):
        module = importlib.import_module(f"api_client_opti24.models.{module_info.name}")
        for model in vars(module).values():
            if not inspect.isclass(model) or model is StrictRequestModel:
                continue
            if not issubclass(model, StrictRequestModel) or model.__module__ != module.__name__:
                continue
            result[model.__name__] = [
                {
                    "name": name,
                    "alias": field.alias or name,
                    "validation_aliases": _validation_aliases(field, name),
                    "serialization_alias": field.serialization_alias or field.alias or name,
                    "type": _annotation_name(field.annotation),
                    "required": field.is_required(),
                }
                for name, field in model.model_fields.items()
            ]
    return result


def verify_api_contract(path: Path) -> tuple[int, int]:
    document = _load_contract(path)
    methods = document.get("methods")
    if not isinstance(methods, list):
        raise APIContractMismatchError("Contract methods must be a list")

    codes = [item.get("external_code") for item in methods if isinstance(item, dict)]
    duplicate_codes = sorted(code for code, count in Counter(codes).items() if count > 1)
    if duplicate_codes:
        raise APIContractMismatchError(f"Duplicate external codes: {duplicate_codes}")

    registry = build_default_registry()
    routes = {
        route.external_code: (spec, route)
        for spec in registry.list_all()
        for route in spec.iter_routes()
        if route.external_code is not None
    }
    expected_codes = set(codes)
    if expected_codes != set(routes):
        raise APIContractMismatchError(
            f"External route mismatch: missing={sorted(expected_codes - set(routes))}, "
            f"unexpected={sorted(set(routes) - expected_codes)}"
        )

    service_hints = get_type_hints(ServiceContainer)
    for item in methods:
        if not isinstance(item, dict):
            raise APIContractMismatchError("Every method contract must be a mapping")
        external_code = item["external_code"]
        spec, route = routes[external_code]
        expected_route = {
            "operation": spec.name,
            "route_name": route.name,
            "http_method": route.http_method,
            "api_version": route.api_version,
            "endpoint": route.endpoint,
            "demo_available": route.demo_available,
            "billable": route.billable,
        }
        actual_route = {name: item.get(name) for name in expected_route}
        if actual_route != expected_route:
            raise APIContractMismatchError(
                f"Route mismatch for {external_code}: expected={expected_route}, actual={actual_route}"
            )

        sdk_contract = item.get("sdk")
        if not isinstance(sdk_contract, dict):
            raise APIContractMismatchError(f"Missing SDK contract for {external_code}")
        service_name = DOMAIN_SERVICE[spec.domain]
        if sdk_contract.get("service") != service_name:
            raise APIContractMismatchError(f"Service mismatch for {external_code}")
        service_type = service_hints[service_name]
        method = getattr(service_type, spec.name)
        parameters = _actual_parameters(method)
        if not _parameters_match(spec.name, parameters, sdk_contract.get("parameters")):
            raise APIContractMismatchError(f"Signature mismatch for {spec.name}")
        if spec.name not in LEGACY_POSITIONAL_OPERATIONS and any(
            not parameter["keyword_only"] for parameter in parameters
        ):
            raise APIContractMismatchError(f"Public parameters must be keyword-only: {spec.name}")

        response = _actual_response(method)
        if response != sdk_contract.get("response"):
            raise APIContractMismatchError(f"Response model mismatch for {spec.name}")
        if response["kind"] == "model" and response["fields"] != EXPECTED_ENVELOPE_FIELDS:
            raise APIContractMismatchError(f"Response must use a full envelope: {spec.name}")

        api_contract = item.get("api")
        if not isinstance(api_contract, dict):
            raise APIContractMismatchError(f"Missing API source metadata for {external_code}")
        if api_contract.get("section") is None:
            if spec.name not in ALLOWED_UNDOCUMENTED_OPERATIONS:
                raise APIContractMismatchError(
                    f"Operation is missing from specification v1.1.60: {spec.name}"
                )
        elif api_contract.get("official_example") is None:
            raise APIContractMismatchError(f"Missing official example for {external_code}")

    expected_models = {item["model"]: item["fields"] for item in document.get("request_models", [])}
    actual_models = _request_models()
    if expected_models != actual_models:
        missing = sorted(set(expected_models) - set(actual_models))
        unexpected = sorted(set(actual_models) - set(expected_models))
        changed = sorted(
            name
            for name in set(expected_models) & set(actual_models)
            if expected_models[name] != actual_models[name]
        )
        raise APIContractMismatchError(
            f"Request model mismatch: missing={missing}, unexpected={unexpected}, changed={changed}"
        )
    return len(methods), len(expected_models)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify EndpointSpec, service signatures and Pydantic schemas against API v1.1.60"
    )
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    method_count, model_count = verify_api_contract(args.contract)
    print(
        f"Verified {method_count} API routes and {model_count} request models "
        "against specification v1.1.60"
    )


if __name__ == "__main__":
    main()
