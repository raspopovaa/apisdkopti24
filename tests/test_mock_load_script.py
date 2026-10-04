"""Нагрузочный скрипт на заглушке HTTP должен оставаться рабочим."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "run_mock_load_test.py"


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_mock_load_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_mock_load_runs_full_sdk_path_with_single_login() -> None:
    script = _load_script()

    summary = await script.run_load_test(total_operations=30, concurrency=10)

    assert summary["auth_calls"] == 1
    assert summary["request_count"] == 31
    assert sum(summary["result_types"].values()) == 30
    assert set(summary["operation_counts"]) == set(script.LOAD_OPERATIONS)
