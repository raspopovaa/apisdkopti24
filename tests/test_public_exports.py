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
