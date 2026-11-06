---
description: Сквозной пример apisdkopti24 от приглашения водителя до платёжного QR-кода: шаги, параметры, ограничения и ошибки.
---

# От приглашения водителя до QR-кода

Пример проходит весь путь: шаблон виртуальной карты, приглашение водителя,
выпуск виртуальной карты, мобильный профиль карты (МПК) и платёжная строка для
QR-кода. Готовый скрипт с комментариями к каждому шагу:
[`examples/driver_qr_walkthrough.py`](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/driver_qr_walkthrough.py).

В примере водитель Иванов Иван с телефоном `79990000000`. Все ID условные.

```text
шаблон ВК ──► приглашение ──► регистрация по SMS ──► виртуальная карта
                                                          │
                     QR на кассе ◄── платёжная строка ◄── МПК (SMS-код)
```

## Перед началом

- Методы МПК и QR есть на тестовом и рабочем API, на DEMO их нет.
- Нужен договор, на котором учётной записи API разрешено приглашать
  пользователей и выпускать виртуальные карты.
- Водителю нужен телефон, который ещё не служит логином в системе оператора.
- Выпуск виртуальной карты тарифицируется и создаёт настоящую карту. Остальные
  изменения тоже настоящие: в примере каждое подтверждается вводом «да».
- PIN, SMS-код, ссылку приглашения и платёжную строку не записывайте в журналы
  и не пересылайте в чаты.

```bash
uv run --with apisdkopti24 --with qrcode python examples/driver_qr_walkthrough.py \
    --env-file .env.test --contract 1-CONTRACT template --product-type 1-XXXXXXX
```

## Вход и договор

Все шаги работают с одним договором. Если у учётной записи их несколько,
`auth_user()` без договора бросает `ContractSelectionError` со списком
`available_contracts`. Выберите договор явно:

```python
await client.auth.auth_user(contract_id="1-CONTRACT")
# или по номеру договора
await client.auth.auth_user(contract_number="ДГ0000000")
```

В примере договор передаётся флагом `--contract`. Без него при нескольких
договорах скрипт остановится на входе.

## Что тарифицируется и где работает

| Метод | Тарифицируется | DEMO | Повтор SDK |
| --- | --- | --- | --- |
| `templates.create_template`, `create_template_limit`, `create_template_restriction` | да | есть | нет |
| `templates.get_template_limits`, `users.get_users` | нет | есть | безопасный |
| `invites.create_invite(with_send=True)` | да | нет | нет |
| `virtual_cards.release_virtual_card` | да | нет | нет |
| `users.attach_card`, `users.detach_card` | да | есть | нет |
| `virtual_cards.init_mpc`, `confirm_mpc`, `delete_mpc` | нет | нет | нет |
| `virtual_cards.generate_payment_qr` | нет | нет | нет |
| `virtual_cards.get_mpc_qr_list` | нет | нет | безопасный |
| `cards.block_card`, `users.delete_user`, `templates.delete_template` | да | есть | нет |

Тарифицируемые вызовы расходуют месячный пакет запросов договора, повторы тоже.
«Повтор SDK: нет» значит, что после сбоя SDK вызов сам не повторит: сначала
проверьте состояние чтением.

## Если карта уже есть

Шаги 1–4 нужны, чтобы выпустить водителю новую виртуальную карту. Если у
договора уже есть подходящая карта и пользователь, достаточно привязать её и
перейти к шагу 5:

```python
await client.users.attach_card(user_id="1-DRIVER", card_id="70000001")
```

Новому водителю можно сразу передать карту в приглашении: `"cards": ["70000001"]`
вместо `template_id`. После регистрации карта будет привязана к нему.

## 1. Шаблон виртуальной карты

Шаблон задаёт лимиты и разрешённые товары будущей карты. Пример создаёт шаблон
«500 л топлива в месяц, разрешено всё топливо».

```python
created = await client.templates.create_template(type_="Limit", name="Водитель QR")
template_id = created.data  # например, "1-TEMPLATE"

await client.templates.create_template_limit(
    template_id=template_id,
    payload={
        "product_type": fuel_type_id,              # «Топливо» без группы
        "amount": {"unit": "LIT", "value": 500},   # объём в литрах
        "time": {"type": 5, "number": 1},          # 1 месяц
    },
)
await client.templates.create_template_restriction(
    template_id=template_id,
    payload={"product_type": fuel_type_id, "restriction_type": 1},  # 1 — разрешить
)
```

