from __future__ import annotations

# ruff: noqa: E402, I001 -- src-layout bootstrap must run before SDK imports.

import argparse
import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if SRC_ROOT.is_dir():
    sys.path.insert(0, str(SRC_ROOT))

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.env import load_env_file


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Безопасная проверка обратимых API-мутаций")
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / ".env.integration")
    parser.add_argument(
        "--cleanup-only",
        action="store_true",
        help="Удалить только временные группы SDK-VALIDATION-* и завершить работу",
    )
    return parser.parse_args()


def failure(operation: str, exc: Exception) -> None:
    status = getattr(exc, "status_code", None)
    suffix = f", HTTP {status}" if isinstance(status, int) else ""
    print(f"FAIL {operation}: {type(exc).__name__}{suffix}")


async def remove_group_with_retries(
    client: APIClient, *, group_id: str, contract_id: str, attempts: int = 3
) -> None:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            await client.card_groups.remove_card_group(group_id=group_id, contract_id=contract_id)
            return
        except Exception as exc:
            last_error = exc
            if attempt + 1 < attempts:
                await asyncio.sleep(2**attempt)
    assert last_error is not None
    raise last_error


async def cleanup_validation_groups(client: APIClient, contract_id: str) -> bool:
    groups = await client.card_groups.get_card_groups(contract_id=contract_id)
    temporary = [
        item for item in groups.data.result or [] if item.name.startswith("SDK-VALIDATION-")
    ]
    for item in temporary:
        try:
            await remove_group_with_retries(client, group_id=item.id, contract_id=contract_id)
            print("OK   remove_card_group:recovery-cleanup")
        except Exception as exc:
            failure("remove_card_group:recovery-cleanup", exc)
            return False
    if not temporary:
        print("OK   cleanup:temporary-groups-absent")
    return True


async def check_group(client: APIClient, contract_id: str, marker: str) -> bool:
    group_id: str | None = None
    try:
        created = await client.card_groups.set_card_group(
            name=f"SDK-VALIDATION-{marker}", contract_id=contract_id
        )
        group_id = created.data.id
        print("OK   set_card_group:create")

        await client.card_groups.set_card_group(
            group_id=group_id,
            name=f"SDK-VALIDATION-{marker}-UPDATED",
            contract_id=contract_id,
        )
        print("OK   set_card_group:update")

        groups = await client.card_groups.get_card_groups(contract_id=contract_id)
        if not any(item.id == group_id for item in groups.data.result or []):
            raise RuntimeError("created group is absent from get_card_groups")
        print("OK   get_card_groups:created-visible")
        return True
    except Exception as exc:
        failure("card_group_flow", exc)
        return False
    finally:
        if group_id is not None:
            try:
                await remove_group_with_retries(client, group_id=group_id, contract_id=contract_id)
                print("OK   remove_card_group:cleanup")
            except Exception as exc:
                failure("remove_card_group:cleanup", exc)


async def check_template(client: APIClient, contract_id: str, marker: str) -> bool:
    template_id: str | None = None
    try:
        created = await client.templates.create_template(
            type_="Wallet",
            name=f"SDK-VALIDATION-{marker}",
            contract_id=contract_id,
        )
        template_id = created.data
        print("OK   create_template")

        await client.templates.update_template(
            template_id=template_id,
            type_="Wallet",
            name=f"SDK-VALIDATION-{marker}-UPDATED",
            contract_id=contract_id,
        )
        print("OK   update_template")

        templates = await client.templates.get_templates(contract_id=contract_id)
        if not any(item.id == template_id for item in templates.data.result or []):
            raise RuntimeError("created template is absent from get_templates")
        print("OK   get_templates:created-visible")
        return True
    except Exception as exc:
        failure("template_flow", exc)
        return False
    finally:
        if template_id is not None:
            try:
                await client.templates.delete_template(template_id=template_id)
                print("OK   delete_template:cleanup")
            except Exception as exc:
                failure("delete_template:cleanup", exc)


async def run(env_file: Path, *, cleanup_only: bool = False) -> int:
    env_file = env_file.expanduser().resolve()
    load_env_file(env_file, override=True)
    contract_id = os.getenv("TEST_CONTRACT_ID", "").strip()
    if not env_file.is_file() or not contract_id:
        print("Нужны существующий .env.integration и TEST_CONTRACT_ID", file=sys.stderr)
        return 2

    settings = ConnectionSettings.from_env(load_dotenv=False)
    credentials = EnvironmentCredentialsProvider.from_env(load_dotenv=False)
    marker = uuid4().hex[:10]

    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        await client.auth.auth_user(contract_id=contract_id)
        if cleanup_only:
            cleanup_ok = await cleanup_validation_groups(client, contract_id)
            return 0 if cleanup_ok else 1
        group_ok = await check_group(client, contract_id, marker)
        template_ok = await check_template(client, contract_id, marker)
        try:
            await client.auth.logoff()
        except Exception as exc:
            failure("logoff", exc)
            return 1
    return 0 if group_ok and template_ok else 1


def main() -> None:
    args = arguments()
    raise SystemExit(asyncio.run(run(args.env_file, cleanup_only=args.cleanup_only)))


if __name__ == "__main__":
    main()
