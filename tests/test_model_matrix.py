from __future__ import annotations

import json
from pathlib import Path

from apisdkopti24.registry import build_default_registry

MATRIX_PATH = Path(__file__).parents[1] / "specifications" / "model-matrix-v1.1.60.json"


def test_model_matrix_covers_all_operations_and_describes_every_field() -> None:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    operations = matrix["operations"]
    names = [entry["operation"] for entry in operations]
    assert matrix["operation_count"] == 89
    assert len(names) == len(set(names)) == 89
    assert set(names) == {item.name for item in build_default_registry().list_all()}
    for operation in operations:
        assert operation["source"]
        assert operation["response_model"]
        for variant in operation["variants"]:
            for field in [*variant["request"], *variant["response"]]:
                assert field["path"]
                assert field["type"]
                assert field["required"] in {True, False, "conditional"}
                if field["required"] == "conditional":
                    assert field["required_condition"]
                assert field["description"]
                assert field["location"] in {"path", "query", "header", "form", "json", "response"}
