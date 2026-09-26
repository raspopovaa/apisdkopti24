---
description: "Блокировка и разблокировка карт: пример client.cards.block_card() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Блокировка и разблокировка карт

`client.cards.block_card()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/block_card.py)

Заблокировать утраченную карту до её замены. Тот же метод с `block=False` разблокирует карты.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/blockCard` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Блокировка и разблокировка карт: client.cards.block_card().

Заблокировать утраченную карту до её замены. Тот же метод с `block=False` разблокирует
карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/block_card.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/block_card/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    AccessDeniedError,
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
)

# Условные значения: замените своими.
CARD_ID = "517945"


async def example(client: APIClient) -> None:
    try:
        response = await client.cards.block_card(card_ids=[CARD_ID], block=True)
    except AccessDeniedError as error:
        print(f"Блокировка запрещена: {error.hint}")
        return
    print(f"Обработаны карты: {', '.join(response.data or [])}")


async def main() -> None:
    answer = input("Вызов изменяет данные и тарифицируется на реальном API. Продолжить? [yes/no] ")
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
| `card_ids` | `list[str]` | обязательный |
| `contract_id` | `str \| None` | `None` |
| `block` | `bool` | `True` |
| `api_version` | `str \| None` | `None` |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/blockCard HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-2Q4CN99&card_id=517945&block=true
```

| Поле | Где передаётся | Значение | Тип в запросе |
|---|---|---|---|
| `contract_id` | форма | `1-2Q4CN99` | string |
| `card_id` | форма | `517945` | string |
| `block` | форма | `true` | string |
| `contract_id` | заголовок | `1-2Q4CN99` | string |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`IDListResponse`](../../data-types/cards/IDListResponse.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    "517945",
    "517946"
  ],
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Обработаны карты: 517945, 517946
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Роль пользователя API не разрешает изменять карты, например доступ только на чтение.

**Что делать:** Проверьте роль пользователя; у пользователя с `read_only` метод недоступен.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Недостаточно прав для блокировки карты"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении block_card Сообщение сервера: Недостаточно прав для блокировки карты. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### 409 · `DuplicateConflictError`

**Почему:** Такой же запрос по этим картам отправлен повторно, пока первый ещё выполняется.

**Что делать:** Не повторяйте запрос сразу. Проверьте статус карт через `get_card_detail` и отправляйте запрос снова только при необходимости.

Ответ API:

```json
{
  "status": {
    "code": 409,
    "errors": [
      {
        "type": "duplicateConflict",
        "message": "Запрос уже обрабатывается"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
DuplicateConflictError: [409] Конфликт повторного запроса при выполнении block_card Сообщение сервера: Запрос уже обрабатывается. Подсказка: Проверьте интеграцию на повторную отправку однотипных запросов.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.block_card(card_ids=[])
```

Нужна хотя бы одна карта; пустой список отклоняется до отправки запроса. Исключение `pydantic.ValidationError`:

```text
1 validation error for BlockCardRequest
card_id
  List should have at least 1 item after validation, not 0 [type=too_short]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- SDK не повторяет этот метод автоматически при сетевой ошибке: при неясном результате проверьте статус карты через `get_card_detail`, а не отправляйте запрос повторно.
- В форме запроса `block` передаётся строкой `"true"` или `"false"`, а `card_id` повторяется для каждой карты списка.
