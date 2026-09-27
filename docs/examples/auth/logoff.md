---
description: "Завершение сессии: пример client.auth.logoff() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/auth.yaml. Не редактируйте вручную. -->

# Завершение сессии

`client.auth.logoff()` · [справочник метода](../../methods/auth.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/auth/logoff.py)

Завершить серверную сессию, когда работа с API закончена. Закрытие клиента (`async with APIClient(...)`) освобождает только локальные ресурсы и сессию на сервере не завершает.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/logoff` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Завершение сессии: client.auth.logoff().

Завершить серверную сессию, когда работа с API закончена. Закрытие клиента (`async with
APIClient(...)`) освобождает только локальные ресурсы и сессию на сервере не завершает.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/auth/logoff.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/auth/logoff/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.auth.logoff()
    print("Сессия завершена" if response.data else "Сервер не подтвердил выход")


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

| Параметр | Python-тип | Обязательный | По умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/logoff HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`LogoffResponse`](../../data-types/auth/LogoffResponse.md).
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
Сессия завершена
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`LogoffResponse`](../../data-types/auth/LogoffResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `bool` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 401 · `NotAuthenticatedError`

**Почему:** Сессия уже завершена или истекла на сервере.

**Что делать:** Ничего делать не нужно — локальная сессия SDK уже очищена.

Ответ API:

```json
{
  "status": {
    "code": 401,
    "errors": [
      {
        "type": "notAuthenticated",
        "message": "Сессия не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotAuthenticatedError: [401] Необходима авторизация при выполнении logoff Сообщение сервера: Сессия не найдена. Подсказка: Проверьте, что пользователь авторизован и передан корректный session_id.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- SDK очищает локальную сессию и выбранный договор даже при ошибке запроса. Следующий вызов любого метода снова авторизуется автоматически.
