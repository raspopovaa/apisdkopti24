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
CARD_ID = "900030"


async def example(client: APIClient) -> None:
    response = await client.limits.get_limits(card_id=CARD_ID)
    for limit in response.data.result or []:
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
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |
| `card_id` | <code>str &#124; None</code> | Нет | `None` | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все продуктовые лимиты, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех продуктовых лимитах по карте, даже если передан ID группы карт |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | ID группы карт. Если передан ID группы карты, то будут возвращены все продуктовые лимиты указанной группы карт. Если передан ID карты и ID группы карт, то будет возвращена информация по карте |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/limit?contract_id=1-T000025&card_id=900030 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-T000025` | string | Да | ID договора |
| `card_id` | строка запроса | `900030` | string | Нет | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все продуктовые лимиты, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех продуктовых лимитах по карте, даже если передан ID группы карт |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

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
        "id": "1-T000062",
        "w4_id": "900030",
        "card_id": "900030",
        "group_id": null,
        "contract_id": "1-T0059",
        "sum": null,
        "amount": {
          "unit": "LIT",
          "value": 40,
          "used": 0
        },
        "term": {
          "days": null,
          "type": 2,
          "time": null
        },
        "transactions": {
          "count": 5,
          "occured": 2
        },
        "time": {
          "type": 7,
          "number": "3"
        },
        "date": "09/03/2018 00:00:00",
        "productType": "1-CK231",
        "productGroup": null,
        "productTypeName": "Топливо",
        "productTypeNameNormal": "Топливо",
        "productGroupName": null
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
1-T000062: 0.0 из 40.0 LIT
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`LimitsResponse`](../../data-types/limits/LimitsResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>LimitsData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`LimitsData`](../../data-types/limits/LimitsData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Общее количество лимитов |
| `result` | `data.result` | <code>list[LimitItem] &#124; None</code> | Нет | Список лимитов |

#### [`LimitItem`](../../data-types/limits/LimitItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | ID лимита |
| `card_id` | `data.result[].card_id` | <code>str &#124; None</code> | Нет | ID карты, если лимит задан для карты |
| `group_id` | `data.result[].group_id` | <code>str &#124; None</code> | Нет | ID группы карт, если лимит задан для группы |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | ID договора, к которому относится лимит |
| `productGroup` | `data.result[].productGroup` | <code>str &#124; None</code> | Нет | ID группы продуктов |
| `productType` | `data.result[].productType` | <code>str</code> | Да | ID типа продукта |
| `amount` | `data.result[].amount` | <code>LimitAmount &#124; None</code> | Нет | Ограничение по объёму (литры и т.д.) |
| `sum` | `data.result[].sum` | <code>LimitSum &#124; None</code> | Нет | Ограничение по сумме в валюте договора |
| `term` | `data.result[].term` | <code>LimitTerm &#124; None</code> | Нет | Периодичность и временные ограничения |
| `transactions` | `data.result[].transactions` | <code>LimitTransactions &#124; None</code> | Нет | Ограничения по количеству транзакций |
| `time` | `data.result[].time` | <code>LimitTime</code> | Да | Периодичность сброса лимита |
| `date` | `data.result[].date` | <code>str</code> | Да | Дата создания лимита (MM/DD/YYYY HH:MM:SS) |

#### [`LimitAmount`](../../data-types/limits/LimitAmount.md) · `data.result[].amount`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `value` | `data.result[].amount.value` | <code>float</code> | Да | Установленное значение лимита |
| `used` | `data.result[].amount.used` | <code>float</code> | Да | Использованное значение лимита |
| `unit` | `data.result[].amount.unit` | <code>str</code> | Да | Единица измерения (например, 'LIT' или 'RUB') |

#### [`LimitSum`](../../data-types/limits/LimitSum.md) · `data.result[].sum`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `currency` | `data.result[].sum.currency` | <code>str</code> | Да | Код валюты (например, 810) |
| `value` | `data.result[].sum.value` | <code>float</code> | Да | Сумма лимита |
| `used` | `data.result[].sum.used` | <code>float</code> | Да | Использованный объём лимита |

#### [`LimitTerm`](../../data-types/limits/LimitTerm.md) · `data.result[].term`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `days` | `data.result[].term.days` | <code>str &#124; None</code> | Нет | Дни недели (например, '1111100' для Пн–Пт) |
| `type` | `data.result[].term.type` | <code>int</code> | Да | Тип периода (1 — будни, 2 — ежедневно и т.д.) |
| `time` | `data.result[].term.time` | <code>LimitTermTime &#124; None</code> | Нет | Временной диапазон действия |

#### [`LimitTransactions`](../../data-types/limits/LimitTransactions.md) · `data.result[].transactions`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `count` | `data.result[].transactions.count` | <code>int</code> | Да | Максимальное количество транзакций |
| `occured` | `data.result[].transactions.occured` | <code>int</code> | Да | Фактическое количество транзакций |

#### [`LimitTime`](../../data-types/limits/LimitTime.md) · `data.result[].time`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `number` | `data.result[].time.number` | <code>int</code> | Да | Число периодов; API присылает строку, SDK приводит её к int |
| `type` | `data.result[].time.type` | <code>int</code> | Да | Тип периода (например, 7 — неделя) |

#### [`LimitTermTime`](../../data-types/limits/LimitTermTime.md) · `data.result[].term.time`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `from` | `data.result[].term.time.from` | <code>str</code> | Да | Время начала действия лимита (HH:MM) |
| `to` | `data.result[].term.time.to` | <code>str</code> | Да | Время окончания действия лимита (HH:MM) |

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
await client.limits.get_limits(card_id=CARD_ID, group_id="1-T000061")
```

Лимиты запрашиваются либо по карте, либо по группе, но не по обоим сразу. Исключение `RequestValidationError`:

```text
card_id и group_id нельзя задавать одновременно
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Без `card_id` и `group_id` метод вернёт лимиты всего договора. Передавайте только один из них.
- `date` приходит в формате `MM/DD/YYYY HH:MM:SS` — месяц идёт первым.
- `time.number` API присылает строкой; SDK приводит его к `int`.
- API присылает также `w4_id`, `productTypeName`, `productTypeNameNormal` и `productGroupName`; в модели SDK их нет, они доступны через `limit.model_extra`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
