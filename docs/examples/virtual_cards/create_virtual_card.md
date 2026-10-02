---
description: "Выпуск виртуальной карты: пример client.virtual_cards.create_virtual_card() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Выпуск виртуальной карты

`client.virtual_cards.create_virtual_card()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/create_virtual_card.py)

Выпустить виртуальную карту для пользователя. Для выпуска у пользователя API должен быть указан номер телефона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Выпуск виртуальной карты: client.virtual_cards.create_virtual_card().

Выпустить виртуальную карту для пользователя. Для выпуска у пользователя API должен быть
указан номер телефона.

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

user_id=1-2Q468ZB
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
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
| `status` | `status` | <code>StatusModel</code> | Да | Статус ответа от сервера |
| `data` | `data` | <code>VirtualCardData</code> | Да | Информация о выпущенной виртуальной карте |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Время ответа сервера в формате Unix Timestamp |

#### [`StatusModel`](../../data-types/virtual_cards/StatusModel.md) · `status`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `status.code` | <code>int</code> | Да | Код статуса ответа (200 — успешно, иное — ошибка) |
| `errors` | `status.errors` | <code>list[dict[str, object]] &#124; None</code> | Нет | Массив ошибок операции |

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

### 400 · `ValidationError`

**Почему:** Для выпуска карты у пользователя должен быть номер телефона.

**Что делать:** Проверьте данные пользователя в `client.users.get_users()`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "У пользователя не указан телефон"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении create_virtual_card Сообщение сервера: У пользователя не указан телефон. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `template_id` можно не передавать, если шаблон виртуальной карты уже закреплён за пользователем через `client.users.attach_contracts()`.
- `user_id` необязателен: вызов только с `template_id` выпускает карту на договор. Ответ содержит `id`, `number`, `carrier`, `product` и `status` новой карты.
- Метод выпускает реальную карту и тарифицируется; SDK не повторяет его автоматически. При неясном результате проверьте список карт через `client.cards.get_cards_v2()`.
