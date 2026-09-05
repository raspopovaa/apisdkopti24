from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from api_client_opti24.registry import build_default_registry
from tools.spec_contract.loader import load_catalog
from tools.spec_contract.runtime import (
    request_model_usage,
    resolve_object,
    resolve_response_model,
    resolve_return_annotation,
    resolve_service_method,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = PROJECT_ROOT / "specifications" / "contracts" / "1.1.60"


@pytest.fixture(scope="session")
def contract_catalog():
    return load_catalog(CONTRACT_ROOT, repository_root=PROJECT_ROOT)


def test_runtime_registry_matches_normalized_contracts(contract_catalog):
    runtime = {spec.name for spec in build_default_registry().list_all()} - set(
        contract_catalog.manifest.excluded_operations
    )
    assert runtime == set(contract_catalog.operations)


def test_service_methods_and_response_contracts_resolve(contract_catalog):
    for operation in contract_catalog.iter_operations():
        method = resolve_service_method(operation.service, operation.name)
        assert inspect.isfunction(method)
        annotation = resolve_return_annotation(method)
        if operation.response_kind == "binary":
            assert annotation is bytes
        elif operation.response_kind == "mapping":
            assert getattr(annotation, "__origin__", None) is dict or annotation is dict
        else:
            response_model = resolve_response_model(method)
            assert response_model is not None
            assert issubclass(response_model, BaseModel)


def test_declared_request_models_exist_and_usage_is_classified(contract_catalog):
    classified = set()
    for operation in contract_catalog.iter_operations():
        if operation.request_model is None:
            continue
        method = resolve_service_method(operation.service, operation.name)
        request_model = resolve_object(operation.request_model)
        assert issubclass(request_model, BaseModel)
        usage = request_model_usage(method, request_model)
        assert usage in {"used-directly", "not-used", "indirect-or-unknown"}
        classified.add(operation.name)

    assert classified == {
        "attach_contracts",
        "check_purchase",
        "create_invite",
        "order_report",
        "set_cards_to_group",
        "create_template",
        "create_template_limit",
        "create_template_restriction",
        "create_template_georestriction",
    }


def test_verified_fixtures_validate_and_required_data_is_enforced(contract_catalog):
    verified = [
        operation
        for operation in contract_catalog.iter_operations()
        if operation.verification == "verified"
    ]
    assert {operation.name for operation in verified} == {
        "move_to_card",
        "move_to_contract",
        "set_card_product",
    }

    for operation in verified:
        method = resolve_service_method(operation.service, operation.name)
        response_model = resolve_response_model(method)
        assert response_model is not None
        for variant in operation.variants:
            assert variant.fixture is not None
            payload = json.loads(variant.fixture.read_text(encoding="utf-8"))
            model = response_model.model_validate(payload)
            assert model.model_dump()["data"] == payload["data"]

            with_unknown = copy.deepcopy(payload)
            with_unknown["server_extension"] = {"enabled": True}
            parsed = response_model.model_validate(with_unknown)
            assert parsed.model_dump()["server_extension"] == {"enabled": True}

            without_data = copy.deepcopy(payload)
            without_data.pop("data")
            with pytest.raises(ValidationError):
                response_model.model_validate(without_data)
