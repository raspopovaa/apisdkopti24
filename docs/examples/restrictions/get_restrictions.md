---
description: "Список товарных ограничителей: пример client.restrictions.get_restrictions() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/restrictions.yaml. Не редактируйте вручную. -->

# Список товарных ограничителей

`client.restrictions.get_restrictions()` · [справочник метода](../../methods/restrictions.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/restrictions/get_restrictions.py)

Получить товарные ограничители договора, карты или группы карт: какие типы продуктов разрешены или запрещены.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/restriction` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Список товарных ограничителей: client.restrictions.get_restrictions().

Получить товарные ограничители договора, карты или группы карт: какие типы продуктов
разрешены или запрещены.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/restrictions/get_restrictions.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/restrictions/get_restrictions/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.restrictions.get_restrictions()
    for item in response.data.result:
        kind = "разрешено" if item.restriction_type == 1 else "запрещено"
        print(f"{item.id}: {item.productTypeName} — {kind}")


async def main() -> None:
    answer = input("Вызов тарифицируется на реальном API. Продолжить? [yes/no] ")
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
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID контракта. |
| `card_id` | <code>str &#124; None</code> | Нет | `None` | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все товарные ограничители, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех товарных ограничителях по карте, даже если передан ID группы карт |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | ID группы карт. Если передан ID группы карты, то будут возвращены все товарные ограничители указанной группы карт. Если передан ID карты и ID группы карт, то будет возвращена информация по карте |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/restriction?contract_id=1-T000025 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-T000025` | string | Да | ID контракта. |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`RestrictionGetResponse`](../../data-types/restrictions/RestrictionGetResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 1,
    "result": [
      {
        "id": "9000036",
        "card_id": null,
        "group_id": null,
        "contract_id": "1-T0059",
        "productType": "1-CK231",
        "productGroup": null,
        "productTypeName": "Топливо",
        "productGroupName": null,
        "restriction_type": 2,
        "date": "09/03/2018 00:00:00"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
9000036: Топливо — запрещено
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`RestrictionGetResponse`](../../data-types/restrictions/RestrictionGetResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>RestrictionList</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`RestrictionList`](../../data-types/restrictions/RestrictionList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Общее количество ограничителей |
| `result` | `data.result` | <code>list[RestrictionItem] &#124; None</code> | Нет | Список ограничителей |

#### [`RestrictionItem`](../../data-types/restrictions/RestrictionItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | ID ограничителя |
| `card_id` | `data.result[].card_id` | <code>str &#124; None</code> | Нет | ID карты, если ограничитель задан для карты |
| `group_id` | `data.result[].group_id` | <code>str &#124; None</code> | Нет | ID группы карт, если ограничитель задан для группы |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | ID договора |
| `productType` | `data.result[].productType` | <code>str &#124; None</code> | Нет | ID типа продукта (например, '1-CK231') |
| `productGroup` | `data.result[].productGroup` | <code>str &#124; None</code> | Нет | ID группы продуктов (если применимо) |
| `productTypeName` | `data.result[].productTypeName` | <code>str &#124; None</code> | Нет | Название типа продукта |
| `productGroupName` | `data.result[].productGroupName` | <code>str &#124; None</code> | Нет | Название группы продуктов |
| `restriction_type` | `data.result[].restriction_type` | <code>int &#124; None</code> | Нет | Тип ограничения (1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель) |
| `date` | `data.result[].date` | <code>str</code> | Да | Дата установки ограничителя (DD/MM/YYYY HH:MM:SS) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Пользователь API не имеет доступа к договору.

**Что делать:** Проверьте `contract_id` и права пользователя.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Нет доступа к договору"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_restrictions Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `restriction_type`: 1 — разрешающий ограничитель, 2 — запрещающий.
- `date` приходит в формате `DD/MM/YYYY HH:MM:SS` — день идёт первым, в отличие от лимитов и региональных ограничений.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
- Поле `data.result[].date`: `DD/MM/YYYY HH:MM:SS`. Тип в модели SDK: строка без разбора.
