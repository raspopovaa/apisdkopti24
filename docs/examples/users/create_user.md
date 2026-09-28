---
description: "Создание пользователя: пример client.users.create_user() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/users.yaml. Не редактируйте вручную. -->

# Создание пользователя

`client.users.create_user()` · [справочник метода](../../methods/users.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/users/create_user.py)

Создать водителя по телефону и вашему внутреннему ID. Телефон становится логином пользователя.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/users` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Создание пользователя: client.users.create_user().

Создать водителя по телефону и вашему внутреннему ID. Телефон становится логином
пользователя.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/users/create_user.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/users/create_user/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.users.create_user(
        uuid="62f2e267-4398-4ea2-b02e-6e88b81b0958", mobile="79990000000"
    )
    print(f"ID пользователя: {response.data}")


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
| `uuid` | `str` | Да | — | Внутренний ID водителя в системе клиента. |
| `mobile` | `str` | Да | — | Телефон водителя, используемый как логин. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`UserCreateRequest`](../../data-types/users/UserCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `uuid` | `str` | Да | минимальная длина: 1 | Ваш внутренний ID водителя |
| `mobile` | `str` | Да | минимальная длина: 1 | Телефон водителя (Логин) |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/users HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

uuid=62f2e267-4398-4ea2-b02e-6e88b81b0958&mobile=79990000000
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `uuid` | форма | `62f2e267-4398-4ea2-b02e-6e88b81b0958` | string | Да | Ваш внутренний ID водителя |
| `mobile` | форма | `79990000000` | string | Да | Телефон водителя (Логин) |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`UserCreateResponse`](../../data-types/users/UserCreateResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": "1-3DYGFR9",
  "timestamp": 1586430473
}
```

Вывод примера на этом ответе:

```text
ID пользователя: 1-3DYGFR9
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`UserCreateResponse`](../../data-types/users/UserCreateResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `str` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 409 · `DuplicateConflictError`

**Почему:** Телефон уже используется как логин другого пользователя.

**Что делать:** Найдите пользователя через `get_users(q=...)`.

Ответ API:

```json
{
  "status": {
    "code": 409,
    "errors": [
      {
        "type": "duplicateConflict",
        "message": "Пользователь с таким телефоном уже существует"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
DuplicateConflictError: [409] Конфликт повторного запроса при выполнении create_user Сообщение сервера: Пользователь с таким телефоном уже существует. Подсказка: Проверьте интеграцию на повторную отправку однотипных запросов.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.users.create_user(uuid="62f2e267-4398-4ea2-b02e-6e88b81b0958", mobile="")
```

Телефон обязателен. Исключение `pydantic.ValidationError`:

```text
1 validation error for UserCreateRequest
mobile
  String should have at least 1 character [type=string_too_short]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `uuid` — ваш собственный идентификатор водителя, по нему удобно сопоставлять пользователя с вашей системой.
- `mobile` — только цифры, от 11 до 13, без `+`: номер `+79990000000` API отклоняет с ошибкой `400`.
- Параметр `mobile`: только цифры, 11–13 знаков, без `+`. В SDK — передаёт значение как есть.
