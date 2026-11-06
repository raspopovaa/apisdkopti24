"""Сквозной пример: от приглашения водителя до платёжного QR-кода.

Шаги (каждый запускается отдельной командой, изменения только после ввода «да»):

  template     шаблон виртуальной карты: лимит на топливо и разрешение топлива
  invite       приглашение водителя по телефону с этим шаблоном
  find-user    найти user_id водителя после регистрации по ссылке из SMS
  card         выпустить водителю виртуальную карту по шаблону
  mpc          выпустить мобильный профиль карты (МПК): init_mpc + код из SMS
  qr           получить платёжную строку и показать её как QR в терминале
  cleanup      удалить МПК, заблокировать карту, удалить водителя и шаблон

Пример запуска (QR в терминале рисует пакет qrcode):

  uv run --with apisdkopti24 --with qrcode python examples/driver_qr_walkthrough.py \\
      --env-file .env.test --contract 1-CONTRACT template --product-type 1-XXXXXXX

Все ID ниже условные. Номера телефонов, PIN, SMS-коды, ссылки приглашений и сама
платёжная строка в журнал не выводятся: это персональные и платёжные данные.
"""

from __future__ import annotations

# ruff: noqa: E402, I001 -- путь к src настраивается до импортов SDK.

import argparse
import asyncio
import getpass
import sys
import time
from pathlib import Path

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
from apisdkopti24.errors import (
    AccessDeniedError,
    APIError,
    DuplicateLoginError,
    InviteNotReadyError,
    NotFoundError,
    ServerError,
)

# ---------------------------------------------------------------------------
# Общие помощники
# ---------------------------------------------------------------------------


def confirm(action: str) -> None:
    """Спросить подтверждение и остановить пример при любом ответе, кроме «да».

    Каждое изменение в API необратимо или тарифицируется, поэтому пример ничего
    не меняет без явного согласия человека. Ответ «lf» — это «да» в английской
    раскладке; его не принимаем, но подсказываем.
    """
    answer = input(f"{action}. Выполнить? Введите «да»: ").strip().casefold()
    if answer == "да":
        return
    if answer == "lf":
        print("Похоже, включена английская раскладка: «lf» — это «да».")
    print("Отменено, ничего не отправлено.")
    raise SystemExit(2)


def explain(exc: APIError) -> str:
    """Короткое описание ошибки API: класс, сообщение, причина и можно ли повторять."""
    reason = exc.context.reason or "нет"
    return f"{type(exc).__name__}: {exc} (reason={reason}, retryable={exc.context.retryable})"


# ---------------------------------------------------------------------------
# Шаг 1. Шаблон виртуальной карты
# ---------------------------------------------------------------------------


async def create_template(
    client: APIClient, *, name: str, product_type: str, liters: int, period_type: int
) -> str:
    """Создать шаблон ВК с лимитом на тип продукта и разрешением этого типа.

    Параметры:
        name: название шаблона, не длиннее 30 символов.
        product_type: ID типа продукта «Топливо» без группы, тогда лимит и
            разрешение действуют на все виды топлива. ID разный в разных средах:
            возьмите его из лимитов уже созданных шаблонов (get_template_limits,
            поле productType) или из справочников договора. Чужой ID даёт
            400 «Выбранное значение некорректно».
        liters: размер лимита в литрах (amount.unit = "LIT").
        period_type: период лимита (time.type): 2 — разовый, 3 — сутки,
            4 — неделя, 5 — месяц; time.number — сколько таких периодов.

    Возвращает ID шаблона. Шаблон пригодится приглашению и выпуску карты.
    """
    confirm(f"Создать шаблон «{name}»: {liters} л, период {period_type}, тип {product_type}")

    # type_="Limit" — карта с лимитами; "Wallet" — карта-кошелёк.
    created = await client.templates.create_template(type_="Limit", name=name)
    template_id = created.data
    print("Шаблон создан:", template_id)

    # Лимит на объём. Без группы продукта (product_group) лимит общий на тип.
    limit = await client.templates.create_template_limit(
        template_id=template_id,
        payload={
            "product_type": product_type,
            "amount": {"unit": "LIT", "value": liters},
            "time": {"type": period_type, "number": 1},
        },
    )
    print("Лимит шаблона:", limit.data)

    # Товарный ограничитель: restriction_type 1 — разрешить, 2 — запретить.
    restriction = await client.templates.create_template_restriction(
        template_id=template_id,
        payload={"product_type": product_type, "restriction_type": 1},
    )
    print("Разрешение в шаблоне:", restriction.data)
    return template_id


