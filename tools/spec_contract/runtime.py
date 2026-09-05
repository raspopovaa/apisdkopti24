from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from functools import cache
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel as PydanticBaseModel

SERVICE_CLASS_PATHS = {
    "auth": "api_client_opti24.services.auth.AuthService",
    "card_groups": "api_client_opti24.services.card_group.CardGroupsService",
    "cards": "api_client_opti24.services.cards.CardsService",
    "contracts": "api_client_opti24.services.contract.ContractsService",
    "dictionaries": "api_client_opti24.services.dictionaries.DictionariesService",
    "ewallet": "api_client_opti24.services.ewallet.EwalletService",
    "final_prices": "api_client_opti24.services.final_prices.FinalPricesService",
    "invites": "api_client_opti24.services.invites.InvitesService",
    "limits": "api_client_opti24.services.limits.LimitsService",
    "region_limits": "api_client_opti24.services.region_limits.RegionLimitsService",
    "reports": "api_client_opti24.services.reports.ReportsService",
    "restrictions": "api_client_opti24.services.restrictions.RestrictionsService",
    "templates": "api_client_opti24.services.templates.TemplatesService",
    "transactions": "api_client_opti24.services.transactions.TransactionsService",
    "users": "api_client_opti24.services.users.UsersService",
    "virtual_cards": "api_client_opti24.services.virtual_cards.VirtualCardsService",
}


@dataclass(frozen=True, slots=True)
class ResolvedField:
    annotation: Any
    required: bool | None
    generic: bool


@cache
def resolve_object(dotted_path: str) -> Any:
    module_name, _, attribute_path = dotted_path.rpartition(".")
    if not module_name or not attribute_path:
        raise ValueError(f"Invalid dotted path: {dotted_path}")
    value: Any = importlib.import_module(module_name)
    for part in attribute_path.split("."):
        value = getattr(value, part)
    return value


@cache
def resolve_service_class(service: str) -> type:
    try:
        path = SERVICE_CLASS_PATHS[service]
    except KeyError as exc:
        raise KeyError(f"Unknown SDK service: {service}") from exc
    value = resolve_object(path)
    if not inspect.isclass(value):
        raise TypeError(f"Service path does not resolve to a class: {path}")
    return value


@cache
def resolve_service_method(service: str, operation: str) -> Any:
    service_class = resolve_service_class(service)
    method = getattr(service_class, operation, None)
    if method is None or not inspect.isfunction(method):
        raise AttributeError(f"Public method client.{service}.{operation}() is missing")
    return method


def resolve_return_annotation(method: Any) -> Any:
    return unwrap_optional(get_type_hints(method).get("return"))


def resolve_response_model(method: Any) -> type[PydanticBaseModel] | None:
    annotation = resolve_return_annotation(method)
    if inspect.isclass(annotation) and issubclass(annotation, PydanticBaseModel):
        return annotation
    return None


def unwrap_optional(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin in {Union, UnionType}:
        non_none = tuple(item for item in get_args(annotation) if item is not type(None))
        if len(non_none) == 1:
            return unwrap_optional(non_none[0])
    return annotation


def unwrap_collection(annotation: Any, *, expects_array: bool) -> tuple[Any, bool]:
    annotation = unwrap_optional(annotation)
    origin = get_origin(annotation)
    if expects_array:
        if origin in {list, tuple, set, frozenset}:
            args = get_args(annotation)
            return (unwrap_optional(args[0]) if args else Any), False
        if annotation is Any:
            return Any, True
        return annotation, False
    return annotation, annotation is Any


def is_generic_annotation(annotation: Any) -> bool:
    annotation = unwrap_optional(annotation)
    if annotation is Any:
        return True
    origin = get_origin(annotation)
    if origin is dict:
        args = get_args(annotation)
        return not args or Any in args
    return False


def _model_field(model: type[PydanticBaseModel], name: str) -> tuple[Any, str] | None:
    for field_name, model_field in model.model_fields.items():
        candidates = {field_name}
        if isinstance(model_field.alias, str):
            candidates.add(model_field.alias)
        if name in candidates:
            return model_field, field_name
    return None


def resolve_model_field(model: type[PydanticBaseModel], path: str) -> ResolvedField | None:
    current: Any = model
    required: bool | None = None
    generic = False
    tokens = [token for token in path.split(".") if token]
    for token in tokens:
        expects_array = token.endswith("[]")
        name = token[:-2] if expects_array else token
        current = unwrap_optional(current)
        if is_generic_annotation(current):
            return ResolvedField(annotation=Any, required=required, generic=True)
        if not inspect.isclass(current) or not issubclass(current, PydanticBaseModel):
            return None
        found = _model_field(current, name)
        if found is None:
            return None
        model_field, _ = found
        required = model_field.is_required()
        current, collection_generic = unwrap_collection(
            model_field.annotation,
            expects_array=expects_array,
        )
        generic = generic or collection_generic or is_generic_annotation(model_field.annotation)
    return ResolvedField(annotation=current, required=required, generic=generic)


def format_annotation(annotation: Any) -> str:
    if annotation is Any:
        return "Any"
    if annotation is None or annotation is type(None):
        return "None"
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in {Union, UnionType}:
        return " | ".join(format_annotation(item) for item in args)
    if origin is not None:
        name = getattr(origin, "__name__", str(origin).replace("typing.", ""))
        return f"{name}[{', '.join(format_annotation(item) for item in args)}]"
    return getattr(annotation, "__name__", str(annotation).replace("typing.", ""))


def request_model_usage(method: Any, request_model: type[PydanticBaseModel]) -> str:
    try:
        source = inspect.getsource(method)
        tree = ast.parse(inspect.cleandoc(source))
    except (OSError, TypeError, SyntaxError):
        return "indirect-or-unknown"
    target = request_model.__name__
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name) and function.id == target:
            return "used-directly"
        if isinstance(function, ast.Attribute) and function.attr in {target, "model_validate"}:
            if function.attr == target:
                return "used-directly"
            if isinstance(function.value, ast.Name) and function.value.id == target:
                return "used-directly"
    return "not-used"


def iter_sdk_models() -> tuple[type[PydanticBaseModel], ...]:
    package = importlib.import_module("api_client_opti24.models")
    result: dict[str, type[PydanticBaseModel]] = {}
    for info in pkgutil.walk_packages(package.__path__, prefix="api_client_opti24.models."):
        module = importlib.import_module(info.name)
        for _, value in inspect.getmembers(module, inspect.isclass):
            if value is PydanticBaseModel or not issubclass(value, PydanticBaseModel):
                continue
            if value.__module__ != module.__name__:
                continue
            result[f"{value.__module__}.{value.__qualname__}"] = value
    return tuple(result[name] for name in sorted(result))


def untyped_model_fields() -> tuple[tuple[str, str, str], ...]:
    findings: list[tuple[str, str, str]] = []
    for model in iter_sdk_models():
        for name, model_field in model.model_fields.items():
            if is_generic_annotation(model_field.annotation):
                findings.append(
                    (
                        f"{model.__module__}.{model.__qualname__}",
                        name,
                        format_annotation(model_field.annotation),
                    )
                )
    return tuple(findings)
