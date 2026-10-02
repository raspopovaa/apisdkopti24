---
description: "Удаление мобильного профиля карты: пример client.virtual_cards.delete_mpc() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Удаление мобильного профиля карты

`client.virtual_cards.delete_mpc()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/delete_mpc.py)

Отключить мобильный профиль карты, например при смене телефона водителя.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/deleteMPC` | Да | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Удаление мобильного профиля карты: client.virtual_cards.delete_mpc().

Отключить мобильный профиль карты, например при смене телефона водителя.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/delete_mpc.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/delete_mpc/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "5050543"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.delete_mpc(card_id=CARD_ID)
    print("Профиль удалён" if response.data else "Сервер не подтвердил удаление")


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
| `card_id` | <code>str</code> | Да | — | ID карты |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/5050543/deleteMPC HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `5050543` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`SimpleActionResponse`](../../data-types/virtual_cards/SimpleActionResponse.md).
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
Профиль удалён
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`SimpleActionResponse`](../../data-types/virtual_cards/SimpleActionResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>StatusModel</code> | Да | Статус выполнения операции |
| `data` | `data` | <code>bool</code> | Да | Результат операции (True — успешно) |
| `timestamp` | `timestamp` | <code>int</code> | Да | Время выполнения запроса (Unix Timestamp) |

#### [`StatusModel`](../../data-types/virtual_cards/StatusModel.md) · `status`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `status.code` | <code>int</code> | Да | Код статуса ответа (200 — успешно, иное — ошибка) |
| `errors` | `status.errors` | <code>list[dict[str, object]] &#124; None</code> | Нет | Массив ошибок операции |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Мобильный профиль уже удалён или не выпускался.

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
NotFoundError: [404] Объект или маршрут не найден при выполнении delete_mpc Сообщение сервера: МПК не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
