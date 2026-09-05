import pytest

from api_client_opti24.modeling import (
    BaseModel,
    Field,
    StrictRequestModel,
    ValidationError,
    decode_model,
)
from api_client_opti24.models.auth import AuthUserResponse


class AdapterExample(BaseModel):
    name: str = Field(...)
    count: int = Field(...)


class TypedContainers(BaseModel):
    values: dict[str, int]
    pair: tuple[int, str]


class RequestExample(StrictRequestModel):
    name: str


def test_model_descriptions_are_available():
    description = AuthUserResponse.describe()

    assert "status" in description
    assert description["status"]["description"] == "Статус ответа API"


def test_model_descriptions_render_human_readable_types():
    description = AuthUserResponse.describe()

    assert description["status"]["type"] == "ResponseStatus"
    assert description["data"]["type"] == "AuthUserData"
    assert description["timestamp"]["type"] == "int | None"


def test_model_validate_and_dump_support_incremental_adapter():
    model = decode_model(AdapterExample, {"name": "demo", "count": "2"})

    assert model.count == 2
    assert model.model_dump() == {"name": "demo", "count": 2}


def test_response_model_does_not_globally_coerce_numbers_to_strings():
    with pytest.raises(ValidationError):
        AdapterExample(name=123, count=2)


def test_response_model_preserves_unknown_fields_for_forward_compatibility():
    model = AdapterExample(name="demo", count=2, server_extension={"enabled": True})

    assert model.model_extra == {"server_extension": {"enabled": True}}
    assert model.model_dump()["server_extension"] == {"enabled": True}


def test_request_model_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        RequestExample(name="demo", injected=True)


def test_typed_dict_contents_and_fixed_tuple_are_validated():
    model = TypedContainers(values={"count": "2"}, pair=[1, "ok"])

    assert model.values == {"count": 2}
    assert model.pair == (1, "ok")

    with pytest.raises(ValidationError):
        TypedContainers(values={"count": "invalid"}, pair=[1, "ok"])
    with pytest.raises(ValidationError):
        TypedContainers(values={"count": 2}, pair=[1, "ok", "extra"])