# ---------------------------------------------------------------------------
# Шаг 2. Приглашение водителя
# ---------------------------------------------------------------------------


async def invite_driver(client: APIClient, *, mobile: str, template_id: str) -> None:
    """Пригласить водителя по номеру телефона с шаблоном ВК договора.

    Параметры:
        mobile: телефон в формате 7XXXXXXXXXX. Он станет логином водителя.
        template_id: шаблон ВК из шага 1.

    Нюансы:
        - Приглашение без карт и без шаблона API не отправляет:
          InviteNotReadyError (500 «Приглашение не готово к отправке»).
        - Если телефон уже чей-то логин в системе оператора (даже не на вашем
          договоре), API ответит DuplicateLoginError. get_users такого
          пользователя не покажет: он видит только пользователей договора.
        - with_send=True отправляет SMS со ссылкой. Ссылка действует 3 дня.
          Пересылать её в чаты и журналы не нужно: это вход в учётную запись.
        - Приглашение с шаблоном само карту не выпускает (шаг 4).
    """
    contract_id = client.contract_id
    if contract_id is None:
        raise SystemExit("Нет выбранного договора: укажите --contract")
    confirm(f"Пригласить водителя …{mobile[-4:]} с шаблоном {template_id}, отправить SMS")
    try:
        response = await client.invites.create_invite(
            data={
                "role": "Driver",
                "mobile": mobile,
                "cards": [],
                "contracts": [{"id": contract_id, "template_id": template_id}],
            },
            with_send=True,
        )
    except DuplicateLoginError:
        print("Этот телефон уже занят в системе оператора: возьмите другой номер.")
        raise
    except InviteNotReadyError:
        print("Приглашению нужна карта или шаблон ВК: проверьте template_id.")
        raise
    print("Приглашение создано:", response.data.id)
    print("Водитель открывает ссылку из SMS на телефоне и завершает регистрацию.")


# ---------------------------------------------------------------------------
# Шаг 3. user_id водителя
# ---------------------------------------------------------------------------


async def find_driver(client: APIClient, *, mobile_suffix: str) -> None:
    """Показать водителей договора, чей телефон оканчивается на mobile_suffix.

    После регистрации по ссылке водитель появляется в get_users с ролью Driver и
    договором, у которого template_id — ваш шаблон. user_id нужен для выпуска
    карты и МПК. Телефон выводится только последними четырьмя цифрами.
    """
    response = await client.users.get_users()
    users = response.data.result if response.data and response.data.result else []
    for user in users:
        phone = user.mobile_phone or user.login or ""
        if user.role.id != "Driver" or not phone.endswith(mobile_suffix):
            continue
        templates = {contract.sid: contract.template_id for contract in user.contracts}
        print(f"user_id {user.id}, телефон …{phone[-4:]}, договоры и шаблоны: {templates}")
        for card in user.cards:
            print(f"  карта {card.sid}: тип {card.product}, статус {card.status}, МПК {card.mpc}")


# ---------------------------------------------------------------------------
# Шаг 4. Виртуальная карта
# ---------------------------------------------------------------------------


async def release_card(client: APIClient, *, user_id: str, template_id: str) -> None:
    """Выпустить водителю виртуальную карту по шаблону.

    Параметры:
        user_id: водитель из шага 3; карта сразу будет привязана к нему.
        template_id: шаблон ВК; задайте его или type_ ("limit"/"wallet"), не оба.

    Нюансы:
        - Метод тарифицируется и выпускает настоящую карту. SDK его не повторяет:
          при сетевом сбое сначала проверьте карты водителя (шаг 3).
        - У виртуальной карты может быть только один водитель. Второго API не
          добавит: 403 «Добавление второго водителя к Виртуальной карте
          запрещено». Чтобы передать карту, отвяжите её (users.detach_card) и
          привяжите к другому пользователю (users.attach_card).
    """
    confirm(f"Выпустить виртуальную карту по шаблону {template_id} водителю {user_id}")
    response = await client.virtual_cards.release_virtual_card(
        template_id=template_id, user_id=user_id
    )
    card = response.data
    print(f"Карта {card.id}: статус {card.status}, продукт {card.product}")


# ---------------------------------------------------------------------------
# Шаг 5. Мобильный профиль карты (МПК)
# ---------------------------------------------------------------------------


