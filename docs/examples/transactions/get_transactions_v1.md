---
description: "Последние транзакции (API v1): пример client.transactions.get_transactions_v1() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/transactions.yaml. Не редактируйте вручную. -->

# Последние транзакции (API v1)

`client.transactions.get_transactions_v1()` · [справочник метода](../../methods/transactions.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/transactions/get_transactions_v1.py)

Получить последние транзакции договора или карты через первую версию API. Для выгрузки за период удобнее `get_transactions_v2`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/transactions` | Нет | Да | Нет | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Последние транзакции (API v1): client.transactions.get_transactions_v1().

Получить последние транзакции договора или карты через первую версию API. Для выгрузки
за период удобнее `get_transactions_v2`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/transactions/get_transactions_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/transactions/get_transactions_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.transactions.get_transactions_v1(count=20)
    for item in response.data.result:
        print(f"{item.time}  карта {item.card_number}  стоимость {item.cost}")


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
| `contract_id` | `str | None` | Нет | `None` | ID договора |
| `card_id` | `str | None` | Нет | `None` | ID карты |
| `count` | `int` | Нет | `20` | Количество транзакций (если не указывать, то вернется 10 последних транзакций) |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `filter_fn` | `Callable[[<class 'apisdkopti24.models.transactions.TransactionV1'>], bool] | None` | Нет | `None` | — |
| `sort_by` | `str | None` | Нет | `None` | — |
| `reverse` | `bool` | Нет | `False` | — |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`TransactionV1`](../../data-types/transactions/TransactionV1.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | `str` | Да | — | ID транзакции |
| `time` | `datetime` | Да | формат: 'date-time' | Дата и время транзакции |
| `host_date` | `datetime` | Да | формат: 'date-time' | Дата и время на хосте |
| `currency` | `str` | Да | — | Код валюты (например, 810) |
| `card_id` | `str` | Да | — | ID карты |
| `service_center` | `str | None` | Нет | — | ID сервисного центра (АЗС) |
| `card_number` | `str` | Да | — | Номер карты |
| `base_cost` | `str` | Да | — | Базовая стоимость транзакции |
| `cost` | `str` | Да | — | Фактическая стоимость с учётом скидок |
| `discount` | `str` | Да | — | Размер скидки |
| `discount_cost` | `str` | Да | — | Стоимость после применения скидки |
| `incoming` | `bool` | Да | — | Признак входящей транзакции |
| `request` | `RequestInfo` | Да | — | Информация о типе операции |
| `transaction_items` | `list[TransactionItem] | None` | Нет | — | Список товаров в транзакции |

#### [`RequestInfo`](../../data-types/transactions/RequestInfo.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `type` | `str` | Да | — | Тип операции (например, Advice) |
| `name` | `str` | Да | — | Название операции (например, Покупка) |

#### [`TransactionItem`](../../data-types/transactions/TransactionItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | `str` | Да | — | ID позиции транзакции |
| `rrn` | `str` | Да | — | Уникальный номер RRN |
| `product` | `str` | Да | — | Наименование продукта (топлива) |
| `amount` | `str` | Да | — | Количество продукта |
| `price` | `str` | Да | — | Цена за единицу |
| `base_cost` | `str` | Да | — | Базовая стоимость |
| `cost` | `str` | Да | — | Итоговая стоимость с учетом скидки |
| `discount` | `str` | Да | — | Скидка по позиции |
| `discount_cost` | `str` | Да | — | Стоимость с учётом скидки |
| `transaction` | `str` | Да | — | ID транзакции |
| `currency` | `str` | Да | — | Валюта |
| `unit` | `str` | Да | — | Единица измерения |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/transactions?contract_id=1-2Q4CN99&count=20 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID договора |
| `count` | строка запроса | `20` | string | Нет | Количество транзакций (если не указывать, то вернется 10 последних транзакций) |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TransactionsV1Response`](../../data-types/transactions/TransactionsV1Response.md).
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
        "id": "3862340995",
        "time": "2018-11-20 07:41:11",
        "host_date": "2018-11-12 12:38:52",
        "currency": "810",
        "card_id": "79000001",
        "service_center": "8807238",
        "card_number": "7000000000000000",
        "base_cost": "1526",
        "cost": "1526",
        "discount": "-50.1",
        "discount_cost": "1576.1",
        "incoming": true,
        "request": {
          "type": "Advice",
          "name": "Покупка"
        },
        "transaction_items": [
          {
            "id": "3862340993",
            "rrn": "6286077679996",
            "product": "Аи-92",
            "amount": "20",
            "price": "33.2",
            "base_cost": "664",
            "cost": "664",
            "discount": "-21.6",
            "discount_cost": "685.6",
            "transaction": "3862340995",
            "currency": "810",
            "unit": "LIT"
          },
          {
            "id": "3862340994",
            "rrn": "6286077679774",
            "product": "Аи-95",
            "amount": "20",
            "price": "43.1",
            "base_cost": "862",
            "cost": "862",
            "discount": "-28.5",
            "discount_cost": "890.5",
            "transaction": "3862340995",
            "currency": "810",
            "unit": "LIT"
          }
        ]
      },
      {
        "id": "3862340837",
        "time": "2018-11-12 09:38:52",
        "host_date": "2018-11-12 12:38:52",
        "currency": "810",
        "card_id": "79000003",
        "service_center": "8807238",
        "card_number": "7000000000000000",
        "base_cost": "962.8",
        "cost": "962.8",
        "discount": "0",
        "discount_cost": "962.8",
        "incoming": true,
        "request": {
          "type": "Advice",
          "name": "Покупка"
        },
        "transaction_items": [
          {
            "id": "3862340838",
            "rrn": "6286077679885",
            "product": "Аи-95",
            "amount": "29",
            "price": "33.2",
            "base_cost": "962.8",
            "cost": "962.8",
            "discount": "0",
            "discount_cost": "962.8",
            "transaction": "3862340837",
            "currency": "810",
            "unit": "LIT"
          }
        ]
      }
    ]
  },
  "timestamp": 1596075915
}
```

Вывод примера на этом ответе:

```text
2018-11-20 07:41:11  карта 7000000000000000  стоимость 1526
2018-11-12 09:38:52  карта 7000000000000000  стоимость 962.8
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TransactionsV1Response`](../../data-types/transactions/TransactionsV1Response.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `TransactionsV1Data` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`TransactionsV1Data`](../../data-types/transactions/TransactionsV1Data.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Общее количество транзакций |
| `result` | `data.result` | `list[TransactionV1] | None` | Нет | Список транзакций |

#### [`TransactionV1`](../../data-types/transactions/TransactionV1.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `str` | Да | ID транзакции |
| `time` | `data.result[].time` | `datetime` | Да | Дата и время транзакции |
| `host_date` | `data.result[].host_date` | `datetime` | Да | Дата и время на хосте |
| `currency` | `data.result[].currency` | `str` | Да | Код валюты (например, 810) |
| `card_id` | `data.result[].card_id` | `str` | Да | ID карты |
| `service_center` | `data.result[].service_center` | `str | None` | Нет | ID сервисного центра (АЗС) |
| `card_number` | `data.result[].card_number` | `str` | Да | Номер карты |
| `base_cost` | `data.result[].base_cost` | `str` | Да | Базовая стоимость транзакции |
| `cost` | `data.result[].cost` | `str` | Да | Фактическая стоимость с учётом скидок |
| `discount` | `data.result[].discount` | `str` | Да | Размер скидки |
| `discount_cost` | `data.result[].discount_cost` | `str` | Да | Стоимость после применения скидки |
| `incoming` | `data.result[].incoming` | `bool` | Да | Признак входящей транзакции |
| `request` | `data.result[].request` | `RequestInfo` | Да | Информация о типе операции |
| `transaction_items` | `data.result[].transaction_items` | `list[TransactionItem] | None` | Нет | Список товаров в транзакции |

#### [`RequestInfo`](../../data-types/transactions/RequestInfo.md) · `data.result[].request`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `type` | `data.result[].request.type` | `str` | Да | Тип операции (например, Advice) |
| `name` | `data.result[].request.name` | `str` | Да | Название операции (например, Покупка) |

#### [`TransactionItem`](../../data-types/transactions/TransactionItem.md) · `data.result[].transaction_items[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].transaction_items[].id` | `str` | Да | ID позиции транзакции |
| `rrn` | `data.result[].transaction_items[].rrn` | `str` | Да | Уникальный номер RRN |
| `product` | `data.result[].transaction_items[].product` | `str` | Да | Наименование продукта (топлива) |
| `amount` | `data.result[].transaction_items[].amount` | `str` | Да | Количество продукта |
| `price` | `data.result[].transaction_items[].price` | `str` | Да | Цена за единицу |
| `base_cost` | `data.result[].transaction_items[].base_cost` | `str` | Да | Базовая стоимость |
| `cost` | `data.result[].transaction_items[].cost` | `str` | Да | Итоговая стоимость с учетом скидки |
| `discount` | `data.result[].transaction_items[].discount` | `str` | Да | Скидка по позиции |
| `discount_cost` | `data.result[].transaction_items[].discount_cost` | `str` | Да | Стоимость с учётом скидки |
| `transaction` | `data.result[].transaction_items[].transaction` | `str` | Да | ID транзакции |
| `currency` | `data.result[].transaction_items[].currency` | `str` | Да | Валюта |
| `unit` | `data.result[].transaction_items[].unit` | `str` | Да | Единица измерения |

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_transactions_v1 Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.transactions.get_transactions_v1(count=0)
```

Количество транзакций должно быть больше нуля. Исключение `RequestValidationError`:

```text
count должен быть больше нуля
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Ответ содержит номер карты (`card_number`). Не выводите его в журналы целиком.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
