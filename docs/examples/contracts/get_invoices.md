---
description: "Счета на оплату: пример client.contracts.get_invoices() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/contracts.yaml. Не редактируйте вручную. -->

# Счета на оплату

`client.contracts.get_invoices()` · [справочник метода](../../methods/contracts.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/contracts/get_invoices.py)

Получить выставленные счета с суммой, оплаченной частью и статусом.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/invoices` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Счета на оплату: client.contracts.get_invoices().

Получить выставленные счета с суммой, оплаченной частью и статусом.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/get_invoices.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/get_invoices/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.contracts.get_invoices()
    for invoice in response.data.result:
        print(f"Счёт {invoice.ref_number}: {invoice.amount}, оплачено {invoice.paid_amount}")


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
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/invoices HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`InvoicesResponse`](../../data-types/contracts/InvoicesResponse.md).
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
        "id": "543845",
        "contract_id": "5960523",
        "ref_number": "201903160025051725914",
        "date_start": "2019-03-16",
        "date_end": "2019-04-14",
        "last_update": "2019-03-16T00:25:05",
        "currency": "810",
        "amount": "10064360.84",
        "paid_amount": "0",
        "status": "OPEN",
        "comment": "Intermediate Invoice"
      }
    ]
  },
  "timestamp": 1591144445
}
```

Вывод примера на этом ответе:

```text
Счёт 201903160025051725914: 10064360.84, оплачено 0
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`InvoicesResponse`](../../data-types/contracts/InvoicesResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>InvoicesData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`InvoicesData`](../../data-types/contracts/InvoicesData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество найденных счетов |
| `result` | `data.result` | <code>list[InvoiceItem] &#124; None</code> | Нет | Список счетов на оплату |

#### [`InvoiceItem`](../../data-types/contracts/InvoiceItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Уникальный идентификатор счёта |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | ID договора, к которому относится счёт |
| `ref_number` | `data.result[].ref_number` | <code>str</code> | Да | Номер счёта, указанный в системе |
| `date_start` | `data.result[].date_start` | <code>str</code> | Да | Дата начала периода счёта (YYYY-MM-DD) |
| `date_end` | `data.result[].date_end` | <code>int &#124; str</code> | Да | Дата окончания периода счёта |
| `last_update` | `data.result[].last_update` | <code>float &#124; str</code> | Да | Дата и время последнего обновления счёта (ISO формат) |
| `currency` | `data.result[].currency` | <code>float &#124; str</code> | Да | Код валюты, например '810' |
| `amount` | `data.result[].amount` | <code>float &#124; str</code> | Да | Сумма счёта |
| `paid_amount` | `data.result[].paid_amount` | <code>str</code> | Да | Оплаченная сумма |
| `status` | `data.result[].status` | <code>str</code> | Да | Статус счёта, например 'OPEN' или 'PAID' |
| `comment` | `data.result[].comment` | <code>str &#124; None</code> | Нет | Комментарий к счёту, например 'Intermediate Invoice' |

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_invoices Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
- Поле `data.result[].amount`, `currency`, `date_end`, `last_update`: строки. Тип в модели SDK: <code>float &#124; str</code>, <code>int &#124; str</code>.
