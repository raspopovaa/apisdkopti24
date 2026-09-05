"""Проверка нетарифицируемых read-only методов на реальном API.

Скрипт читает настройки из `.env` рядом с этим файлом и не содержит секретов.
Он намеренно не вызывает методы, которые создают, изменяют или удаляют данные,
даже если такие методы помечены в контракте как нетарифицируемые.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from api_client_opti24 import (
    APIClient,
    ConnectionSettings,
    ContractSelectionError,
    EnvironmentCredentialsProvider,
)

ENV_FILE = Path(__file__).with_name(".env")
DICTIONARIES = (
    "CardStatus",
    "ContractStatus",
    "Goods",
    "ProductGroup",
    "ProductType",
    "Region",
    "Services",
)


class SmokeState:
    contract_id: str | None = None
    card_id: str | None = None
    group_id: str | None = None


def dump_preview(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json", by_alias=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return text if len(text) <= 1200 else f"{text[:1200]}...\n<обрезано>"


async def run_step(name: str, call: Callable[[], Awaitable[Any]]) -> Any | None:
    print(f"\n=== {name} ===")
    try:
        result = await call()
    except Exception as exc:  # noqa: BLE001 - smoke-script should continue.
        print(f"ERROR: {exc}")
        return None
    print("OK")
    print(dump_preview(result))
    return result


async def authorize(client: APIClient, state: SmokeState) -> None:
    try:
        auth = await client.auth.auth_user()
    except ContractSelectionError as exc:
        print("Доступно несколько договоров:")
        for contract_id, contract_number in exc.available_contracts:
            print(f"- {contract_id}: {contract_number}")
        state.contract_id = input("Введите ID договора для проверки: ").strip()
        auth = await client.auth.auth_user(contract_id=state.contract_id)
    else:
        if auth.data.contracts:
            state.contract_id = auth.data.contracts[0].id

    print(f"Авторизация OK, выбран договор: {state.contract_id}")


async def main() -> None:
    settings = ConnectionSettings.from_env(env_file=ENV_FILE)
    credentials = EnvironmentCredentialsProvider.from_env(env_file=ENV_FILE)
    state = SmokeState()

    async with APIClient(
        settings=settings,
        credentials_provider=credentials,
    ) as client:
        await authorize(client, state)
        try:
            await run_step("auth.get_info", lambda: client.auth.get_info())

            cards = await run_step(
                "cards.get_cards_v2",
                lambda: client.cards.get_cards_v2(page=1, onpage=5),
            )
            if cards is not None and cards.result:
                state.card_id = cards.result[0].id
                print(f"Автоматически выбран card_id: {state.card_id}")

            groups = await run_step(
                "card_groups.get_card_groups",
                lambda: client.card_groups.get_card_groups(),
            )
            if groups is not None and groups.data.result:
                state.group_id = groups.data.result[0].id
                print(f"Автоматически выбран group_id: {state.group_id}")

            await run_step("limits.get_limits", lambda: client.limits.get_limits())
            await run_step("reports.get_reports", lambda: client.reports.get_reports())
            await run_step(
                "reports.get_report_jobs",
                lambda: client.reports.get_report_jobs(),
            )
            await run_step(
                "reports.get_report_job_list_v1",
                lambda: client.reports.get_report_job_list_v1(),
            )
            await run_step(
                "dictionaries.get_azs_filters",
                lambda: client.dictionaries.get_azs_filters(),
            )
            await run_step(
                "dictionaries.get_azs_list_v1",
                lambda: client.dictionaries.get_azs_list_v1(page=1, onpage=3),
            )
            await run_step(
                "dictionaries.get_azs_list_v2",
                lambda: client.dictionaries.get_azs_list_v2(),
            )

            for dictionary_name in DICTIONARIES:
                await run_step(
                    f"dictionaries.get_dictionary({dictionary_name})",
                    lambda name=dictionary_name: client.dictionaries.get_dictionary(name=name),
                )

            if state.card_id is not None:
                await run_step(
                    "cards.get_card_detail",
                    lambda: client.cards.get_card_detail(card_id=state.card_id),
                )
                await run_step(
                    "cards.get_card_drivers",
                    lambda: client.cards.get_card_drivers(card_id=state.card_id),
                )

            if state.group_id is not None:
                await run_step(
                    "cards.get_cards_by_group",
                    lambda: client.cards.get_cards_by_group(group_id=state.group_id),
                )
        finally:
            await client.auth.logoff()


if __name__ == "__main__":
    asyncio.run(main())
