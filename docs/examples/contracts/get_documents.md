---
description: "Закрывающие документы: пример client.contracts.get_documents() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/contracts.yaml. Не редактируйте вручную. -->

# Закрывающие документы

`client.contracts.get_documents()` · [справочник метода](../../methods/contracts.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/contracts/get_documents.py)

Получить документы договора за период: УПД, акты и другие, с номером, датой и суммой.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/documents` | Нет | Нет | Нет | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Закрывающие документы: client.contracts.get_documents().

Получить документы договора за период: УПД, акты и другие, с номером, датой и суммой.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/get_documents.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/get_documents/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.contracts.get_documents(
        date_start="2026-08-01", date_end="2026-08-31", page=1, on_page=20
    )
    print(f"Документов за период: {response.data.total_count}")
    for document in response.data.result or []:
        print(f"{document.name} № {document.number}: {document.sum}")


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
| `date_start` | <code>str</code> | Да | — | Дата начала периода в формате `YYYY-MM-DD`. |
| `date_end` | <code>str</code> | Да | — | Дата окончания периода в формате `YYYY-MM-DD`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `page` | <code>int</code> | Нет | `1` | Номер страницы (Пагинация) |
| `on_page` | <code>int</code> | Нет | `10` | Количество элементов на странице. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`DateRangePaginationQuery`](../../data-types/request_parts/DateRangePaginationQuery.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `date_start` | <code>str</code> | Да | — | Дата начала периода в формате YYYY-MM-DD |
| `date_end` | <code>str</code> | Да | — | Дата окончания периода в формате YYYY-MM-DD |
| `page` | <code>int</code> | Нет | — | Номер страницы |
| `on_page` | <code>int</code> | Нет | — | Количество элементов на странице |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/documents?date_start=2026-08-01&date_end=2026-08-31&page=1&on_page=20 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `date_start` | строка запроса | `2026-08-01` | string | Да | Дата начала периода (Формат: 2019-01-01) |
| `date_end` | строка запроса | `2026-08-31` | string | Да | Дата окончания периода (Формат: 2020-01-01) |
| `page` | строка запроса | `1` | string | Нет | Номер страницы (Пагинация) |
| `on_page` | строка запроса | `20` | string | Нет | Элементов на странице (Пагинация) |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`DocumentsResponse`](../../data-types/contracts/DocumentsResponse.md).
Пример ответа; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 14,
    "result": [
      {
        "id": "a9a866ae-9d23-11e9-8120-005056a969a3",
        "name": "УПД",
        "name_doc": "СчетФактураВыданный",
        "number": "CSC0000000533998",
        "date": 1561928399,
        "total": 1610393.25,
        "vat": 268398.88,
        "sum": 1341994.37,
        "currency": "руб.",
        "consignee": "СПТ ООО",
        "contract_id": "1-T0057",
        "contract_name": "ЯР014005482"
      },
      {
        "id": "6fffd550-b55f-11e9-8123-005056a969a3",
        "name": "УПД",
        "name_doc": "СчетФактураВыданный",
        "number": "CSC0000000627192",
        "date": 1564606799,
        "total": 1983746.48,
        "vat": 330624.41,
        "sum": 1653122.07,
        "currency": "руб.",
        "consignee": "СПТ ООО",
        "contract_id": "1-T0057",
        "contract_name": "ЯР014005482"
      }
    ]
  },
  "timestamp": 1591144445
}
```

Вывод примера на этом ответе:

```text
Документов за период: 14
УПД № CSC0000000533998: 1341994.37
УПД № CSC0000000627192: 1653122.07
УПД № CSC0000000668808: 51950.56
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`DocumentsResponse`](../../data-types/contracts/DocumentsResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>DocumentsData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`DocumentsData`](../../data-types/contracts/DocumentsData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество найденных документов |
| `result` | `data.result` | <code>list[DocumentItem] &#124; None</code> | Нет | Список найденных документов |

#### [`DocumentItem`](../../data-types/contracts/DocumentItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Уникальный идентификатор документа (UUID) |
| `name` | `data.result[].name` | <code>str</code> | Да | Название документа, например 'УПД' |
| `name_doc` | `data.result[].name_doc` | <code>str &#124; None</code> | Нет | Системное имя документа, например 'СчетФактураВыданный' |
| `number` | `data.result[].number` | <code>str</code> | Да | Номер документа, например 'CSC0000000533998' |
| `date` | `data.result[].date` | <code>int</code> | Да | Дата документа в формате UNIX timestamp |
| `total` | `data.result[].total` | <code>float</code> | Да | Общая сумма документа |
| `vat` | `data.result[].vat` | <code>float</code> | Да | Сумма НДС |
| `sum` | `data.result[].sum` | <code>float</code> | Да | Сумма без НДС |
| `currency` | `data.result[].currency` | <code>str</code> | Да | Валюта документа, например 'руб.' |
| `consignee` | `data.result[].consignee` | <code>str &#124; None</code> | Нет | Грузополучатель (организация) |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | ID договора, к которому относится документ |
| `contract_name` | `data.result[].contract_name` | <code>str</code> | Да | Номер или название договора |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Пользователь API не имеет доступа к документам договора.

**Что делать:** Проверьте права пользователя.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Нет доступа к документам"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_documents Сообщение сервера: Нет доступа к документам. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.contracts.get_documents(date_start="2026-08-31", date_end="2026-08-01")
```

Дата окончания не может быть раньше даты начала. Исключение `RequestValidationError`:

```text
date_end не может предшествовать date_start
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Даты передаются в формате `YYYY-MM-DD`. SDK проверяет формат и порядок дат до отправки запроса.
- Поле `date` в ответе — время в формате Unix (секунды), а не строка.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