async def issue_mpc(client: APIClient, *, card_id: str, user_id: str) -> None:
    """Выпустить МПК: init_mpc отправляет SMS водителю, confirm_mpc принимает код.

    Параметры init_mpc (SDK проверяет их до сетевого запроса):
        pin: 4–8 цифр. PIN нужен для каждой генерации QR; не храните его.
        device_id: 1–255 символов, стабильный ID устройства водителя.
        device_name: 11–17 символов, понятное имя устройства.

    Нюансы:
        - Карта должна быть привязана к user_id, иначе
          403 «Данная карта не привязана к пользователю».
        - На карте только один МПК. Существующий удалите через delete_mpc.
        - МПК выпускается на телефон пользователя: у него должен быть включён
          мобильный доступ (access.mobile в get_users). Без него init_mpc может
          ответить 500 «технические проблемы».
        - Неверный SMS-код блокирует выпуск: не перебирайте коды. Блокировку
          снимает reset_mpc.
        - Методы МПК есть только на тестовом и рабочем API, на DEMO их нет.
    """
    device_id = input("device_id (1–255 символов): ").strip()
    device_name = input("device_name (11–17 символов): ").strip()
    while not 11 <= len(device_name) <= 17:
        device_name = input(f"Нужно 11–17 символов, сейчас {len(device_name)}: ").strip()
    pin = getpass.getpass("PIN МПК (4–8 цифр, не показывается): ")

    confirm(f"Выпустить МПК на карту {card_id} пользователю {user_id}, отправить SMS")
    try:
        started = await client.virtual_cards.init_mpc(
            card_id=card_id,
            user_id=user_id,
            pin=pin,
            device_id=device_id,
            device_name=device_name,
        )
    except AccessDeniedError:
        print("Карта не привязана к пользователю: проверьте шаг 3.")
        raise
    print("SMS отправлено" if started.data else "Сервер не подтвердил отправку SMS")

    code = getpass.getpass("Код из SMS (один раз; неверный код блокирует выпуск): ")
    confirm("Отправить код в confirm_mpc")
    confirmed = await client.virtual_cards.confirm_mpc(card_id=card_id, code=code)
    print("МПК выпущен" if confirmed.data else "Сервер не подтвердил МПК")


# ---------------------------------------------------------------------------
# Шаг 6. Платёжный QR-код
# ---------------------------------------------------------------------------


async def show_qr(client: APIClient, *, card_id: str) -> None:
    """Получить платёжную строку и показать её как QR в терминале.

    Нюансы:
        - code — строка BER-TLV. Передайте её в генератор QR без изменений.
        - end_date — Unix-время окончания в секундах. Описание API обещает до
          10 минут, но строка может жить заметно меньше: проверяйте end_date
          перед показом и не кэшируйте строку.
        - transaction_count растёт при каждой генерации, даже без оплаты;
          tries — предел строк до перевыпуска МПК.
        - 404 «На карте нет МПК» — профиль не выпущен или удалён (шаг 5).
        - 5xx на генерации — результат неизвестен. Сначала посмотрите
          get_mpc_qr_list: если transaction_count не вырос, строка не выдана.
          Повтор генерации не списывает деньги, а только расходует tries.
        - Оплата проходит на кассе АЗС, которая принимает QR. SDK не платит сам.
    """
    import qrcode  # type: ignore[import-untyped]  # pip install qrcode

    pin = getpass.getpass("PIN МПК (не показывается): ")
    confirm(f"Получить платёжную строку по карте {card_id}")
    try:
        payment = await client.virtual_cards.generate_payment_qr(card_id=card_id, pin=pin)
    except NotFoundError:
        print("На карте нет МПК: выпустите его (шаг mpc).")
        raise
    except ServerError:
        print("Ответ не получен. Проверьте счётчик строк, прежде чем повторять:")
        for profile in (await client.virtual_cards.get_mpc_qr_list()).result:
            if profile.card_id == card_id:
                print(f"  выдано строк {profile.transaction_count} из {profile.tries}")
        raise

    seconds_left = payment.end_date - int(time.time())
    if seconds_left <= 0:
        raise SystemExit("Строка уже недействительна: запросите новую.")
    image = qrcode.QRCode(border=1)
    image.add_data(payment.code)
    image.print_ascii(invert=True)
    print(
        f"Строка действует ещё {seconds_left} с, "
        f"выдано строк {payment.data.transaction_count} из {payment.data.tries}."
    )
    input("Покажите QR на кассе, затем нажмите Enter, чтобы очистить экран.")
    print("\033[2J\033[H", end="")


