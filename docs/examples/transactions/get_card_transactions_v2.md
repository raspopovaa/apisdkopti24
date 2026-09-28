---
description: "Транзакции карты за период: пример client.transactions.get_card_transactions_v2() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/transactions.yaml. Не редактируйте вручную. -->

# Транзакции карты за период

`client.transactions.get_card_transactions_v2()` · [справочник метода](../../methods/transactions.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/transactions/get_card_transactions_v2.py)

Получить операции одной карты за период с товарами, ценами и суммами.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/cards/{card_id}/transactions` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Транзакции карты за период: client.transactions.get_card_transactions_v2().

Получить операции одной карты за период с товарами, ценами и суммами.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/transactions/get_card_transactions_v2.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/transactions/get_card_transactions_v2/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "15844989"


async def example(client: APIClient) -> None:
    response = await client.transactions.get_card_transactions_v2(
        card_id=CARD_ID, date_from="2026-09-01", date_to="2026-09-30"
    )
    for item in response.data.result:
        print(f"{item.timestamp}  {item.product_name}  {item.qty}  {item.sum}")


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
| `card_id` | `str` | Да | — | ID карты |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `date_from` | `str` | Да | — | Начало периода транзакций |
| `date_to` | `str` | Да | — | Окончание периода транзакций |
| `page_limit` | `int` | Нет | `100` | Количество транзакций на странице. |
| `page_offset` | `int` | Нет | `0` | Количество транзакций, которые нужно пропустить. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `filter_fn` | `Callable[[<class 'apisdkopti24.models.transactions.TransactionItemV2'>], bool] | None` | Нет | `None` | — |
| `sort_by` | `str | None` | Нет | `None` | — |
| `reverse` | `bool` | Нет | `False` | — |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`TransactionItemV2`](../../data-types/transactions/TransactionItemV2.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | `int | str` | Да | — | ID транзакции |
| `timestamp` | `datetime` | Да | формат: 'date-time' | Местное время транзакции. Строка оканчивается на Z, но время не UTC: SDK разбирает его как UTC, поэтому не используйте tzinfo этого поля |
| `utc_time` | `datetime` | Да | формат: 'date-time' | Время транзакции в UTC |
| `card_id` | `str` | Да | — | ID карты |
| `poi_id` | `str` | Да | — | ID точки продаж (АЗС) |
| `terminal_id` | `str` | Да | — | ID терминала |
| `type` | `str` | Да | — | Тип операции (P — покупка, R — возврат) |
| `product_id` | `str` | Да | — | ID продукта |
| `product_name` | `str` | Да | — | Наименование продукта |
| `product_category_id` | `str` | Да | — | Категория продукта (например, НП) |
| `currency` | `str` | Да | — | Код валюты (например, RUR) |
| `check_id` | `int | str` | Да | — | Номер чека |
| `stor_transaction_id` | `int | str | None` | Да | — | ID сторнируемой транзакции |
| `is_storno` | `bool` | Да | — | Признак сторно |
| `is_manual_correction` | `bool` | Да | — | Признак ручной корректировки |
| `qty` | `int | float` | Да | — | Количество |
| `price` | `float | str` | Да | — | Цена за единицу |
| `price_no_discount` | `float | str` | Да | — | Цена без скидки |
| `sum` | `float | str` | Да | — | Сумма с учетом скидки |
| `sum_no_discount` | `float | str` | Да | — | Сумма без скидки |
| `discount` | `float | str` | Да | — | Размер скидки |
| `exchange_rate` | `float | str` | Да | — | Курс обмена |
| `card_number` | `str` | Да | — | Номер карты |
| `payment_type` | `str` | Да | — | Тип оплаты (например, Карта) |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/cards/15844989/transactions?contract_id=1-2Q4CN99&date_from=2026-09-01&date_to=2026-09-30&page_limit=100&page_offset=0 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `15844989` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `contract_id` | строка запроса | `1-2Q4CN99` | string | — | — |
| `date_from` | строка запроса | `2026-09-01` | string | Да | Начало периода транзакций |
| `date_to` | строка запроса | `2026-09-30` | string | Да | Окончание периода транзакций |
| `page_limit` | строка запроса | `100` | string | Нет | Количество транзакций на странице. 500, если не указано. |
| `page_offset` | строка запроса | `0` | string | Нет | Количество транзакций, которые пропускаются |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TransactionsV2Response`](../../data-types/transactions/TransactionsV2Response.md).
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
        "id": 9281938435,
        "timestamp": "2002-11-28T00:10:00.000000Z",
        "utc_time": "2002-11-27T22:10:00.000000Z",
        "card_id": "15844989",
        "poi_id": "1-3GQFQPF",
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
        "qty": 53.1,
        "price": 54.9,
        "price_no_discount": 52.79,
        "sum": 2915.19,
        "sum_no_discount": 2803.15,
        "discount": 112.04,
        "exchange_rate": 1,
        "card_number": "7000000000000000",
        "payment_type": "Карта"
      },
      {
        "id": 9281938437,
        "timestamp": "2002-11-28T00:10:00.000000Z",
        "utc_time": "2002-11-27T22:10:00.000000Z",
        "card_id": "15844990",
        "poi_id": "1-3GQFQPF",
        "terminal_id": "RZ142481",
        "type": "R",
        "product_id": "00000000000003",
        "product_name": "Аи-95",
        "product_category_id": "НП",
        "currency": "RUR",
        "check_id": 127523194203,
        "stor_transaction_id": 9271461749,
        "is_storno": true,
        "is_manual_corrention": false,
        "qty": -11.5,
        "price": 43.38,
        "price_no_discount": 46.7,
        "sum": -598.64,
        "sum_no_discount": -644.46,
        "discount": -45.82,
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
2002-11-28 00:10:00+00:00  Аи-95  53.1  2915.19
2002-11-28 00:10:00+00:00  Аи-95  -11.5  -598.64
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TransactionsV2Response`](../../data-types/transactions/TransactionsV2Response.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `TransactionsV2Data` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`TransactionsV2Data`](../../data-types/transactions/TransactionsV2Data.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Общее количество транзакций |
| `result` | `data.result` | `list[TransactionItemV2] | None` | Нет | Список транзакций (v2) |

#### [`TransactionItemV2`](../../data-types/transactions/TransactionItemV2.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `int | str` | Да | ID транзакции |
| `timestamp` | `data.result[].timestamp` | `datetime` | Да | Местное время транзакции. Строка оканчивается на Z, но время не UTC: SDK разбирает его как UTC, поэтому не используйте tzinfo этого поля |
| `utc_time` | `data.result[].utc_time` | `datetime` | Да | Время транзакции в UTC |
| `card_id` | `data.result[].card_id` | `str` | Да | ID карты |
| `poi_id` | `data.result[].poi_id` | `str` | Да | ID точки продаж (АЗС) |
| `terminal_id` | `data.result[].terminal_id` | `str` | Да | ID терминала |
| `type` | `data.result[].type` | `str` | Да | Тип операции (P — покупка, R — возврат) |
| `product_id` | `data.result[].product_id` | `str` | Да | ID продукта |
| `product_name` | `data.result[].product_name` | `str` | Да | Наименование продукта |
| `product_category_id` | `data.result[].product_category_id` | `str` | Да | Категория продукта (например, НП) |
| `currency` | `data.result[].currency` | `str` | Да | Код валюты (например, RUR) |
| `check_id` | `data.result[].check_id` | `int | str` | Да | Номер чека |
| `stor_transaction_id` | `data.result[].stor_transaction_id` | `int | str | None` | Да | ID сторнируемой транзакции |
| `is_storno` | `data.result[].is_storno` | `bool` | Да | Признак сторно |
| `is_manual_correction` | `data.result[].is_manual_correction` | `bool` | Да | Признак ручной корректировки |
| `qty` | `data.result[].qty` | `int | float` | Да | Количество |
| `price` | `data.result[].price` | `float | str` | Да | Цена за единицу |
| `price_no_discount` | `data.result[].price_no_discount` | `float | str` | Да | Цена без скидки |
| `sum` | `data.result[].sum` | `float | str` | Да | Сумма с учетом скидки |
| `sum_no_discount` | `data.result[].sum_no_discount` | `float | str` | Да | Сумма без скидки |
| `discount` | `data.result[].discount` | `float | str` | Да | Размер скидки |
| `exchange_rate` | `data.result[].exchange_rate` | `float | str` | Да | Курс обмена |
| `card_number` | `data.result[].card_number` | `str` | Да | Номер карты |
| `payment_type` | `data.result[].payment_type` | `str` | Да | Тип оплаты (например, Карта) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Карты с таким `card_id` нет в выбранном договоре.

**Что делать:** Возьмите `id` карты из `client.cards.get_cards_v2()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Карта не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении get_card_transactions_v2 Сообщение сервера: Карта не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.transactions.get_card_transactions_v2(card_id=CARD_ID, date_from="01.09.2026", date_to="30.09.2026")
```

Даты передаются в формате `YYYY-MM-DD`. Исключение `RequestValidationError`:

```text
Даты должны иметь формат ISO YYYY-MM-DD
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Ограничения периода и постраничного вывода те же, что у `get_transactions_v2`.
- `timestamp` — местное время транзакции, хотя строка оканчивается на `Z`; время в UTC — в `utc_time`. SDK разбирает `timestamp` как UTC, поэтому не используйте его часовой пояс: берите `utc_time` или отбрасывайте `tzinfo`.
- Признак ручной корректировки API присылает под именем `is_manual_corrention`; в модели SDK поле называется `is_manual_correction`.
- Поле `data.result[].stor_transaction_id`: `null` у несторнированных транзакций. Тип в модели SDK: `int | str | None`.
- Поле `data.result[].timestamp`: местное время со суффиксом `Z`. Тип в модели SDK: `datetime` с часовым поясом UTC; используйте `utc_time`.
