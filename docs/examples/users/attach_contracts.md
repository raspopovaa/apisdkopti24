---
description: "Привязка договоров к пользователю: пример client.users.attach_contracts() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/users.yaml. Не редактируйте вручную. -->

# Привязка договоров к пользователю

`client.users.attach_contracts()` · [справочник метода](../../methods/users.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/users/attach_contracts.py)

Закрепить пользователя за договорами, указать шаблон виртуальной карты и разрешить выпуск мобильного профиля карты (МПК).

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/users/{user_id}/attachContracts` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Привязка договоров к пользователю: client.users.attach_contracts().

Закрепить пользователя за договорами, указать шаблон виртуальной карты и разрешить
выпуск мобильного профиля карты (МПК).

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/users/attach_contracts.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/users/attach_contracts/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.users import UserAttachContractRequest

# Условные значения: замените своими.
USER_ID = "1-FK485FK"
CONTRACT_ID = "1-380B94P"


async def example(client: APIClient) -> None:
    contracts = [UserAttachContractRequest(sid=CONTRACT_ID, use_mpc=True)]
    response = await client.users.attach_contracts(user_id=USER_ID, contracts=contracts)
    print("Договоры привязаны" if response.data else "Сервер не подтвердил привязку")


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
| `user_id` | `str` | Да | — | Идентификатор пользователя. |
| `contracts` | `list[UserAttachContractRequest | Mapping[str, object]]` | Да | — | Список договоров для прикрепления к пользователю. Для каждого договора указываются `sid` — ID договора, `template_id` — ID шаблона ВК, `use_mpc` — разрешение выпуска МПК (`true`/`false`). |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`UserAttachContractRequest`](../../data-types/users/UserAttachContractRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `sid` | `str` | Да | — | ID договора |
| `template_id` | `str | None` | Нет | — | ID шаблона виртуальной карты |
| `use_mpc` | `bool | None` | Нет | — | Разрешён ли выпуск МПК |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/users/1-FK485FK/attachContracts HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
Content-Type: application/json

[
  {
    "sid": "1-380B94P",
    "use_mpc": true
  }
]
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `user_id` | путь | `1-FK485FK` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `(всё тело)` | тело JSON | `[{"sid": "1-380B94P", "use_mpc": true}]` | array | Да | Тело запроса — JSON-массив, а не объект с полями. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`UserBoolResponse`](../../data-types/users/UserBoolResponse.md).
Пример ответа.

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
Договоры привязаны
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`UserBoolResponse`](../../data-types/users/UserBoolResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `bool` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Договора с таким `sid` нет у клиента.

**Что делать:** Возьмите ID договора из `client.auth.auth_user()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Договор не найден"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении attach_contracts Сообщение сервера: Договор не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.users.attach_contracts(user_id=USER_ID, contracts=[])
```

Нужен хотя бы один договор. Исключение `ValueError`:

```text
contracts должен содержать хотя бы один элемент
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `use_mpc=True` разрешает пользователю выпускать мобильный профиль карты — без него виртуальной картой нельзя платить.
- Тело запроса — JSON-массив договоров.
