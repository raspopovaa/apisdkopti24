---
description: "Запрос кода для сброса PIN: пример client.cards.verify_pin() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Запрос кода для сброса PIN

`client.cards.verify_pin()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/verify_pin.py)

Первый шаг сброса счётчика неверных вводов PIN: сервер отправляет одноразовый код. Второй шаг — `reset_pin` с этим кодом.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/verifyPIN` | Да | Нет | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Запрос кода для сброса PIN: client.cards.verify_pin().

Первый шаг сброса счётчика неверных вводов PIN: сервер отправляет одноразовый код.
Второй шаг — `reset_pin` с этим кодом.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/verify_pin.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/verify_pin/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    response = await client.cards.verify_pin(card_id=CARD_ID)
    if response.data:
        print("Код отправлен. Передайте его в client.cards.reset_pin(card_id=..., code=...)")


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

| Параметр | Тип | По умолчанию |
|---|---|---|
| `card_id` | `str` | обязательный |
| `contract_id` | `str \| None` | `None` |
| `api_version` | `str \| None` | `None` |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/382359/verifyPIN?contract_id=1-2Q4CN99 HTTP/1.1
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

SDK проверяет ответ моделью [`BoolResponse`](../../data-types/cards/BoolResponse.md).
Пример ответа взят из спецификации API 1.1.60.

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
Код отправлен. Передайте его в client.cards.reset_pin(card_id=..., code=...)
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 409 · `DuplicateConflictError`

**Почему:** Предыдущий код ещё действует, а запрос отправлен повторно.

**Что делать:** Дождитесь кода и используйте его в `reset_pin`.

Ответ API:

```json
{
  "status": {
    "code": 409,
    "errors": [
      {
        "type": "duplicateConflict",
        "message": "Код уже отправлен"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
DuplicateConflictError: [409] Конфликт повторного запроса при выполнении verify_pin Сообщение сервера: Код уже отправлен. Подсказка: Проверьте интеграцию на повторную отправку однотипных запросов.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Не вызывайте метод в цикле: каждый вызов отправляет новый код.
