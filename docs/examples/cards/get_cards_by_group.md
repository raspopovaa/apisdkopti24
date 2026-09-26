---
description: "Карты группы: пример client.cards.get_cards_by_group() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Карты группы

`client.cards.get_cards_by_group()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/get_cards_by_group.py)

Получить карты, входящие в группу карт договора.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/cards` | Нет | Нет | Нет | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Карты группы: client.cards.get_cards_by_group().

Получить карты, входящие в группу карт договора.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_cards_by_group.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_cards_by_group/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
GROUP_ID = "1-CRPDCT2"


async def example(client: APIClient) -> None:
    response = await client.cards.get_cards_by_group(group_id=GROUP_ID)
    for card in response.data.result:
        print(f"{card.id}  {card.number}  {card.status}")


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
| `group_id` | `str` | обязательный |
| `contract_id` | `str \| None` | `None` |
| `api_version` | `str \| None` | `None` |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/cards?contract_id=1-2Q4CN99&group_id=1-CRPDCT2 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе |
|---|---|---|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string |
| `group_id` | строка запроса | `1-CRPDCT2` | string |
| `contract_id` | заголовок | `1-2Q4CN99` | string |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardGroupResponse`](../../data-types/cards/CardGroupResponse.md).
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
        "group": "1-CRPDCT2",
        "contract_id": "1-1FLKAJQ",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "comment": "Комментарий",
        "product": "limit",
        "payment_of_tolls": "N",
        "sync_group_state": "Синхронизирована"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
382359  7000000000000000  Locked(Client)
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Группа удалена или принадлежит другому договору.

**Что делать:** Обновите список групп через `client.card_groups.get_card_groups()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Группа карт не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении get_cards_by_group Сообщение сервера: Группа карт не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.get_cards_by_group(group_id="")
```

Пустой `group_id` отклоняется до отправки запроса. Исключение `RequestValidationError`:

```text
group_id: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- ID групп возвращает `client.card_groups.get_card_groups()`. Тот же результат с пагинацией даёт `get_cards_v2(group_id=...)`.
