---
description: "Водители карты: пример client.cards.get_card_drivers() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Водители карты

`client.cards.get_card_drivers()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/get_card_drivers.py)

Получить пользователей (водителей), которым доступна карта.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/cards/{card_id}/drivers` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Водители карты: client.cards.get_card_drivers().

Получить пользователей (водителей), которым доступна карта.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_card_drivers.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_card_drivers/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    response = await client.cards.get_card_drivers(card_id=CARD_ID)
    print(f"Водителей: {response.total_count}")
    for driver in response.result:
        print(f"{driver.id}  {driver.last_name} {driver.first_name}  роль: {driver.role}")


async def main() -> None:
    answer = input("Вызов тарифицируется на реальном API. Продолжить? [yes/no] ")
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

| Параметр | Тип | По умолчанию |
|---|---|---|
| `card_id` | `str` | обязательный |
| `contract_id` | `str \| None` | `None` |
| `api_version` | `str \| None` | `None` |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/cards/382359/drivers?contract_id=1-2Q4CN99 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе |
|---|---|---|---|
| `card_id` | путь | `382359` | string |
| `contract_id` | строка запроса | `1-2Q4CN99` | string |
| `contract_id` | заголовок | `1-2Q4CN99` | string |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardDriversResponse`](../../data-types/cards/CardDriversResponse.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 2,
    "result": [
      {
        "id": "1-3AKNC9S",
        "login": "<LOGIN>",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "date": "01/01/1970",
        "position": "Водитель",
        "role": "Водитель",
        "mobile_phone": "79990000000",
        "email": "user@example.com"
      },
      {
        "id": "1-37TPIP6",
        "login": "<LOGIN>",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "date": "07/12/1981",
        "position": "Дальнобойщик",
        "role": "Водитель",
        "mobile_phone": "79990000000",
        "email": "user@example.com"
      }
    ]
  },
  "timestamp": 1582741325
}
```

Вывод примера на этом ответе:

```text
Водителей: 2
1-3AKNC9S  Иванов Иван  роль: Водитель
1-37TPIP6  Иванов Иван  роль: Водитель
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Карты с таким `card_id` нет в выбранном договоре.

**Что делать:** Возьмите `id` карты из `get_cards_v2`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Карта не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении get_card_drivers Сообщение сервера: Карта не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.get_card_drivers(card_id="../cards")
```

Идентификатор с `/` мог бы изменить путь запроса, поэтому SDK отклоняет его до отправки. Исключение `ValueError`:

```text
Небезопасный параметр пути: card_id
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `card_id` передаётся в пути запроса (`cards/{card_id}/drivers`). SDK экранирует его и отклоняет значения с `/`, `?`, `#`, `.` и `..`.
- Ответ содержит персональные данные водителей (телефон, email). Не пишите его в журналы целиком.
