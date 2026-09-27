---
description: "Выпуск мобильного профиля карты: пример client.virtual_cards.init_mpc() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Выпуск мобильного профиля карты

`client.virtual_cards.init_mpc()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/init_mpc.py)

Первый шаг выпуска МПК на устройстве водителя: задать PIN профиля и устройство. Затем профиль подтверждается кодом из SMS через `confirm_mpc`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/initMPC` | Да | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Выпуск мобильного профиля карты: client.virtual_cards.init_mpc().

Первый шаг выпуска МПК на устройстве водителя: задать PIN профиля и устройство. Затем
профиль подтверждается кодом из SMS через `confirm_mpc`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/init_mpc.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/init_mpc/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "15054450"
USER_ID = "1-2Q468ZB"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.init_mpc(
        card_id=CARD_ID,
        user_id=USER_ID,
        pin="4815",
        device_id="device-example",
        device_name="Pixel Example",
    )
    print("Код подтверждения отправлен по SMS" if response.data else "Выпуск не начат")


async def main() -> None:
    answer = input("Вызов изменяет данные на реальном API. Продолжить? [yes/no] ")
    if answer.strip().lower() != "yes":
        return
    settings = ConnectionSettings.from_env()
    credentials = EnvironmentCredentialsProvider.from_env()
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        contract_id = os.getenv("API_CONTRACT_ID")
        if contract_id:
            client.select_contract(contract_id=contract_id)
        await example(client)


if __name__ == "__main__":
    asyncio.run(main())
```

### Параметры метода

| Параметр | Python-тип | Обязательный | По умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | `str` | Да | — | ID карты |
| `user_id` | `str` | Да | — | ID пользователя, к которому привязана карта. |
| `pin` | `str` | Да | — | Новый PIN мобильного профиля из 4–8 цифр. |
| `device_id` | `str` | Да | — | Идентификатор устройства длиной 1–255 символов. |
| `device_name` | `str` | Да | — | Название устройства длиной 11–17 символов. |
| `contract_id` | `str | None` | Нет | `None` | ID договора |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`MPCInitRequest`](../../data-types/virtual_cards/MPCInitRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `pin` | `str` | Да | шаблон: '^[0-9]{4,8}$' | Пин-код из 4–8 цифр |
| `user_id` | `str` | Да | минимальная длина: 1 | ID пользователя |
| `device_id` | `str` | Да | минимальная длина: 1; максимальная длина: 255 | ID устройства |
| `device_name` | `str` | Да | минимальная длина: 11; максимальная длина: 17 | Название устройства |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/15054450/initMPC HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

pin=***&user_id=1-2Q468ZB&device_id=***&device_name=Pixel Example
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `15054450` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `pin` | форма | `***` | string | Да | Пин-код из 4–8 цифр |
| `user_id` | форма | `1-2Q468ZB` | string | Да | ID пользователя |
| `device_id` | форма | `***` | string | Да | ID устройства |
| `device_name` | форма | `Pixel Example` | string | Да | Название устройства |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`MPCActionResponse`](../../data-types/virtual_cards/MPCActionResponse.md).
Пример ответа условный, структура совпадает с моделью SDK..

```json
{
  "status": {
    "code": 200
  },
  "data": true,
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Код подтверждения отправлен по SMS
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`MPCActionResponse`](../../data-types/virtual_cards/MPCActionResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `bool` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 409 · `DuplicateConflictError`

**Почему:** Для карты уже выпущен мобильный профиль.

**Что делать:** Проверьте профили через `get_mpc_qr_list()`.

Ответ API:

```json
{
  "status": {
    "code": 409,
    "errors": [
      {
        "type": "duplicateConflict",
        "message": "МПК уже выпущен"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
DuplicateConflictError: [409] Конфликт повторного запроса при выполнении init_mpc Сообщение сервера: МПК уже выпущен. Подсказка: Проверьте интеграцию на повторную отправку однотипных запросов.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.virtual_cards.init_mpc(card_id=CARD_ID, user_id=USER_ID, pin="12", device_id="device-example", device_name="Pixel Example")
```

PIN должен состоять из 4–8 цифр. Исключение `pydantic.ValidationError`:

```text
1 validation error for MPCInitRequest
pin
  Value error, pin должен содержать от 4 до 8 цифр [type=value_error]
```

```python
await client.virtual_cards.init_mpc(card_id=CARD_ID, user_id=USER_ID, pin="4815", device_id="device-example", device_name="Pixel")
```

Название устройства короче 11 символов. Исключение `pydantic.ValidationError`:

```text
1 validation error for MPCInitRequest
device_name
  String should have at least 11 characters [type=string_too_short]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- PIN — от 4 до 8 цифр, название устройства — от 11 до 17 символов. На странице и в журналах SDK PIN и ID устройства скрыты.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
