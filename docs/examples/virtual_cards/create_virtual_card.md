---
description: "Выпуск виртуальной карты: пример client.virtual_cards.create_virtual_card() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Выпуск виртуальной карты

`client.virtual_cards.create_virtual_card()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/create_virtual_card.py)

Выпустить виртуальную карту по шаблону ВК, закреплённому за пользователем, или по явно указанному шаблону.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Выпуск виртуальной карты: client.virtual_cards.create_virtual_card().

Выпустить виртуальную карту по шаблону ВК, закреплённому за пользователем, или по явно
указанному шаблону.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/create_virtual_card.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/create_virtual_card/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
USER_ID = "1-2Q468ZB"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.create_virtual_card(user_id=USER_ID)
    card = response.data
    print(f"Карта {card.id}: {card.carrier}, продукт {card.product}, статус {card.status}")


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
| `user_id` | <code>str &#124; None</code> | Нет | `None` | ID пользователя (Если указан, то выпуск карты производится с использванием данных указанного клиента пользователя) |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `template_id` | <code>str &#124; None</code> | Нет | `None` | ID шаблона ВК (Не обязателен, если шаблон ВК был ранее закреплен за пользователем) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`VirtualCardCreateRequest`](../../data-types/virtual_cards/VirtualCardCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `template_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID шаблона ВК (Не обязателен, если шаблон ВК был ранее закреплен за пользователем) |
| `user_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID пользователя (Если указан, то выпуск карты производится с использванием данных указанного клиента пользователя) |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-2Q4CN99&user_id=1-2Q468ZB
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | форма | `1-2Q4CN99` | string | Нет | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `user_id` | форма | `1-2Q468ZB` | string | Нет | ID пользователя (Если указан, то выпуск карты производится с использванием данных указанного клиента пользователя) |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`VirtualCardResponse`](../../data-types/virtual_cards/VirtualCardResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "id": "15054450",
    "number": "7000000000000000",
    "carrier": "Virtual Card",
    "product": "wallet",
    "status": "Active"
  },
  "timestamp": 1588540016
}
```

Вывод примера на этом ответе:

```text
Карта 15054450: Virtual Card, продукт wallet, статус Active
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`VirtualCardResponse`](../../data-types/virtual_cards/VirtualCardResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>VirtualCardData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`VirtualCardData`](../../data-types/virtual_cards/VirtualCardData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.id` | <code>str</code> | Да | ID виртуальной карты |
| `number` | `data.number` | <code>str &#124; None</code> | Нет | Номер виртуальной карты |
| `carrier` | `data.carrier` | <code>str &#124; None</code> | Нет | Тип носителя, обычно 'Virtual Card' |
| `product` | `data.product` | <code>str &#124; None</code> | Нет | Тип продукта карты ('wallet' или 'limit') |
| `status` | `data.status` | <code>str &#124; None</code> | Нет | Статус карты (например, 'Active', 'Blocked', 'Pending') |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Роль учётной записи не разрешает метод, договор не привязан к учётной записи, исчерпан тариф или неверен ключ API.

**Что делать:** Проверьте роль, привязку договора и остаток запросов по тарифу.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Доступ запрещён"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении create_virtual_card Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Порядок подготовки: создать и настроить шаблон ВК (`client.templates.create_template()`), закрепить его за пользователем, который будет выпускать карты (`client.users.attach_contracts()`, поле `template_id`), после чего выпускать карты.
- `template_id` можно не передавать, если шаблон виртуальной карты уже закреплён за пользователем через `client.users.attach_contracts()`.
- Договор — `contract_id` или выбранный договор сессии. Без договора сервер выпустил бы карту на первый из договоров пользователя, поэтому SDK всегда передаёт договор и без него выдаёт `RequestValidationError` до запроса.
- `user_id` необязателен: вызов только с `template_id` выпускает карту на договор. Ответ содержит `id`, `number`, `carrier`, `product` и `status` новой карты.
- Метод выпускает реальную карту и тарифицируется, на DEMO недоступен; SDK не повторяет его автоматически. При неясном результате проверьте список карт через `client.cards.get_cards_v2()`.
- В описании API тело запроса — JSON, но SDK отправляет форму: сервер её принимает.
