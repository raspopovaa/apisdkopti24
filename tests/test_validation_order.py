"""Проверки параметров идут до ленивой авторизации.

Без явного ``contract_id`` вызов ``_resolve_contract_id`` выполняет authUser. Ошибка в
параметре, найденная после него, стоит лишнего входа и слота ограничителя частоты, а
документация обещает обратное. Тест разбирает код сервисов и находит проверки и
сборку DTO после первого выбора договора.
"""

import ast
from pathlib import Path

SERVICES_ROOT = Path(__file__).resolve().parents[1] / "src" / "apisdkopti24" / "services"
CONTRACT_RESOLUTION = frozenset({"_resolve_contract_id", "_resolve_batch_contract_id"})
# Вызовы после выбора договора, которые проверяют только сам договор или уже
# проверенные значения.
CONTRACT_ONLY_CALLS = frozenset({"create", "target_query", "model_copy"})
ALLOWED_LATE_CALLS = {
    # TemplateCreateRequest собирается из type_ и name, проверенных до выбора договора.
    ("templates.py", "create_template", "TemplateCreateRequest"),
    ("templates.py", "update_template", "TemplateCreateRequest"),
    # Договор из payload проверяется только при явном contract_id — без входа.
    ("templates.py", "_payload_contract_id", "require_identifier"),
}


def _call_name(node: ast.Call) -> str:
    function = node.func
    if isinstance(function, ast.Attribute):
        return function.attr
    if isinstance(function, ast.Name):
        return function.id
    return ""


def _is_parameter_check(name: str) -> bool:
    return (
        name.startswith(("validate", "require", "parse"))
        or name in {"model_validate", "removal_form", "decimal_to_wire"}
        or name.endswith(("Query", "Request", "Form"))
    )


def _late_checks(path: Path) -> list[str]:
    problems: list[str] = []
    for function in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not isinstance(function, ast.AsyncFunctionDef):
            continue
        calls = sorted(
            (node.lineno, _call_name(node))
            for node in ast.walk(function)
            if isinstance(node, ast.Call)
        )
        resolution_lines = [line for line, name in calls if name in CONTRACT_RESOLUTION]
        if not resolution_lines:
            continue
        for line, name in calls:
            if (
                line > resolution_lines[0]
                and _is_parameter_check(name)
                and name not in CONTRACT_ONLY_CALLS
                and (path.name, function.name, name) not in ALLOWED_LATE_CALLS
            ):
                problems.append(f"{path.name}:{line} {function.name}: {name} после выбора договора")
    return problems


def test_parameters_are_validated_before_the_contract_is_resolved() -> None:
    problems = [
        problem for path in sorted(SERVICES_ROOT.glob("*.py")) for problem in _late_checks(path)
    ]

    assert problems == []


def test_guard_detects_a_check_after_contract_resolution(tmp_path: Path) -> None:
    service = tmp_path / "sample.py"
    service.write_text(
        "async def remove(self, item_id, contract_id=None):\n"
        "    cid = await self._resolve_contract_id(contract_id)\n"
        "    return require_identifier(item_id, 'item_id')\n",
        encoding="utf-8",
    )

    assert _late_checks(service) == ["sample.py:3 remove: require_identifier после выбора договора"]
