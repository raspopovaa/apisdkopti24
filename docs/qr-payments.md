# Оплата по QR-коду

SDK поддерживает полный жизненный цикл мобильного профиля карты (МПК): выпуск,
подтверждение по SMS, генерацию платёжной строки, обновление, удаление и сброс
счётчиков. Методы находятся в `client.virtual_cards` и используют API v2.

Источник требований — спецификация сервиса API QR версии 1.0.4 от 30.05.2024.
Примеры ниже используют условные идентификаторы и не содержат credentials.

## Подготовка МПК

Карта должна быть привязана к указанному пользователю. На одной карте может
существовать только один МПК.

```python
await client.virtual_cards.init_mpc(
    card_id="card-id",
    user_id="user-id",
    pin="1234",
    device_id="device-id",
    device_name="Driver phone",
)

await client.virtual_cards.confirm_mpc(
    card_id="card-id",
    code="432245",
)
```

`pin` должен содержать от 4 до 8 цифр. `device_id` допускает от 1 до 255
символов, `device_name` — от 11 до 17 символов. SDK проверяет эти ограничения до
сетевого запроса. PIN и SMS-код нельзя сохранять в логах или telemetry.

## Формирование платёжного QR-кода

```python
from time import time

payment = await client.virtual_cards.generate_payment_qr(
    card_id="card-id",
    pin="1234",
)

if payment.end_date <= int(time()):
    raise RuntimeError("Платёжная строка уже недействительна")

qr_payload = payment.code
```

API возвращает строку BER-TLV в `payment.code`, но не растровое изображение.
Передайте эту строку выбранной библиотеке отображения QR-кодов. Не преобразуйте
и не сокращайте значение: кассовая система должна получить его без изменений.

Платёжная строка действует не более 10 минут. Всегда проверяйте `end_date`
непосредственно перед показом или оплатой и выпускайте новую строку после
истечения срока. Не кэшируйте её и не передавайте в логи.

Поля `transaction_count` и `tries` показывают число использованных и максимально
доступных попыток. При достижении лимита сервер автоматически перевыпускает МПК.

## Управление профилем

```python
# Перевыпустить ключи без смены PIN.
await client.virtual_cards.update_mpc(card_id="card-id", pin="1234")

# Перевыпустить ключи и изменить PIN.
await client.virtual_cards.update_mpc(
    card_id="card-id", pin="1234", new_pin="4321"
)

# Сбросить блокировку оплаты или выпуска.
await client.virtual_cards.reset_mpc("card-id", "ResetCounterCode")
await client.virtual_cards.reset_mpc("card-id", "ResetCounterMPC")

# Удалить профиль.
await client.virtual_cards.delete_mpc("card-id")
```

Операции изменения МПК не повторяются автоматически после неопределённого
сетевого сбоя. Сначала запросите список профилей и проверьте состояние карты.

## Список выпущенных МПК

```python
profiles = await client.virtual_cards.get_mpc_qr_list()

for profile in profiles.result:
    print(profile.card_number, profile.device_name, profile.use_mpc)
```

Без `contract_id` API может вернуть все МПК клиента. Явно передайте
`contract_id`, если приложению разрешено работать только с одним договором.
