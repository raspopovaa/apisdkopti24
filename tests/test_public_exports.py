from __future__ import annotations

import ast
import importlib
from pathlib import Path

from mypy import api as mypy_api

import apisdkopti24

PACKAGE_INIT = Path(apisdkopti24.__file__)


def _type_checking_imports() -> dict[str, str]:
    tree = ast.parse(PACKAGE_INIT.read_text(encoding="utf-8"))
    block = next(
        node
        for node in tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "TYPE_CHECKING"
    )
    imported: dict[str, str] = {}
    for statement in block.body:
        assert isinstance(statement, ast.ImportFrom)
        for alias in statement.names:
            assert alias.asname == alias.name, "реэкспорт требует формы `X as X`"
            imported[alias.name] = "." * statement.level + (statement.module or "")
    return imported


def test_type_checking_block_lists_every_lazy_export() -> None:
    lazy_exports = set(apisdkopti24._EXPORTS)

    assert set(_type_checking_imports()) == lazy_exports
    assert set(apisdkopti24.__all__) == lazy_exports | {"APIClient", "__version__"}


def test_type_checking_imports_resolve_to_runtime_objects() -> None:
    # Сравниваем с источником из _EXPORTS, а не с кэшем пакета: другие тесты
    # перезагружают модули, и закэшированный объект может быть от прежней загрузки.
    for name, module_name in _type_checking_imports().items():
        typed_module = importlib.import_module(module_name, apisdkopti24.__name__)
        runtime_module_name, runtime_attribute = apisdkopti24._EXPORTS[name]
        runtime_module = importlib.import_module(runtime_module_name, apisdkopti24.__name__)

        assert getattr(typed_module, name) is getattr(runtime_module, runtime_attribute), name


def test_type_checker_sees_concrete_types_of_lazy_exports(tmp_path: Path) -> None:
    user_code = tmp_path / "user_code.py"
    user_code.write_text(
        "from apisdkopti24 import ConnectionSettings, RequestValidationError\n"
        "ConnectionSettings(base_url=123, no_such_option=True)\n"
        "error: RequestValidationError = 'не исключение'\n",
        encoding="utf-8",
    )

    # Пустой конфиг: проверяем пакет так, как его видит проект пользователя.
    empty_config = tmp_path / "mypy.ini"
    empty_config.write_text("[mypy]\n", encoding="utf-8")

    stdout, _, exit_status = mypy_api.run(
        [
            "--config-file",
            str(empty_config),
            "--no-incremental",
            "--follow-imports=silent",
            "--no-error-summary",
            str(user_code),
        ]
    )

    assert exit_status == 1, stdout
    assert 'Unexpected keyword argument "no_such_option"' in stdout
    assert 'Argument "base_url" to "ConnectionSettings"' in stdout
    assert "RequestValidationError" in stdout and "incompatible types" in stdout.lower()


def test_type_checker_accepts_optional_request_fields_and_model_lists(tmp_path: Path) -> None:
    # Field(None, ...) mypy не считает значением по умолчанию: поле выглядело
    # обязательным, а list[X | Mapping] отвергал list[X] из-за инвариантности list.
    user_code = tmp_path / "user_code.py"
    user_code.write_text(
        "from apisdkopti24.models.card_group import CardGroupAssignmentRequest\n"
        "from apisdkopti24.models.limits import LimitTermTimeRequest\n"
        "from apisdkopti24.models.region_limits import RegionLimitRequestItem\n"
        "from apisdkopti24.models.restrictions import RestrictionRequestItem\n"
        "from apisdkopti24.models.users import UserAttachContractRequest\n"
        "from apisdkopti24.services.card_group import CardGroupsService\n"
        "from apisdkopti24.services.users import UsersService\n"
        "\n"
        "async def use(groups: CardGroupsService, users: UsersService) -> None:\n"
        "    RestrictionRequestItem(card_id='card-1', productType='fuel', restriction_type=1)\n"
        "    LimitTermTimeRequest(from_='08:00', to='20:00')\n"
        "    RegionLimitRequestItem(card_id='card-1', country='RU', limit_type=1)\n"
        "    cards = [CardGroupAssignmentRequest(id='card-1', type='Attach')]\n"
        "    await groups.set_cards_to_group(group_id='group-1', cards_list=cards)\n"
        "    contracts = [UserAttachContractRequest(sid='c-1', template_id='t-1')]\n"
        "    await users.attach_contracts(user_id='user-1', contracts=contracts)\n",
        encoding="utf-8",
    )
    empty_config = tmp_path / "mypy.ini"
    empty_config.write_text("[mypy]\n", encoding="utf-8")

    stdout, _, exit_status = mypy_api.run(
        ["--config-file", str(empty_config), "--no-incremental", str(user_code)]
    )

    assert exit_status == 0, stdout


def test_field_defaults_are_passed_by_keyword() -> None:
    # Только default=... распознают анализаторы типов (dataclass_transform).
    positional_defaults = []
    for path in sorted(PACKAGE_INIT.parent.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "Field"
                and node.args
                and not (isinstance(node.args[0], ast.Constant) and node.args[0].value is ...)
            ):
                positional_defaults.append(f"{path.name}:{node.lineno}")

    assert positional_defaults == []