| Параметр | Значение |
| --- | --- |
| `type_` | `"Limit"` — карта с лимитами, `"Wallet"` — карта-кошелёк |
| `name` | до 30 символов |
| `product_type` | ID типа продукта; без `product_group` правило действует на весь тип |
| `amount.unit` / `sum.currency` | `"LIT"` для литров или сумма в рублях (`"810"`) |
| `time.type` | `2` — разовый, `3` — сутки, `4` — неделя, `5` — месяц |
| `restriction_type` | `1` — разрешить, `2` — запретить |

!!! warning "ID продуктов зависят от среды"
    ID типа продукта «Топливо» может различаться между средами, и ID из
    примеров описания API может не подойти. Чужой ID даёт
    `400 «Выбранное значение некорректно»`. Возьмите ID из лимитов уже
    созданных шаблонов (`get_template_limits`, поле `productType` у записи
    с `productTypeName` «Топливо») или из справочников договора.

## 2. Приглашение водителя

```python
invite = await client.invites.create_invite(
    data={
        "role": "Driver",
        "mobile": "79990000000",
        "cards": [],
        "contracts": [{"id": client.contract_id, "template_id": template_id}],
    },
    with_send=True,  # отправить SMS со ссылкой на регистрацию
)
```

- Приглашению нужна карта (`cards`) или шаблон ВК в договоре (`template_id`).
  Без них API отвечает `InviteNotReadyError` (500 «Приглашение не готово к
  отправке»).
- Телефон станет логином водителя. Если такой логин уже есть где-либо в системе
  оператора, API ответит `DuplicateLoginError`, даже если `get_users` этого
  пользователя не показывает: список видит только пользователей вашего договора.
- Ссылка из SMS действует 3 дня. Водитель открывает её на телефоне и
  завершает регистрацию. Имя и фамилию водитель вводит сам: через API их не
  задать.
- Приглашение с шаблоном само карту не выпускает.

## 3. user_id водителя

После регистрации водитель появляется в `users.get_users`: роль `Driver`, договор
с вашим `template_id`, карт пока нет.

```python
mobile = "79990000000"
matches, page = [], 1
while True:
    # get_users отдаёт страницы; q ищет по ФИО, логину, email и телефону.
    users = await client.users.get_users(
        q=mobile, filter={"role": "Driver"}, page=page, on_page=50
    )
    batch = users.result
    matches += [user for user in batch if mobile in {user.mobile_phone, user.login}]
    if not batch or page * 50 >= users.total_count:
        break
    page += 1

# Нужно ровно одно совпадение по полному номеру: по чужому user_id следующий
# шаг выпустит настоящую карту другому человеку.
if len(matches) != 1:
    raise RuntimeError(f"Найдено водителей: {len(matches)}")
user_id = matches[0].id  # например, "1-DRIVER"
```

## 4. Виртуальная карта

```python
card = await client.virtual_cards.release_virtual_card(
    template_id=template_id,  # или type_="limit" / "wallet", но не оба сразу
    user_id=user_id,          # карта сразу привязывается к водителю
)
card_id = card.data.id        # например, "217000000"; статус Active
```

- Метод тарифицируется и не повторяется автоматически. При сетевом сбое
  сначала проверьте карты водителя через `get_users`.
- У виртуальной карты только один водитель. Попытка добавить второго:
  `403 «Добавление второго водителя к Виртуальной карте запрещено»`. Чтобы
  передать карту, отвяжите её (`users.detach_card`) и привяжите к другому
  пользователю (`users.attach_card`).
- У только что выпущенной виртуальной карты номер в `get_users` может прийти
  не строкой; SDK принимает такой ответ (`UserCardItem.number` — `str | None`).

## 5. Мобильный профиль карты

```python
await client.virtual_cards.init_mpc(
    card_id=card_id,
    user_id=user_id,
    pin="1234",                  # 4–8 цифр, понадобится для каждого QR
    device_id="ivanov-phone-01", # 1–255 символов
    device_name="Иванов телефон",# 11–17 символов
)
await client.virtual_cards.confirm_mpc(card_id=card_id, code=sms_code)
```

- `init_mpc` отправляет SMS с кодом на телефон водителя. `confirm_mpc` принимает
  этот код.
