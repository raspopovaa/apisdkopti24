---
description: "Список продуктовых лимитов: пример client.limits.get_limits() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/limits.yaml. Не редактируйте вручную. -->

# Список продуктовых лимитов

`client.limits.get_limits()` · [справочник метода](../../methods/limits.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/limits/get_limits.py)

Получить лимиты договора, конкретной карты или группы карт: сколько можно потратить и сколько уже израсходовано за период.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/limit` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Список продуктовых лимитов: client.limits.get_limits().

Получить лимиты договора, конкретной карты или группы карт: сколько можно потратить и
сколько уже израсходовано за период.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/limits/get_limits.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/limits/get_limits/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "517945"


async def example(client: APIClient) -> None:
    response = await client.limits.get_limits(card_id=CARD_ID)
    for limit in response.data.result:
        if limit.amount is not None:
            amount = limit.amount
            print(f"{limit.id}: {amount.used} из {amount.value} {amount.unit}")


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
| `contract_id` | `str | None` | Нет | `None` | ID договора |
| `card_id` | `str | None` | Нет | `None` | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все продуктовые лимиты, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех продуктовых лимитах по карте, даже если передан ID группы карт |
| `group_id` | `str | None` | Нет | `None` | ID группы карт. Если передан ID группы карты, то будут возвращены все продуктовые лимиты указанной группы карт. Если передан ID карты и ID группы карт, то будет возвращена информация по карте |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/limit?contract_id=1-2Q4CN99&card_id=517945 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID договора |
| `card_id` | строка запроса | `517945` | string | Нет | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все продуктовые лимиты, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех продуктовых лимитах по карте, даже если передан ID группы карт |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`LimitsResponse`](../../data-types/limits/LimitsResponse.md).
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
        "id": "1-D7H3FRC",
        "card_id": "517945",
        "group_id": null,
        "contract_id": "1-B7C8D",
        "amount": {
          "value": 40,
          "used": 0,
          "unit": "LIT"
        },
        "productGroup": "1-CK235",
        "productType": "1-CK231",
        "sum": null,
        "term": {
          "days": "0000000",
          "type": 2,
          "time": {
            "from": "07:00",
            "to": "18:00"
          }
        },
        "transactions": {
          "count": 5,
          "occured": 2
        },
        "time": {
          "number": 3,
          "type": 7
        },
        "date": "09/03/2018 00:00:00"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
1-D7H3FRC: 0.0 из 40.0 LIT
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`LimitsResponse`](../../data-types/limits/LimitsResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `LimitsData` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`LimitsData`](../../data-types/limits/LimitsData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Общее количество лимитов |
| `result` | `data.result` | `list[LimitItem] | None` | Нет | Список лимитов |

#### [`LimitItem`](../../data-types/limits/LimitItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `str` | Да | ID лимита |
| `card_id` | `data.result[].card_id` | `str | None` | Нет | ID карты, если лимит задан для карты |
| `group_id` | `data.result[].group_id` | `str | None` | Нет | ID группы карт, если лимит задан для группы |
| `contract_id` | `data.result[].contract_id` | `str` | Да | ID договора, к которому относится лимит |
| `productGroup` | `data.result[].productGroup` | `str | None` | Нет | ID группы продуктов |
| `productType` | `data.result[].productType` | `str` | Да | ID типа продукта |
| `amount` | `data.result[].amount` | `LimitAmount | None` | Нет | Ограничение по объёму (литры и т.д.) |
| `sum` | `data.result[].sum` | `LimitSum | None` | Нет | Ограничение по сумме в валюте договора |
| `term` | `data.result[].term` | `LimitTerm | None` | Нет | Периодичность и временные ограничения |
| `transactions` | `data.result[].transactions` | `LimitTransactions | None` | Нет | Ограничения по количеству транзакций |
| `time` | `data.result[].time` | `LimitTime` | Да | Периодичность сброса лимита |
| `date` | `data.result[].date` | `str` | Да | Дата создания лимита (формат dd/mm/yyyy hh:mm:ss) |

#### [`LimitAmount`](../../data-types/limits/LimitAmount.md) · `data.result[].amount`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `value` | `data.result[].amount.value` | `float` | Да | Установленное значение лимита |
| `used` | `data.result[].amount.used` | `float` | Да | Использованное значение лимита |
| `unit` | `data.result[].amount.unit` | `str` | Да | Единица измерения (например, 'LIT' или 'RUB') |

#### [`LimitSum`](../../data-types/limits/LimitSum.md) · `data.result[].sum`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `currency` | `data.result[].sum.currency` | `str` | Да | Код валюты (например, 810) |
| `value` | `data.result[].sum.value` | `float` | Да | Сумма лимита |
| `used` | `data.result[].sum.used` | `float` | Да | Использованный объём лимита |

#### [`LimitTerm`](../../data-types/limits/LimitTerm.md) · `data.result[].term`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `days` | `data.result[].term.days` | `str | None` | Нет | Дни недели (например, '1111100' для Пн–Пт) |
| `type` | `data.result[].term.type` | `int` | Да | Тип периода (1 — будни, 2 — ежедневно и т.д.) |
| `time` | `data.result[].term.time` | `LimitTermTime | None` | Нет | Временной диапазон действия |

#### [`LimitTransactions`](../../data-types/limits/LimitTransactions.md) · `data.result[].transactions`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `count` | `data.result[].transactions.count` | `int` | Да | Максимальное количество транзакций |
| `occured` | `data.result[].transactions.occured` | `int` | Да | Фактическое количество транзакций |

#### [`LimitTime`](../../data-types/limits/LimitTime.md) · `data.result[].time`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `number` | `data.result[].time.number` | `int` | Да | Период в числовом виде (например, 3) |
| `type` | `data.result[].time.type` | `int` | Да | Тип периода (например, 7 — неделя) |

#### [`LimitTermTime`](../../data-types/limits/LimitTermTime.md) · `data.result[].term.time`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `from` | `data.result[].term.time.from` | `str` | Да | Время начала действия лимита (HH:MM) |
| `to` | `data.result[].term.time.to` | `str` | Да | Время окончания действия лимита (HH:MM) |

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
NotFoundError: [404] Объект или маршрут не найден при выполнении get_limits Сообщение сервера: Карта не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.limits.get_limits(card_id=CARD_ID, group_id="1-CRPDCT2")
```

Лимиты запрашиваются либо по карте, либо по группе, но не по обоим сразу. Исключение `RequestValidationError`:

```text
card_id и group_id нельзя задавать одновременно
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Без `card_id` и `group_id` метод вернёт лимиты всего договора. Передавайте только один из них.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
