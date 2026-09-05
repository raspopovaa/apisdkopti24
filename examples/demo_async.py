import asyncio
import os
from pathlib import Path

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is required. Copy .env.example to .env and fill it."
        )
    return value


async def main() -> None:
    settings = ConnectionSettings.from_env(env_file=ENV_FILE)
    credentials = EnvironmentCredentialsProvider.from_env(env_file=ENV_FILE)
    contract_id = require_env("API_CONTRACT_ID")

    async with APIClient(
        settings=settings,
        credentials_provider=credentials,
    ) as client:
        auth = await client.auth.auth_user(contract_id=contract_id)
        print("Авторизация выполнена")
        print("Пользователь:", auth.data.user_id)
        print("Выбранный договор:", client.contract_id)

        try:
            info = await client.auth.get_info()
            cards = await client.cards.get_cards_v2(
                contract_id=contract_id,
                page=1,
                onpage=5,
            )
            reports = await client.reports.get_reports()
            users = await client.users.get_users(page=1, on_page=5)

            print("Период статистики:", info.data.from_, "—", info.data.to)
            print("Карт найдено:", cards.total_count)
            print("Отчётов доступно:", reports.total_count)
            print("Пользователей найдено:", users.data.total_count)
        finally:
            await client.auth.logoff()
            print("Сессия завершена")


if __name__ == "__main__":
    asyncio.run(main())
