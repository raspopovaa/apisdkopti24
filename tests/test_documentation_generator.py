from __future__ import annotations

import ast
import importlib.util
import inspect
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = PROJECT_ROOT / "scripts" / "generate_docs.py"


def load_generator():
    module_name = "generate_docs"
    spec = importlib.util.spec_from_file_location(module_name, GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_generator_covers_every_publishable_registry_operation() -> None:
    generator = load_generator()
    registry = generator.build_default_registry()
    publishable = {
        operation.name
        for operation in registry.list_all()
        if operation.name not in generator.EXCLUDED_OPERATIONS
    }
    documented = {operation.name for operation in generator.documented_specs()}

    assert documented == publishable
    assert len(registry.list_all()) == 89
    assert not documented.intersection(generator.EXCLUDED_OPERATIONS)

    services = generator.service_classes()
    missing = []
    for operation in generator.documented_specs():
        service_name = generator.SERVICE_NAMES[operation.domain]
        methods = generator.public_service_methods(services[service_name])
        if operation.name not in methods:
            missing.append(f"{service_name}.{operation.name}")

    assert not missing, "Undocumented operations: " + ", ".join(missing)


def test_every_documented_operation_has_docstring_and_return_annotation() -> None:
    generator = load_generator()
    services = generator.service_classes()
    errors = []

    for operation in generator.documented_specs():
        service_name = generator.SERVICE_NAMES[operation.domain]
        method = generator.public_service_methods(services[service_name]).get(operation.name)
        if method is None:
            continue
        if not generator.clean_docstring(method):
            errors.append(f"{service_name}.{operation.name}: missing docstring")
        if "return" not in generator.get_type_hints(method):
            errors.append(f"{service_name}.{operation.name}: missing return annotation")

    assert not errors, "\n".join(errors)


def test_generated_output_is_idempotent_and_has_required_sections() -> None:
    generator = load_generator()
    first = generator.build_all()
    second = generator.build_all()

    assert first == second
    assert generator.DOCS_PATH / "methods.md" in first
    assert generator.DATA_TYPES_PATH / "index.md" in first

    method_pages = {
        path: content for path, content in first.items() if path.parent == generator.METHODS_PATH
    }
    assert method_pages
    for path, content in method_pages.items():
        assert "### Параметры" in content, path
        assert "### Возвращаемое значение" in content, path
        assert "**Тип после валидации:**" in content, path
        assert "### Пример" in content, path


def test_method_return_models_are_expanded() -> None:
    generator = load_generator()
    output = generator.build_all()
    cards_page = output[generator.METHODS_PATH / "cards.md"]

    assert "**Pydantic-модель:**" in cards_page
    assert "#### Поля возвращаемой модели" in cards_page
    assert "| Поле | Тип после валидации | JSON-тип |" in cards_page
    assert "Ответ передаётся в `" in cards_page
    assert "**Вложенные модели:**" in cards_page
    assert "../data-types/cards/" in cards_page


def test_model_pages_describe_actual_pydantic_validation() -> None:
    generator = load_generator()
    output = generator.build_all()
    card_info = output[generator.DATA_TYPES_PATH / "cards" / "CardInfo.md"]

    assert "## Поведение модели" in card_info
    assert "## Поля и проверки" in card_info
    assert "Тип после валидации" in card_info
    assert "JSON-тип" in card_info
    assert "Ограничения схемы" in card_info
    assert "Что проверяет Pydantic" in card_info
    assert "Дополнительные поля (`extra`)" in card_info
    assert "Число → строка" in card_info
    assert "`date_expired`" in card_info
    assert "date-time" in card_info
    assert "Граница проверки" in card_info


def test_custom_field_validators_are_documented() -> None:
    generator = load_generator()
    output = generator.build_all()
    card_detail = output[generator.DATA_TYPES_PATH / "cards" / "CardDetail.md"]

    assert "## Пользовательские валидаторы" in card_detail
    assert "`empty_str_to_none`" in card_detail
    assert "`date_last_usage, date_released`" in card_detail
    assert "before" in card_detail


def test_documented_schema_matches_pydantic_json_schema() -> None:
    generator = load_generator()
    output = generator.build_all()
    card_info = output[generator.DATA_TYPES_PATH / "cards" / "CardInfo.md"]

    models = {model.__name__: model for model in generator.model_types()}
    schema = models["CardInfo"].model_json_schema(by_alias=False)
    date_schema = schema["properties"]["date_expired"]
    formats = {
        branch.get("format") for branch in date_schema.get("anyOf", []) if isinstance(branch, dict)
    }

    assert "date-time" in formats
    assert "формат: 'date-time'" in card_info


def test_generated_python_examples_are_syntactically_valid() -> None:
    generator = load_generator()
    output = generator.build_all()
    for path, content in output.items():
        if path.parent != generator.METHODS_PATH:
            continue
        blocks = content.split("```python")[1:]
        for block in blocks:
            source = block.split("```", 1)[0].strip()
            ast.parse(source)


def test_qr_operations_are_documented() -> None:
    generator = load_generator()
    output = generator.build_all()
    combined = "\n".join(output.values()).lower()

    assert not generator.EXCLUDED_OPERATIONS
    assert "confirmmpc" in combined
    assert "resetmpc" in combined
    assert "paymentqrresponse" in combined


def test_request_models_do_not_claim_automatic_sdk_validation() -> None:
    generator = load_generator()
    output = generator.build_all()
    request_page = output[generator.DATA_TYPES_PATH / "final_prices" / "CheckPurchaseRequest.md"]

    assert "явно создаёт `CheckPurchaseRequest`" in request_page
    assert "не означает, что каждый метод SDK автоматически создаёт её" in request_page
    assert "фактический входной контракт" in request_page


def test_approved_spec_parameter_descriptions_are_applied() -> None:
    generator = load_generator()
    metadata = generator.load_metadata()
    operations = metadata["operations"]
    approved = {
        (operation, parameter): description
        for operation, operation_meta in operations.items()
        for parameter, description in operation_meta.get("parameters", {}).items()
    }

    assert len(approved) == 78
    assert approved[("move_to_card", "amount")] == "Сумма перевода."

    services = generator.service_classes()
    specs = {spec.name: spec for spec in generator.documented_specs()}
    for (operation, parameter), expected in approved.items():
        spec = specs[operation]
        service_name = generator.SERVICE_NAMES[spec.domain]
        method = generator.public_service_methods(services[service_name])[operation]
        assert parameter in inspect.signature(method).parameters, f"{operation}.{parameter}"
        doc_params = generator.parse_param_docs(generator.clean_docstring(method))
        actual = generator.parameter_description(
            parameter, doc_params, metadata, operations[operation]
        )
        assert actual == expected
        assert actual != "Параметр публичного метода SDK."

    output = generator.build_all()
    ewallet_page = output[generator.METHODS_PATH / "ewallet.md"]
    assert "| `amount` | `Decimal` | Да | — | Сумма перевода. |" in ewallet_page
