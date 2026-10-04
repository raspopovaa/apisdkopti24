---
description: "Повторная отправка приглашения: пример client.invites.resend_invite() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/invites.yaml. Не редактируйте вручную. -->

# Повторная отправка приглашения

`client.invites.resend_invite()` · [справочник метода](../../methods/invites.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/invites/resend_invite.py)

Отправить действующее приглашение ещё раз по SMS или email.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/invites/{invite_id}/send` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Повторная отправка приглашения: client.invites.resend_invite().

Отправить действующее приглашение ещё раз по SMS или email.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/invites/resend_invite.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/invites/resend_invite/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
INVITE_ID = "000000000000000000000001"


async def example(client: APIClient) -> None:
    response = await client.invites.resend_invite(invite_id=INVITE_ID)
    print(f"Отправлено. Попыток повторной отправки в день: {response.data.attempts}")


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
| `invite_id` | <code>str</code> | Да | — | Идентификатор приглашения. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/invites/000000000000000000000001/send HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `invite_id` | путь | `000000000000000000000001` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`InviteResponse`](../../data-types/invites/InviteResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "id": "000000000000000000000001",
    "url": "https://lk.opti-24.ru/invite/?hash=000000000000000000000001",
    "attempts": 1,
    "expired_at": 1574965330
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Отправлено. Попыток повторной отправки в день: 1
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`InviteResponse`](../../data-types/invites/InviteResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>InviteActionResult</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`InviteActionResult`](../../data-types/invites/InviteActionResult.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.id` | <code>str</code> | Да | ID приглашения |
| `url` | `data.url` | <code>str</code> | Да | Ссылка на приглашение |
| `attempts` | `data.attempts` | <code>int</code> | Да | Количество попыток отправки |
| `expired_at` | `data.expired_at` | <code>int</code> | Да | Дата истечения срока действия ссылки (timestamp) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 409 · `DuplicateConflictError`

**Почему:** Приглашение уже отправлялось максимально допустимое число раз.

**Что делать:** Создайте новое приглашение или отправьте ссылку самостоятельно.

Ответ API:

```json
{
  "status": {
    "code": 409,
    "errors": [
      {
        "type": "duplicateConflict",
        "message": "Лимит повторных отправок исчерпан"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
DuplicateConflictError: [409] Конфликт повторного запроса при выполнении resend_invite Сообщение сервера: Лимит повторных отправок исчерпан. Подсказка: Проверьте интеграцию на повторную отправку однотипных запросов.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Метод отправляется запросом GET, но отправляет сообщение получателю, поэтому пример спрашивает подтверждение. SDK не повторяет его автоматически — ни после `429`/`509`, ни после сетевой ошибки: при неясном результате проверьте `attempts` и `sended_at` в `get_invites()`.
- Между отправками одного приглашения должна пройти минута: более ранний вызов, в том числе сразу после `create_invite(with_send=True)`, сервер отклоняет ответом `429`. Это пауза конкретного приглашения, а не общий лимит частоты запросов.
- После одной успешной повторной отправки `attempts` в ответе изменился с 2 на 0, а `expired_at` не изменился: повторная отправка не продлевает приглашение — для этого есть `prolong_invite()`.
