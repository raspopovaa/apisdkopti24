---
description: "Общий справочник: пример client.dictionaries.get_dictionary() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/dictionaries.yaml. Не редактируйте вручную. -->

# Общий справочник

`client.dictionaries.get_dictionary()` · [справочник метода](../../methods/dictionaries.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/dictionaries/get_dictionary.py)

Получить значения справочника по имени: единицы измерения, статусы карт, товары, регионы, офисы продаж и другие. Коды из справочников передаются в фильтры и параметры других методов.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/getDictionary` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Общий справочник: client.dictionaries.get_dictionary().

Получить значения справочника по имени: единицы измерения, статусы карт, товары,
регионы, офисы продаж и другие. Коды из справочников передаются в фильтры и параметры
других методов.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/dictionaries/get_dictionary.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/dictionaries/get_dictionary/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.dictionaries.get_dictionary(name="Unit")
    for item in response.data.result:
        print(f"{item.id}  {item.value}")


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
| `name` | <code>str</code> | Да | — | Наименование справочника: `CardStatus`, `ContractStatus`, `Country`, `Currency`, `Goods`, `PaymentScheme`, `PaymentTerm`, `ProductGroup`, `ProductType`, `POIType`, `Region`, `Services`, `Unit`, `Office`, `POIPartner` или `DiscountScheme`. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/getDictionary?name=Unit HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `name` | строка запроса | `Unit` | string | Да | Наименование справочника: • CardStatus – Запрос списка статусов карт. • ContractStatus – Запрос списка статусов договора. • Country – Запрос списка стран. • Currency – Запрос списка валют. • Goods – Запрос списка топлива для цен на АЗС. • PaymentScheme – Запрос списка схем оплаты договора. • PaymentTerm – Запрос списка условий оплаты договора. • ProductGroup – Запрос списка групп продукта. • ProductType – Запрос списка типов продукта. • POIType – Запрос списка типов принадлежности АЗС. • Region – Запрос списка регионов. • Services – Запрос списка услуг на АЗС. • Unit – Запрос списка единиц измерения продуктов • Office – Запрос списка офисов продаж • POIPartner – Запрос списка партнеров • DiscountScheme – Запрос списка схем расчета скидки |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`DictionaryResponse`](../../data-types/dictionaries/DictionaryResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 2,
    "result": [
      {
        "id": "LIT",
        "value": "ЛИТ",
        "last_update": "2015-09-25 12:51:52",
        "deleted": 0
      },
      {
        "id": "IT",
        "value": "ШТ",
        "last_update": "2015-09-25 12:52:36",
        "deleted": 0
      }
    ]
  },
  "timestamp": 1586308843
}
```

Вывод примера на этом ответе:

```text
LIT  ЛИТ
IT  ШТ
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`DictionaryResponse`](../../data-types/dictionaries/DictionaryResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>DictionaryData &#124; None</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`DictionaryData`](../../data-types/dictionaries/DictionaryData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество элементов в справочнике |
| `result` | `data.result` | <code>list[DictionaryItem] &#124; None</code> | Нет | Список элементов справочника |

#### [`DictionaryItem`](../../data-types/dictionaries/DictionaryItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Уникальный идентификатор элемента справочника |
| `code` | `data.result[].code` | <code>str &#124; None</code> | Нет | Код элемента (например, код валюты) |
| `value` | `data.result[].value` | <code>str &#124; None</code> | Нет | Значение элемента (используется в старых справочниках) |
| `name` | `data.result[].name` | <code>str &#124; None</code> | Нет | Название элемента (используется в новых справочниках) |
| `deleted` | `data.result[].deleted` | <code>int &#124; None</code> | Нет | Признак удаления элемента (0 — активен) |
| `last_update` | `data.result[].last_update` | <code>str &#124; None</code> | Нет | Дата последнего обновления записи |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Имя справочника указано с ошибкой, например `unit` вместо `Unit`.

**Что делать:** Возьмите имя из описания параметра `name` — регистр букв важен.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Неизвестный справочник"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении get_dictionary Сообщение сервера: Неизвестный справочник. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Справочники меняются редко: храните их в кэше приложения и обновляйте, например, раз в сутки, а не перед каждым запросом.
- Большие справочники (`Office`, `POIPartner`) могут превысить лимит размера JSON-ответа. Поднимите `API_MAX_JSON_RESPONSE_BYTES`, если увидите `ResponseTooLargeError`.
- Поле `data.result[].id`: число в справочнике `Services`. Тип в модели SDK: строка; число приводится к строке.
