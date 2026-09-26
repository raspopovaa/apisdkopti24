---
description: "Комментарий к карте: пример client.cards.set_card_comment() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Комментарий к карте

`client.cards.set_card_comment()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/set_card_comment.py)

Записать комментарий к карте, например госномер машины или ФИО водителя. Комментарий виден в личном кабинете и в `get_cards_v2`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/setCardComment` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Метод изменяет данные"
    Проверяйте его на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Комментарий к карте: client.cards.set_card_comment().

Записать комментарий к карте, например госномер машины или ФИО водителя. Комментарий
виден в личном кабинете и в `get_cards_v2`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/set_card_comment.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/set_card_comment/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    response = await client.cards.set_card_comment(card_id=CARD_ID, comment="Камаз А123ВС")
    print("Комментарий сохранён" if response.data else "Сервер не подтвердил изменение")


async def main() -> None:
    answer = input("Пример изменяет данные на реальном API. Продолжить? [yes/no] ")
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
| `comment` | `str` | обязательный |
| `contract_id` | `str \| None` | `None` |
| `api_version` | `str \| None` | `None` |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/setCardComment HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

card_id=382359&contract_id=1-2Q4CN99&comment=Камаз А123ВС
```

| Поле | Где передаётся | Значение | Тип в запросе |
|---|---|---|---|
| `card_id` | форма | `382359` | string |
| `contract_id` | форма | `1-2Q4CN99` | string |
| `comment` | форма | `Камаз А123ВС` | string |
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
Комментарий сохранён
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Карты с таким `card_id` нет в выбранном договоре.

**Что делать:** Возьмите `id` карты из `get_cards_v2`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Карта не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении set_card_comment Сообщение сервера: Карта не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.set_card_comment(card_id=CARD_ID, comment="")
```

Пустой комментарий отклоняется моделью запроса. Исключение `pydantic.ValidationError`:

```text
1 validation error for SetCardCommentRequest
comment
  String should have at least 1 character [type=string_too_short]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Поиск `get_cards_v2(q=...)` ищет и по комментарию, поэтому единый формат комментариев упрощает поиск.
