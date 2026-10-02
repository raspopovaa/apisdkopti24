---
description: "Фильтры поиска АЗС: пример client.dictionaries.get_azs_filters() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/dictionaries.yaml. Не редактируйте вручную. -->

# Фильтры поиска АЗС

`client.dictionaries.get_azs_filters()` · [справочник метода](../../methods/dictionaries.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/dictionaries/get_azs_filters.py)

Получить группы фильтров для поиска АЗС и допустимые коды в каждой группе: типы точек, виды топлива, услуги. Коды передаются в `get_azs_list_v2`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/azs/filters` | Нет | Нет | Нет | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Фильтры поиска АЗС: client.dictionaries.get_azs_filters().

Получить группы фильтров для поиска АЗС и допустимые коды в каждой группе: типы точек,
виды топлива, услуги. Коды передаются в `get_azs_list_v2`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/dictionaries/get_azs_filters.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/dictionaries/get_azs_filters/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.dictionaries.get_azs_filters()
    for group in response.data:
        codes = ", ".join(item.code for item in group.items)
        print(f"{group.filter} ({group.name}): {codes}")


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
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/azs/filters HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`AzsFiltersResponse`](../../data-types/dictionaries/AzsFiltersResponse.md).
Пример ответа условный: структура соответствует модели SDK, значения взяты из примеров запросов `get_azs_list_v2`..

```json
{
  "status": {
    "code": 200
  },
  "data": [
    {
      "filter": "poi_types",
      "name": "Тип точки",
      "items": [
        {
          "name": "АЗС",
          "code": "AZS"
        }
      ]
    },
    {
      "filter": "diesel",
      "name": "Дизельное топливо",
      "items": [
        {
          "name": "ДТ",
          "code": "00000000000006"
        }
      ]
    }
  ],
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
poi_types (Тип точки): AZS
diesel (Дизельное топливо): 00000000000006
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`AzsFiltersResponse`](../../data-types/dictionaries/AzsFiltersResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>list[AzsFilterItem] &#124; None</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`AzsFilterItem`](../../data-types/dictionaries/AzsFilterItem.md) · `data[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `filter` | `data[].filter` | <code>str</code> | Да | Ключ фильтра (например: services_with_card, countries и т.д.) |
| `name` | `data[].name` | <code>str</code> | Да | Название фильтра (человекочитаемое) |
| `items` | `data[].items` | <code>list[AzsFilterValue]</code> | Да | Список значений для данного фильтра |

#### [`AzsFilterValue`](../../data-types/dictionaries/AzsFilterValue.md) · `data[].items[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `name` | `data[].items[].name` | <code>str</code> | Да | Название значения фильтра |
| `code` | `data[].items[].code` | <code>str &#124; None</code> | Да | Код значения фильтра; реальный API может вернуть null |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Метод недоступен для ключа API или тарифа.

**Что делать:** Проверьте права ключа API.

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_azs_filters Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Поле `filter` группы — это имя ключа в фильтре `get_azs_list_v2`, а `code` элементов — допустимые значения.
