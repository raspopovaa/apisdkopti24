---
description: "Список карт договора (API v1): пример client.cards.get_cards_v1() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Список карт договора (API v1)

`client.cards.get_cards_v1()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/get_cards_v1.py)

Получить все карты договора одним запросом через первую версию API. Метод нужен для совместимости; для новых интеграций используйте `get_cards_v2`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/cards` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Список карт договора (API v1): client.cards.get_cards_v1().

Получить все карты договора одним запросом через первую версию API. Метод нужен для
совместимости; для новых интеграций используйте `get_cards_v2`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_cards_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_cards_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.cards.get_cards_v1()
    print(f"Всего карт: {response.total_count}")
    for card in response.result:
        print(f"{card.id}  {card.number}  {card.status}  комментарий: {card.comment}")


async def main() -> None:
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
| `contract_id` | `str \| None` | `None` |
| `cache` | `bool` | `True` |
| `api_version` | `str \| None` | `None` |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/cards?contract_id=1-2Q4CN99&cache=true HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе |
|---|---|---|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string |
| `cache` | строка запроса | `true` | string |
| `contract_id` | заголовок | `1-2Q4CN99` | string |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardsListResponse`](../../data-types/cards/CardsListResponse.md).
Пример ответа взят из спецификации API 1.1.60; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 3,
    "result": [
      {
        "id": "382359",
        "contract_id": "1-1FLKAJQ",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "can_work_offline": true,
        "card_auth_type": "PIN",
        "comment": "Комментарий",
        "date_expired": "2034-09-30 23:59:59",
        "date_last_usage": "2015-04-27 00:00:00",
        "date_released": "2014-09-24 00:00:00",
        "servicecenter_last_usage_name": "AZS103261",
        "transaction_last_detail": "",
        "transaction_timeout": {
          "type": "H",
          "value": "1"
        },
        "product": "limit",
        "payment_of_tolls": "N"
      },
      {
        "id": "382360",
        "contract_id": "1-1FLKAJQ",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "can_work_offline": true,
        "card_auth_type": "PIN",
        "comment": "Комментарий",
        "date_expired": "2034-09-30 23:59:59",
        "date_last_usage": null,
        "date_released": "2014-09-24 00:00:00",
        "servicecenter_last_usage_name": null,
        "transaction_last_detail": "",
        "transaction_timeout": {
          "type": "N",
          "value": "10"
        },
        "product": "wallet",
        "payment_of_tolls": "N"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Всего карт: 3
382359  7000000000000000  Locked(Client)  комментарий: Комментарий
382360  7000000000000000  Locked(Client)  комментарий: Комментарий
382361  7000000000000000  Active  комментарий: лимиты не работают
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Пользователь API не имеет доступа к выбранному договору.

**Что делать:** Проверьте `contract_id` и права пользователя.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Нет доступа к договору"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_cards_v1 Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Метод возвращает все карты сразу, без пагинации: на договорах с тысячами карт ответ большой. Для таких договоров удобнее `get_cards_v2` с `onpage`.
- `cache=True` (по умолчанию в SDK) — данные из кэша карт; `cache=False` — прямой запрос в процессинг за актуальными данными.
