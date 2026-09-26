---
description: "Сброс счётчика неверных вводов PIN: пример client.cards.reset_pin() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Сброс счётчика неверных вводов PIN

`client.cards.reset_pin()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/reset_pin.py)

Второй шаг сброса: подтвердить одноразовым кодом из `verify_pin`, после чего карту снова можно использовать с PIN.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/resetPIN` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Сброс счётчика неверных вводов PIN: client.cards.reset_pin().

Второй шаг сброса: подтвердить одноразовым кодом из `verify_pin`, после чего карту снова
можно использовать с PIN.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/reset_pin.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/reset_pin/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    ValidationError,
)

# Условные значения: замените своими.
CARD_ID = "382359"
CODE = "123456"


async def example(client: APIClient) -> None:
    try:
        response = await client.cards.reset_pin(card_id=CARD_ID, code=CODE)
    except ValidationError:
        print("Код неверный или устарел: запросите новый через verify_pin")
        return
    print("Счётчик сброшен" if response.data else "Сервер не подтвердил сброс")


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
| `card_id` | `str` | обязательный |
| `code` | `str` | обязательный |
| `contract_id` | `str \| None` | `None` |
| `api_version` | `str \| None` | `None` |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/382359/resetPIN HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-2Q4CN99&code=123456
```

| Поле | Где передаётся | Значение | Тип в запросе |
|---|---|---|---|
| `card_id` | путь | `382359` | string |
| `contract_id` | форма | `1-2Q4CN99` | string |
| `code` | форма | `123456` | string |
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
Счётчик сброшен
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Код введён с ошибкой, устарел или уже использован.

**Что делать:** Запросите новый код через `verify_pin`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Неверный проверочный код"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении reset_pin Сообщение сервера: Неверный проверочный код. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.reset_pin(card_id=CARD_ID, code="")
```

Пустой код отклоняется моделью запроса. Исключение `pydantic.ValidationError`:

```text
1 validation error for ResetPinRequest
code
  String should have at least 1 character [type=string_too_short]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Код одноразовый. SDK скрывает его в журналах (поле `code`), но не храните его в своих логах и не передавайте третьим лицам.
