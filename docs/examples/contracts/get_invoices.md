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
| `contract_id` | `str | None` | Нет | `None` | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

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
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`InvoicesResponse`](../../data-types/contracts/InvoicesResponse.md).
Пример ответа взят из спецификации API 1.1.60.

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

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`InvoicesResponse`](../../data-types/contracts/InvoicesResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `InvoicesData` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`InvoicesData`](../../data-types/contracts/InvoicesData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `total_count` | `data.total_count` | `int` | Да | uint, обязательное | Количество найденных счетов |
| `result` | `data.result` | `list[InvoiceItem] | None` | Нет | json, необязательное | Список счетов на оплату |

#### [`InvoiceItem`](../../data-types/contracts/InvoiceItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `id` | `data.result[].id` | `str` | Да | string, обязательное | Уникальный идентификатор счёта |
| `contract_id` | `data.result[].contract_id` | `str` | Да | string, обязательное | ID договора, к которому относится счёт |
| `ref_number` | `data.result[].ref_number` | `str` | Да | string, обязательное | Номер счёта, указанный в системе |
| `date_start` | `data.result[].date_start` | `str` | Да | string, обязательное | Дата начала периода счёта (YYYY-MM-DD) |
| `date_end` | `data.result[].date_end` | `int | str` | Да | uint, обязательное | Дата окончания периода счёта |
| `last_update` | `data.result[].last_update` | `float | str` | Да | float, обязательное | Дата и время последнего обновления счёта (ISO формат) |
| `currency` | `data.result[].currency` | `float | str` | Да | float, обязательное | Код валюты, например '810' |
| `amount` | `data.result[].amount` | `float | str` | Да | float, обязательное | Сумма счёта |
| `paid_amount` | `data.result[].paid_amount` | `str` | Да | string, обязательное | Оплаченная сумма |
| `status` | `data.result[].status` | `str` | Да | string, обязательное | Статус счёта, например 'OPEN' или 'PAID' |
| `comment` | `data.result[].comment` | `str | None` | Нет | string, необязательное | Комментарий к счёту, например 'Intermediate Invoice' |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

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

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Счета на оплату». Запрос в спецификации: `GET http://localhost/vip/v2/invoices`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- `contract_id` в API обязателен. Если его не передать, SDK подставит договор, выбранный при авторизации.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET: http://localhost/vip/v2/invoices
```
