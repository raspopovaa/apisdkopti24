"""Проверка 89 методов SDK с автоматической подстановкой параметров.

Использует сценарий ``check_all_89_real_api.py``, но не спрашивает параметры, для которых
значение уже известно: введённые в прошлом прогоне (``--from-responses``), найденные в
ответах текущего прогона ID и значения по умолчанию. Читающие методы выполняются сразу.
Методы, которые меняют данные или тарифицируются, по умолчанию требуют подтверждения
(``--mutations ask``) или пропускаются (``--mutations skip``).

Пример:

    python examples/check_all_89_auto.py --env-file .env \\
        --from-responses responses-20260925-223926.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import sys
from collections.abc import Awaitable
from pathlib import Path
from types import ModuleType
from typing import Any

CHECKER_PATH = Path(__file__).with_name("check_all_89_real_api.py")


def load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_all_89_real_api", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Не удалось загрузить {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_auto_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Разобрать параметры автоматического режима; остальные передаются основному сценарию."""
    parser = argparse.ArgumentParser(
        description="Проверка 89 методов SDK с автоматической подстановкой параметров",
        epilog=(
            "Остальные параметры (--env-file, --from-responses, --responses-file, "
            "--no-save-responses) передаются check_all_89_real_api.py."
        ),
    )
    parser.add_argument(
        "--mutations",
        choices=("ask", "skip"),
        default="ask",
        help="Методы, изменяющие данные: ask — спрашивать подтверждение, skip — пропускать",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Не спрашивать обязательные параметры без известного значения: метод пропускается",
    )
    return parser.parse_known_args(argv)


def install_auto_answers(checker: ModuleType, *, mutations: str, no_prompt: bool) -> None:
    """Заменить интерактивный ввод основного сценария автоматической подстановкой."""
    manual_ask_value = checker.ask_value
    manual_prompt_before_call = checker.prompt_before_call
    color, dim = checker.color, checker.Color.DIM

    def remember_input(name: str, value: Any) -> None:
        checker.CURRENT_INPUTS[checker.extract_input_key(name)] = value

    def ask_value(
        name: str,
        *,
        default: str | None = None,
        required: bool = True,
        example: str | None = None,
    ) -> str | None:
        if default is None:
            previous = checker.previous_input(name)
            default = None if previous is None else str(previous)
        if default:
            print(color(f"{name}: {default} (подставлено автоматически)", dim))
            remember_input(name, default)
            return default
        if not required:
            print(color(f"{name}: не задан (необязательный параметр)", dim))
            return None
        if no_prompt:
            raise checker.SkipMethod(f"Нет известного значения для {name}")
        return manual_ask_value(name, default=default, required=required, example=example)

    def ask_bool(name: str, *, default: bool, example: str | None = None) -> bool:
        del example
        previous = checker.previous_input(name)
        value = previous if isinstance(previous, bool) else default
        print(color(f"{name}: {'да' if value else 'нет'} (подставлено автоматически)", dim))
        remember_input(name, value)
        return value

    def prompt_before_call(*, mutating: bool, awaitable: Awaitable[Any] | None = None) -> None:
        if not mutating:
            print(color("Читающий метод: выполняется автоматически", dim))
            return
        if mutations == "skip":
            if awaitable is not None:
                checker.close_if_pending(awaitable)
            raise checker.SkipMethod("Изменяющие методы пропускаются (--mutations skip)")
        manual_prompt_before_call(mutating=mutating, awaitable=awaitable)

    checker.ask_value = ask_value
    checker.ask_bool = ask_bool
    checker.prompt_before_call = prompt_before_call


def main() -> None:
    args, checker_argv = parse_auto_args(sys.argv[1:])
    checker = load_checker()
    install_auto_answers(checker, mutations=args.mutations, no_prompt=args.no_prompt)
    sys.argv = [str(CHECKER_PATH), *checker_argv]
    asyncio.run(checker.main())


if __name__ == "__main__":
    main()
