---
description: "Сброс счётчика мобильного профиля: пример client.virtual_cards.reset_mpc() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Сброс счётчика мобильного профиля

`client.virtual_cards.reset_mpc()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/reset_mpc.py)

Сбросить счётчик неверных вводов PIN или использований мобильного профиля карты.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/resetMPC` | Да | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Сброс счётчика мобильного профиля: client.virtual_cards.reset_mpc().

Сбросить счётчик неверных вводов PIN или использований мобильного профиля карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/reset_mpc.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/reset_mpc/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "5050543"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.reset_mpc(card_id=CARD_ID, type_="ResetCounterCode")
    print("Счётчик сброшен" if response.data else "Сервер не подтвердил сброс")


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
| `type_` | `str` | Нет | `'ResetCounterCode'` | `ResetCounterCode` сбрасывает блокировку оплаты, `ResetCounterMPC` — блокировку выпуска МПК. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `contract_id` | `str | None` | Нет | `None` | ID договора |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`MPCResetRequest`](../../data-types/virtual_cards/MPCResetRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `type` | `Literal[ResetCounterCode, ResetCounterMPC]` | Нет | допустимые значения: 'ResetCounterCode', 'ResetCounterMPC' | Тип счетчика; по умолчанию ResetCounterCode |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/5050543/resetMPC HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

type=ResetCounterCode
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `5050543` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `type` | форма | `ResetCounterCode` | string | Нет | Тип счетчика; по умолчанию ResetCounterCode |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`ResetMPCResponse`](../../data-types/virtual_cards/ResetMPCResponse.md).
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
Счётчик сброшен
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`ResetMPCResponse`](../../data-types/virtual_cards/ResetMPCResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `StatusModel` | Да | Статус выполнения операции сброса |
| `data` | `data` | `bool` | Да | Результат операции (True — успешно) |
| `timestamp` | `timestamp` | `int` | Да | Время выполнения запроса (Unix Timestamp) |

#### [`StatusModel`](../../data-types/virtual_cards/StatusModel.md) · `status`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `status.code` | `int` | Да | Код статуса ответа (200 — успешно, иное — ошибка) |
| `errors` | `status.errors` | `list[dict[str, object]] | None` | Нет | Массив ошибок операции |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Для карты нет выпущенного мобильного профиля.

**Что делать:** Проверьте профили через `get_mpc_qr_list()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "МПК не найден"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении reset_mpc Сообщение сервера: МПК не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.virtual_cards.reset_mpc(card_id=CARD_ID, type_="ResetAll")
```

Допустимы только типы `ResetCounterCode` и `ResetCounterMPC`. Исключение `pydantic.ValidationError`:

```text
1 validation error for MPCResetRequest
type
  Input should be 'ResetCounterCode' or 'ResetCounterMPC' [type=literal_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `type_`: `ResetCounterCode` (по умолчанию) или `ResetCounterMPC`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
