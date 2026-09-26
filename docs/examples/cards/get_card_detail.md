---
description: "Сведения о карте: пример client.cards.get_card_detail() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Сведения о карте

`client.cards.get_card_detail()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/get_card_detail.py)

Получить подробную информацию об одной карте: статус, способ авторизации, дату последнего использования, срок действия и настройки таймаута операций.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/cards` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Сведения о карте: client.cards.get_card_detail().

Получить подробную информацию об одной карте: статус, способ авторизации, дату
последнего использования, срок действия и настройки таймаута операций.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_card_detail.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_card_detail/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    NotFoundError,
)

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    try:
        response = await client.cards.get_card_detail(card_id=CARD_ID)
    except NotFoundError:
        print("Карта не найдена: проверьте CARD_ID и выбранный договор")
        return
    for card in response.data.result:
        print(f"Карта {card.number}: статус {card.status}")
        print(f"Последнее использование: {card.date_last_usage}")


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
GET /vip/v1/cards?contract_id=1-2Q4CN99&card_id=382359 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе |
|---|---|---|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string |
| `card_id` | строка запроса | `382359` | string |
| `contract_id` | заголовок | `1-2Q4CN99` | string |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardDetailResponse`](../../data-types/cards/CardDetailResponse.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 1,
    "result": [
      {
        "id": "382359",
        "contract_id": "1-1FLKAJQ",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "can_work_offline": true,
        "card_auth_type": "PIN",
        "comment": "Комментарий",
        "date_last_usage": "2015-04-27 00:00:00",
        "date_released": null,
        "servicecenter_last_usage_name": "602881",
        "transaction_timeout": {
          "type": 2,
          "value": "1"
        },
        "product": "limit",
        "carrier": "Virtual Card",
        "available": "40000",
        "currency": "810",
        "payment_of_tolls": "N",
        "mpc": false,
        "pin_reset": 3,
        "pin_counter": 3,
        "previous": "",
        "next": "382360"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Карта 7000000000000000: статус Locked(Client)
Последнее использование: 2015-04-27 00:00:00
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Карты с таким `card_id` нет или она принадлежит другому договору. Частая причина — передан номер карты вместо её ID.

**Что делать:** Возьмите `id` карты из `get_cards_v2` для того же договора.

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
NotFoundError: [404] Объект или маршрут не найден при выполнении get_card_detail Сообщение сервера: Карта не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.get_card_detail(card_id="  ")
```

SDK отклоняет пустой идентификатор до отправки запроса, чтобы не тратить лимит запросов API. Исключение `RequestValidationError`:

```text
card_id: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `card_id` — внутренний ID карты из `get_cards_v2`, а не 16-значный номер карты.
