from __future__ import annotations

# ruff: noqa: E402, I001 -- src-layout bootstrap must run before SDK imports.

import argparse
import asyncio
import os
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, TypeVar

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if SRC_ROOT.is_dir():
    sys.path.insert(0, str(SRC_ROOT))

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    ContractSelectionError,
    EnvironmentCredentialsProvider,
)
from apisdkopti24.env import load_env_file
from apisdkopti24.modeling import ValidationError

ResultT = TypeVar("ResultT")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Найти безопасные тестовые ID для .env.integration"
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=PROJECT_ROOT / ".env.discovery",
        help="Файл с API_BASE_URL, API_KEY, API_LOGIN и API_PASSWORD",
    )
    parser.add_argument(
        "--contract-id",
        help="Договор для выборки; обязателен, если учётной записи доступно несколько",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Проверить доступ без вывода идентификаторов",
    )
    return parser.parse_args()


async def optional_call(
    label: str,
    request: Callable[[], Awaitable[ResultT]],
) -> ResultT | None:
    try:
        return await request()
    except ValidationError as exc:
        print(f"# {label}: ответ не прошёл Pydantic-валидацию", file=sys.stderr)
        for error in exc.errors(include_input=False, include_url=False):
            location = ".".join(str(part) for part in error["loc"])
            print(
                f"#   {location}: {error['type']} — {error['msg']}",
                file=sys.stderr,
            )
        return None
    except Exception as exc:  # diagnostic boundary: continue discovering other IDs
        print(f"# {label}: недоступно ({type(exc).__name__})", file=sys.stderr)
        return None


def first_id(response: Any) -> str | None:
    if response is None:
        return None
    result = getattr(getattr(response, "data", None), "result", None)
    if not result:
        return None
    value = getattr(result[0], "id", None)
    return str(value) if value is not None else None


def line(name: str, value: str | None, explanation: str) -> None:
    print(f"{name}={value}" if value else f"{name}=  # {explanation}")


async def discover(
    env_file: Path,
    preferred_contract_id: str | None,
    *,
    check_only: bool = False,
) -> int:
    env_file = env_file.expanduser().resolve()
    if not env_file.is_file():
        print(f"Файл не найден: {env_file}", file=sys.stderr)
        return 2

    load_env_file(env_file, override=True)
    required_names = ("API_BASE_URL", "API_KEY", "API_LOGIN", "API_PASSWORD")
    missing = [name for name in required_names if not os.getenv(name, "").strip()]
    if missing:
        print(
            f"В файле {env_file} не заполнены переменные: {', '.join(missing)}",
            file=sys.stderr,
        )
        print("Добавьте строки NAME=value без символов < и >.", file=sys.stderr)
        return 2

    if preferred_contract_id is None:
        preferred_contract_id = os.getenv("TEST_CONTRACT_ID") or None

    settings = ConnectionSettings.from_env(load_dotenv=False)
    credentials = EnvironmentCredentialsProvider.from_env(load_dotenv=False)

    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        try:
            auth = await client.auth.auth_user(contract_id=preferred_contract_id)
        except ContractSelectionError as exc:
            print(
                "Доступно несколько договоров. Подождите не менее 5 секунд и "
                "повторите команду с одним из значений:"
            )
            for contract_id, contract_number in exc.available_contracts:
                print(
                    f"  python examples/discover_integration_ids.py "
                    f"--contract-id {contract_id}  # {contract_number}"
                )
            return 2

        selected_contract_id = client.contract_id
        cards = await optional_call(
            "карты", lambda: client.cards.get_cards_v2(contract_id=selected_contract_id, onpage=10)
        )
        groups = await optional_call(
            "группы карт",
            lambda: client.card_groups.get_card_groups(contract_id=selected_contract_id),
        )
        users = await optional_call(
            "пользователи",
            lambda: client.users.get_users(contract_id=selected_contract_id, on_page=10),
        )
        templates = await optional_call(
            "шаблоны",
            lambda: client.templates.get_templates(contract_id=selected_contract_id),
        )
        reports = await optional_call("отчёты", client.reports.get_reports)

        contract = next(
            (item for item in auth.data.contracts if item.id == selected_contract_id),
            auth.data.contracts[0] if auth.data.contracts else None,
        )
        card_id = first_id(cards)

        if check_only:
            print("Read-only проверка завершена.")
            print(f"Договоры: {len(auth.data.contracts)}")
            print(f"Карты: {getattr(getattr(cards, 'data', None), 'total_count', 0)}")
            print(f"Группы: {getattr(getattr(groups, 'data', None), 'total_count', 0)}")
            print(f"Пользователи: {getattr(users, 'total_count', 0)}")
            print(f"Шаблоны: {getattr(getattr(templates, 'data', None), 'total_count', 0)}")
            print(f"Отчёты: {getattr(getattr(reports, 'data', None), 'total_count', 0)}")
        else:
            print("# Скопируйте блок в .env.integration и заполните оставшиеся строки.")
            print("# API_KEY, API_LOGIN, API_PASSWORD и session_id намеренно не выводятся.")
            print(f"API_BASE_URL={settings.base_url}")
            print("API_KEY=  # скопируйте из .env.discovery")
            print("API_LOGIN=  # скопируйте из .env.discovery")
            print("API_PASSWORD=  # скопируйте из .env.discovery")
            line("TEST_CONTRACT_ID", selected_contract_id, "нет доступного договора")
            line("TEST_CONTRACT_NUMBER", contract.number if contract else None, "не найден")
            line("TEST_CARD_ID", card_id, "на договоре нет карты")
            line("TEST_GROUP_ID", first_id(groups), "на договоре нет группы карт")
            line("TEST_USER_ID", first_id(users) or auth.data.user_id, "пользователь не найден")
            line("TEST_TEMPLATE_ID", first_id(templates), "сначала создайте тестовый шаблон")
            line("TEST_REPORT_ID", first_id(reports), "нет доступного отчёта")
            line(
                "TEST_MPC_CARD_ID",
                card_id if contract and contract.mpc else None,
                "нужна MPC-карта",
            )
            print("TEST_POI_ID=  # выберите АЗС после проверки get_azs_list_v2")
            print("TEST_INVITE_ID=  # создаётся отдельным разрешённым mutation-сценарием")
            print("TEST_REPORT_JOB_ID=  # появляется после заказа тестового отчёта")
            print("TEST_TRANSACTION_ID=  # выберите из ответа get_transactions_v2")

        try:
            await client.auth.logoff()
        except Exception as exc:
            print(f"# logoff завершился с {type(exc).__name__}", file=sys.stderr)
    return 0


def main() -> None:
    args = arguments()
    raise SystemExit(
        asyncio.run(discover(args.env_file, args.contract_id, check_only=args.check_only))
    )


if __name__ == "__main__":
    main()