# ---------------------------------------------------------------------------
# Шаг 7. Уборка после теста
# ---------------------------------------------------------------------------


async def cleanup(client: APIClient, *, card_id: str, user_id: str, template_id: str) -> None:
    """Удалить МПК, заблокировать карту, удалить водителя и шаблон.

    Порядок важен: сначала МПК (он привязан к карте и пользователю), затем
    блокировка карты, затем пользователь и шаблон. Удаление необратимо.
    """
    confirm(f"Удалить МПК карты {card_id}")
    print("delete_mpc:", (await client.virtual_cards.delete_mpc(card_id=card_id)).data)
    confirm(f"Заблокировать карту {card_id}")
    print("block_card:", (await client.cards.block_card(card_ids=[card_id])).data)
    confirm(f"Удалить пользователя {user_id}")
    print("delete_user:", (await client.users.delete_user(user_id=user_id)).data)
    confirm(f"Удалить шаблон {template_id}")
    print(
        "delete_template:", (await client.templates.delete_template(template_id=template_id)).data
    )


# ---------------------------------------------------------------------------
# Запуск
# ---------------------------------------------------------------------------


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--env-file", type=Path, required=True, help="API_BASE_URL, ключ и вход")
    parser.add_argument("--contract", help="ID договора, если их несколько")
    parser.add_argument(
        "step", choices=["template", "invite", "find-user", "card", "mpc", "qr", "cleanup"]
    )
    parser.add_argument("--template", help="ID шаблона ВК (шаги invite, card, cleanup)")
    parser.add_argument("--product-type", help="ID типа продукта «Топливо» (шаг template)")
    parser.add_argument("--liters", type=int, default=500, help="Лимит в литрах (шаг template)")
    parser.add_argument("--period-type", type=int, default=5, help="Период лимита: 5 — месяц")
    parser.add_argument("--name", default="Водитель QR", help="Название шаблона, до 30 символов")
    parser.add_argument("--mobile", help="Телефон водителя 7XXXXXXXXXX (шаг invite)")
    parser.add_argument("--suffix", help="Последние цифры телефона (шаг find-user)")
    parser.add_argument("--user", help="user_id водителя")
    parser.add_argument("--card", help="ID виртуальной карты")
    return parser.parse_args()


def require(value: str | None, flag: str) -> str:
    if not value:
        raise SystemExit(f"Для этого шага нужен {flag}")
    return value


async def run(args: argparse.Namespace) -> None:
    env_file = args.env_file.expanduser()
    settings = ConnectionSettings.from_env(env_file=env_file)
    credentials = EnvironmentCredentialsProvider.from_env(env_file=env_file)
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        # Вход и выбор договора: все шаги работают с этим договором. При
        # нескольких договорах без --contract API не выберет договор сам.
        try:
            await client.auth.auth_user(contract_id=args.contract)
        except ContractSelectionError as exc:
            for contract_id, number in exc.available_contracts:
                print(f"  {contract_id}  {number}")
            raise SystemExit("Укажите договор: --contract 1-…") from exc
        try:
            if args.step == "template":
                await create_template(
                    client,
                    name=args.name,
                    product_type=require(args.product_type, "--product-type"),
                    liters=args.liters,
                    period_type=args.period_type,
                )
            elif args.step == "invite":
                await invite_driver(
                    client,
                    mobile=require(args.mobile, "--mobile"),
                    template_id=require(args.template, "--template"),
                )
            elif args.step == "find-user":
                await find_driver(client, mobile_suffix=require(args.suffix, "--suffix"))
            elif args.step == "card":
                await release_card(
                    client,
                    user_id=require(args.user, "--user"),
                    template_id=require(args.template, "--template"),
                )
            elif args.step == "mpc":
                await issue_mpc(
                    client,
                    card_id=require(args.card, "--card"),
                    user_id=require(args.user, "--user"),
                )
            elif args.step == "qr":
                await show_qr(client, card_id=require(args.card, "--card"))
            else:
                await cleanup(
                    client,
                    card_id=require(args.card, "--card"),
                    user_id=require(args.user, "--user"),
                    template_id=require(args.template, "--template"),
                )
        except APIError as exc:
            # Не повторяйте изменение вслепую: сначала проверьте состояние чтением.
            print("Ошибка API:", explain(exc))
            raise SystemExit(1) from exc
        finally:
            await client.auth.logoff()


if __name__ == "__main__":
    asyncio.run(run(arguments()))
