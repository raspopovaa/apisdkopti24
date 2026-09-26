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

| Параметр | Python-тип | Обязательный | По умолчанию | Описание |
|---|---|:---:|---|---|
| `card_ids` | `list[str]` | Да | — | ID карт |
| `contract_id` | `str | None` | Нет | `None` | ID контракта |
| `block` | `bool` | Нет | `True` | `true` — заблокировать карту, `false` — разблокировать. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`BlockCardRequest`](../../data-types/cards/BlockCardRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str` | Да | минимальная длина: 1 | ID контракта |
| `card_id` | `list[str]` | Да | минимум элементов: 1 | ID карт |
| `block` | `bool` | Нет | — | true – блокировка, false – разблокировка |

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

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | форма | `1-2Q4CN99` | string | Да | ID контракта |
| `card_id` | форма | `517945` | string | Да | ID карт |
| `block` | форма | `true` | string | Да | true – блокировка, false – разблокировка |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

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

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`IDListResponse`](../../data-types/cards/IDListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `list[str] | None` | Нет | [string, string], необязательное | Список идентификаторов обработанных карт |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

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

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Блокировка и разблокировка карты». Запрос в спецификации: `POST http://localhost/vip/v1/blockCard`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- `contract_id` в API обязателен. Если его не передать, SDK подставит договор, выбранный при авторизации.
- `block` в API обязателен. SDK передаёт его всегда; значение по умолчанию — `True`.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
Блокировка карты
POST: http://localhost/vip/v1/blockCard
BODY: contract_id=1-B7C8D&card_id=["517945","517946"]&block=true
Разблокировка карты
POST: http://localhost/vip/v1/blockCard
BODY: contract_id=1-B7C8D&card_id=["517945","517946"]&block=false
```

## Что важно знать

- SDK не повторяет этот метод автоматически при сетевой ошибке: при неясном результате проверьте статус карты через `get_card_detail`, а не отправляйте запрос повторно.
- В форме запроса `block` передаётся строкой `"true"` или `"false"`, а `card_id` повторяется для каждой карты списка.
- В примере спецификации несколько карт переданы одной строкой JSON-массива: `card_id=["517945","517946"]`. SDK передаёт повторяющиеся поля `card_id`. Для одной карты такой запрос реальный API принимает; для нескольких карт формат на реальном API пока не проверен — проверьте на DEMO-стенде.
