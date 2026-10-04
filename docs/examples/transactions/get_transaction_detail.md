---
description: "Детали транзакции: пример client.transactions.get_transaction_detail() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/transactions.yaml. Не редактируйте вручную. -->

# Детали транзакции

`client.transactions.get_transaction_detail()` · [справочник метода](../../methods/transactions.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/transactions/get_transaction_detail.py)

Получить подробности одной транзакции по её ID: точку обслуживания, товар, цену до и после скидки.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/transactions/{transaction_id}` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Детали транзакции: client.transactions.get_transaction_detail().

Получить подробности одной транзакции по её ID: точку обслуживания, товар, цену до и
после скидки.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/transactions/get_transaction_detail.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/transactions/get_transaction_detail/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TRANSACTION_ID = "9000000041"


async def example(client: APIClient) -> None:
    response = await client.transactions.get_transaction_detail(transaction_id=TRANSACTION_ID)
    for item in response.data.result:
        print(f"{item.product_name}: {item.qty} по {item.price}, скидка {item.discount}")


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
| `transaction_id` | <code>str</code> | Да | — | ID транзакции |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`ContractQuery`](../../data-types/request_parts/ContractQuery.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str</code> | Да | — | ID договора |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/transactions/9000000041?contract_id=1-T000025 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `transaction_id` | путь | `9000000041` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `contract_id` | строка запроса | `1-T000025` | string | — | — |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TransactionDetailResponse`](../../data-types/transactions/TransactionDetailResponse.md).
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
        "id": 9000000041,
        "timestamp": "2002-11-28T00:10:00.000000Z",
        "utc_time": "2002-11-27T22:10:00.000000Z",
        "card_id": "90000010",
        "poi_id": "1-T000052",
        "terminal_id": "RZ142481",
        "type": "P",
        "product_id": "00000000000003",
        "product_name": "Аи-95",
        "product_category_id": "НП",
        "currency": "RUR",
        "check_id": 127523194203,
        "stor_transaction_id": null,
        "is_storno": false,
        "is_manual_corrention": false,
        "qty": 11.5,
        "price": 43.38,
        "price_no_discount": 46.7,
        "sum": 598.64,
        "sum_no_discount": 644.46,
        "discount": 45.82,
        "exchange_rate": 1,
        "card_number": "7000000000000000",
        "payment_type": "Карта"
      }
    ]
  },
  "timestamp": 1596075915
}
```

Вывод примера на этом ответе:

```text
Аи-95: 11.5 по 43.38, скидка 45.82
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TransactionDetailResponse`](../../data-types/transactions/TransactionDetailResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>TransactionDetailData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`TransactionDetailData`](../../data-types/transactions/TransactionDetailData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Общее количество транзакций |
| `result` | `data.result` | <code>list[TransactionDetailItem] &#124; None</code> | Нет | Детали транзакции |

#### [`TransactionDetailItem`](../../data-types/transactions/TransactionDetailItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>int &#124; str</code> | Да | ID транзакции |
| `timestamp` | `data.result[].timestamp` | <code>datetime</code> | Да | Местное время транзакции. Строка оканчивается на Z, но время не UTC: SDK разбирает его как UTC, поэтому не используйте tzinfo этого поля |
| `utc_time` | `data.result[].utc_time` | <code>datetime</code> | Да | Время транзакции в UTC |
| `card_id` | `data.result[].card_id` | <code>str</code> | Да | ID карты |
| `poi_id` | `data.result[].poi_id` | <code>str</code> | Да | ID точки продаж (АЗС) |
| `terminal_id` | `data.result[].terminal_id` | <code>str</code> | Да | ID терминала |
| `type` | `data.result[].type` | <code>str</code> | Да | Тип операции (P — покупка, R — возврат) |
| `product_id` | `data.result[].product_id` | <code>str</code> | Да | ID продукта |
| `product_name` | `data.result[].product_name` | <code>str</code> | Да | Наименование продукта |
| `product_category_id` | `data.result[].product_category_id` | <code>str</code> | Да | Категория продукта (например, НП) |
| `currency` | `data.result[].currency` | <code>str</code> | Да | Код валюты (например, RUR) |
| `check_id` | `data.result[].check_id` | <code>int &#124; str</code> | Да | Номер чека |
| `stor_transaction_id` | `data.result[].stor_transaction_id` | <code>int &#124; str &#124; None</code> | Да | ID сторнируемой транзакции |
| `is_storno` | `data.result[].is_storno` | <code>bool</code> | Да | Признак сторно |
| `is_manual_correction` | `data.result[].is_manual_correction` | <code>bool</code> | Да | Признак ручной корректировки |
| `qty` | `data.result[].qty` | <code>int &#124; float</code> | Да | Количество |
| `price` | `data.result[].price` | <code>float &#124; str</code> | Да | Цена за единицу |
| `price_no_discount` | `data.result[].price_no_discount` | <code>float &#124; str</code> | Да | Цена без скидки |
| `sum` | `data.result[].sum` | <code>float &#124; str</code> | Да | Сумма с учетом скидки |
| `sum_no_discount` | `data.result[].sum_no_discount` | <code>float &#124; str</code> | Да | Сумма без скидки |
| `discount` | `data.result[].discount` | <code>float &#124; str</code> | Да | Размер скидки |
| `exchange_rate` | `data.result[].exchange_rate` | <code>float &#124; str</code> | Да | Курс обмена |
| `card_number` | `data.result[].card_number` | <code>str</code> | Да | Номер карты |
| `payment_type` | `data.result[].payment_type` | <code>str</code> | Да | Тип оплаты (например, Карта) |
| `date` | `data.result[].date` | <code>str &#124; None</code> | Нет | Дата транзакции |

## Ошибки

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.transactions.get_transaction_detail(transaction_id="")
```

Пустой `transaction_id` отклоняется до отправки запроса. Исключение `RequestValidationError`:

```text
transaction_id: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `timestamp` — местное время транзакции, хотя строка оканчивается на `Z`; время в UTC — в `utc_time`. SDK разбирает `timestamp` как UTC, поэтому не используйте его часовой пояс: берите `utc_time` или отбрасывайте `tzinfo`.
- Признак ручной корректировки API присылает под именем `is_manual_corrention`; в модели SDK поле называется `is_manual_correction`.
- Для несуществующего ID API не возвращает ошибку: ответ успешный, с `total_count: 0` и пустым `result`. Проверяйте `total_count`, а не перехватывайте `NotFoundError`.
- Поле `data.result[].stor_transaction_id`: `null` у несторнированных транзакций. Тип в модели SDK: <code>int &#124; str &#124; None</code>.
- Поле `data.result[].date`: поле не приходит. Тип в модели SDK: <code>str &#124; None</code>, по умолчанию `None`.
- Поле `data.result[].timestamp`: местное время со суффиксом `Z`. Тип в модели SDK: `datetime` с часовым поясом UTC; используйте `utc_time`.
- Поле `data.result[].id`, `check_id`: числа. Тип в модели SDK: <code>int &#124; str</code>.
- Поле `data.result[].price`, `sum`, `price_no_discount`, `sum_no_discount`, `discount`, `exchange_rate`, `qty`: числа, в том числе дробные. Тип в модели SDK: числа или строки.
