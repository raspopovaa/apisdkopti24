from api_client_opti24.payloads import with_method_override


def test_method_override_copies_mapping() -> None:
    payload = {"contract_id": "contract-1"}

    result = with_method_override(payload, "delete")

    assert result == {"contract_id": "contract-1", "_method": "DELETE"}
    assert payload == {"contract_id": "contract-1"}


def test_method_override_copies_sequence_items() -> None:
    payload = [{"contract_id": "contract-1"}]

    result = with_method_override(payload, "put")

    assert result == [{"contract_id": "contract-1", "_method": "PUT"}]
    assert payload == [{"contract_id": "contract-1"}]


def test_method_override_builds_body_for_empty_delete() -> None:
    assert with_method_override(None, "delete") == {"_method": "DELETE"}
