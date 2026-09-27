---
description: "Платежи по договору: пример client.contracts.get_payments() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/contracts.yaml. Не редактируйте вручную. -->

# Платежи по договору

`client.contracts.get_payments()` · [справочник метода](../../methods/contracts.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/contracts/get_payments.py)

Получить поступившие на договор платежи с датой, суммой и назначением.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/getPayments` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Платежи по договору: client.contracts.get_payments().

Получить поступившие на договор платежи с датой, суммой и назначением.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/get_payments.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/get_payments/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.contracts.get_payments()
    for payment in response.data.result:
        print(f"{payment.date}  {payment.amount}  {payment.payment_name}")


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
| `contract_id` | `str | None` | Нет | `None` | ID контракта |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`ContractQuery`](../../data-types/request_parts/ContractQuery.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str` | Да | — | ID договора |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/getPayments?contract_id=1-2Q4CN99 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID контракта |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`PaymentsResponse`](../../data-types/contracts/PaymentsResponse.md).
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
        "id": "1334479",
        "contract_id": "1-1FLW4T7",
        "date": "2015-04-15T15:25:20",
        "amount": "10000",
        "currency": "810;RUR",
        "amount_client": "10000",
        "description": " БН00-00000250099 от 15.04.2015 15:25:14",
        "payment_name": "Payment To Client Contract",
        "payment_type": "P;Advice",
        "payment_number": "0000250099"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
2015-04-15T15:25:20  10000  Payment To Client Contract
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`PaymentsResponse`](../../data-types/contracts/PaymentsResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `PaymentsData` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`PaymentsData`](../../data-types/contracts/PaymentsData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Количество найденных платежей |
| `result` | `data.result` | `list[PaymentItem] | None` | Нет | Список платежей по договору |

#### [`PaymentItem`](../../data-types/contracts/PaymentItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `str` | Да | Идентификатор платежа |
| `contract_id` | `data.result[].contract_id` | `str` | Да | ID договора, к которому относится платёж |
| `date` | `data.result[].date` | `str` | Да | Дата и время платежа в формате ISO 8601 (например, 2015-04-15T15:25:20) |
| `amount` | `data.result[].amount` | `str` | Да | Сумма платежа в валюте договора |
| `currency` | `data.result[].currency` | `str` | Да | Код валюты и её обозначение, например '810;RUR' |
| `amount_client` | `data.result[].amount_client` | `str` | Да | Сумма, поступившая клиенту |
| `description` | `data.result[].description` | `str` | Да | Описание или назначение платежа |
| `payment_name` | `data.result[].payment_name` | `str` | Да | Наименование типа платежа, например 'Payment To Client Contract' |
| `payment_type` | `data.result[].payment_type` | `str` | Да | Тип платежа, например 'P;Advice' |
| `payment_number` | `data.result[].payment_number` | `str` | Да | Номер платёжного документа |

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_payments Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