- Длину PIN, `device_id` и `device_name` SDK проверяет до запроса:
  `RequestValidationError` без введённых значений в тексте.
- Карта должна быть привязана к `user_id`, иначе
  `403 «Данная карта не привязана к пользователю»`.
- На карте только один МПК. Существующий профиль удалите через `delete_mpc`.
- Неверный SMS-код блокирует выпуск. Не перебирайте коды: блокировку снимает
  `reset_mpc`.
- МПК выпускается на телефон пользователя: проверьте, что у него включён
  мобильный доступ (`access.mobile` в `get_users`). Для пользователя без
  мобильного доступа `init_mpc` может ответить 500 «технические проблемы».
- После нового `init_mpc` счётчик строк начинается заново.

## 6. Платёжная строка и QR-код

```python
import time

import qrcode

payment = await client.virtual_cards.generate_payment_qr(card_id=card_id, pin="1234")
if payment.end_date <= int(time.time()):
    raise RuntimeError("Строка уже недействительна, запросите новую")

image = qrcode.QRCode(border=1)
image.add_data(payment.code)  # BER-TLV без изменений
image.print_ascii(invert=True)
```

- `code` — строка BER-TLV, а не картинка. Передайте её в генератор QR без
  изменений.
- `end_date` — Unix-время окончания в секундах. Описание API обещает до 10 минут,
  но строка может жить заметно меньше, например около 3 минут. Проверяйте
  `end_date` перед показом и не кэшируйте строку.
- По описанию API `transaction_count` — проведённые транзакции, `tries` — предел
  попыток оплаты. На практике `transaction_count` растёт при каждой генерации,
  даже без оплаты; `tries` —
  предел строк до перевыпуска МПК.
- Оплата проходит на кассе АЗС, которая принимает QR. SDK сам не платит.

Проверить профиль можно в любой момент, это бесплатно:

```python
profiles = await client.virtual_cards.get_mpc_qr_list(contract_id="1-CONTRACT")
for profile in profiles.result:
    # use_mpc — профиль работает; device_name — устройство из init_mpc.
    print(profile.card_id, profile.use_mpc, profile.device_name,
          profile.transaction_count, profile.tries)
```

Если оплата на кассе не проходит или нужно сменить PIN, перевыпустите ключи через
`update_mpc`. Блокировку после неверного кода или неверных секретных значений
снимает `reset_mpc` (подробнее в разделе [Оплата по QR-коду](qr-payments.md)).

## 7. Уборка после теста

```python
await client.virtual_cards.delete_mpc(card_id=card_id)
await client.cards.block_card(card_ids=[card_id])
await client.users.delete_user(user_id=user_id)
await client.templates.delete_template(template_id=template_id)
```

Сначала удалите МПК, затем заблокируйте карту, потом удалите водителя и шаблон.
Удаление необратимо.

## Ошибки по шагам

| Шаг | Ответ API | Исключение SDK | Что делать |
| --- | --- | --- | --- |
| Лимит шаблона | 400 «Выбранное значение некорректно» | `ValidationError` | проверить `product_type` для этой среды |
| Приглашение | 500 «Приглашение не готово к отправке» | `InviteNotReadyError` | добавить карту или `template_id` |
| Приглашение, пользователь | логин уже существует | `DuplicateLoginError` | взять другой телефон |
| Привязка ВК | 403 «Добавление второго водителя…» | `AccessDeniedError` | отвязать карту от прежнего водителя |
| `init_mpc` | 403 «Данная карта не привязана к пользователю» | `AccessDeniedError` | привязать карту к `user_id` |
| `init_mpc` | 500 «технические проблемы» | `ServerError` | проверить `access.mobile` и `get_mpc_qr_list`, повторить позже |
| `generate_payment_qr` | 404 «На карте нет МПК» | `NotFoundError` | выпустить МПК (шаг 5) |
| `generate_payment_qr` | 502 от шлюза | `ServerError`, `reason="outcome_unknown"` | см. ниже |

Если генерация строки вернула 5xx, результат неизвестен. Посмотрите
`get_mpc_qr_list`: если `transaction_count` не вырос, строка не выдана. Повтор
генерации денег не списывает, он только расходует `tries`. Изменения карты,
пользователя и МПК после 5xx вслепую не повторяйте: сначала проверьте состояние
чтением.

См. также: [Оплата по QR-коду](qr-payments.md), [Ошибки и повторы](errors.md).
