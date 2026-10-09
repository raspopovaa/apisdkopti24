---
description: "Лимиты шаблона: пример client.templates.get_template_limits() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Лимиты шаблона

`client.templates.get_template_limits()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/get_template_limits.py)

Получить лимиты, которые получат карты, выпущенные по шаблону.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/vc/templates/{template_id}/limits` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Лимиты шаблона: client.templates.get_template_limits().

Получить лимиты, которые получат карты, выпущенные по шаблону.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/get_template_limits.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/get_template_limits/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000043"


async def example(client: APIClient) -> None:
    response = await client.templates.get_template_limits(template_id=TEMPLATE_ID)
    for limit in response.data.result or []:
        if limit.amount is not None:
            print(f"{limit.id}: {limit.productTypeName} — {limit.amount.value} {limit.amount.unit}")


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
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/vc/templates/1-T000043/limits HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-T000043` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateLimitListResponse`](../../data-types/templates/TemplateLimitListResponse.md).
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
        "term": {
          "days": null,
          "time": null,
          "type": 1
        },
        "transactions": {
          "count": 0
        },
        "template_id": "1-T000043",
        "contract_id": "1-T000036",
        "id": "1-T000044",
        "amount": {
          "unit": "LIT",
          "value": 3000
        },
        "sum": null,
        "time": {
          "type": 5,
          "number": "1"
        },
        "date": "12/17/2019 13:07:17",
        "productType": "1-276PF01",
        "productGroup": "1-276PF0E",
        "productTypeName": "Топливо",
        "productTypeNameNormal": "Топливо",
        "productGroupName": "G-95"
      },
      {
        "term": {
          "days": null,
          "time": null,
          "type": 1
        },
        "transactions": {
          "count": 0
        },
        "template_id": "1-T000043",
        "contract_id": "1-T000036",
        "id": "1-T000045",
        "amount": {
          "unit": "LIT",
          "value": 500
        },
        "sum": null,
        "time": {
          "type": 5,
          "number": "1"
        },
        "date": "12/17/2019 13:07:29",
        "productType": "1-276PF01",
        "productGroup": "1-276PF0E",
        "productTypeName": "Топливо",
        "productTypeNameNormal": "Топливо",
        "productGroupName": "G-95"
      }
    ]
  },
  "timestamp": 1585191856
}
```

Вывод примера на этом ответе:

```text
1-T000044: Топливо — 3000.0 LIT
1-T000045: Топливо — 500.0 LIT
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TemplateLimitListResponse`](../../data-types/templates/TemplateLimitListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>TemplateLimitListData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`TemplateLimitListData`](../../data-types/templates/TemplateLimitListData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество найденных лимитов |
| `result` | `data.result` | <code>list[TemplateLimit] &#124; None</code> | Нет | Список лимитов шаблона |

#### [`TemplateLimit`](../../data-types/templates/TemplateLimit.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Идентификатор лимита шаблона |
| `template_id` | `data.result[].template_id` | <code>str</code> | Да | Идентификатор шаблона, которому принадлежит лимит |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | Идентификатор договора, на который распространяется лимит |
| `amount` | `data.result[].amount` | <code>LimitAmount &#124; None</code> | Нет | Объемный лимит (в литрах и т.д.) |
| `sum` | `data.result[].sum` | <code>LimitSum &#124; None</code> | Нет | Суммовой лимит (в рублях и т.д.) |
| `time` | `data.result[].time` | <code>LimitTime</code> | Да | Период действия лимита |
| `term` | `data.result[].term` | <code>LimitTerm</code> | Да | Дополнительные временные ограничения |
| `transactions` | `data.result[].transactions` | <code>LimitTransactions</code> | Да | Информация по транзакциям лимита |
| `date` | `data.result[].date` | <code>str</code> | Да | Дата создания лимита (MM/DD/YYYY HH:MM:SS) |
| `productType` | `data.result[].productType` | <code>str</code> | Да | Тип продукта (топливо, услуга и т.д.) |
| `productGroup` | `data.result[].productGroup` | <code>str &#124; None</code> | Нет | Группа продукта (например, G-95) |
| `productTypeName` | `data.result[].productTypeName` | <code>str</code> | Да | Название типа продукта |
| `productGroupName` | `data.result[].productGroupName` | <code>str &#124; None</code> | Нет | Название группы продукта |

#### [`LimitAmount`](../../data-types/limits/LimitAmount.md) · `data.result[].amount`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `unit` | `data.result[].amount.unit` | <code>str</code> | Да | Единица измерения (например, 'LIT') |
| `value` | `data.result[].amount.value` | <code>float</code> | Да | Количество или объем в единицах измерения |

#### [`LimitSum`](../../data-types/limits/LimitSum.md) · `data.result[].sum`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `currency` | `data.result[].sum.currency` | <code>str</code> | Да | Код валюты (например, '810') |
| `currencyName` | `data.result[].sum.currencyName` | <code>str &#124; None</code> | Нет | Название валюты (например, 'р.') |
| `value` | `data.result[].sum.value` | <code>float</code> | Да | Сумма лимита в указанной валюте |

#### [`LimitTime`](../../data-types/limits/LimitTime.md) · `data.result[].time`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `type` | `data.result[].time.type` | <code>int</code> | Да | Тип периода лимита (например, 3 — день, 5 — месяц) |
| `number` | `data.result[].time.number` | <code>int</code> | Да | Количество единиц периода; API присылает строку, SDK приводит её к int |

#### [`LimitTerm`](../../data-types/limits/LimitTerm.md) · `data.result[].term`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `days` | `data.result[].term.days` | <code>str &#124; None</code> | Нет | Маска дней действия лимита (например, '1111100') |
| `type` | `data.result[].term.type` | <code>int</code> | Да | Тип временного ограничения |
| `time` | `data.result[].term.time` | <code>LimitTermTime &#124; None</code> | Нет | Временные границы лимита |

#### [`LimitTransactions`](../../data-types/limits/LimitTransactions.md) · `data.result[].transactions`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `count` | `data.result[].transactions.count` | <code>int</code> | Да | Количество транзакций, на которое распространяется лимит |

#### [`LimitTermTime`](../../data-types/limits/LimitTermTime.md) · `data.result[].term.time`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `from` | `data.result[].term.time.from` | <code>str &#124; None</code> | Нет | Начало временного диапазона (например, '03:00') |
| `to` | `data.result[].term.time.to` | <code>str &#124; None</code> | Нет | Конец временного диапазона (например, '08:00') |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Шаблона с таким ID нет в договоре.

**Что делать:** Возьмите ID из `get_templates()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Шаблон не найден"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении get_template_limits Сообщение сервера: Шаблон не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `date` приходит в формате `MM/DD/YYYY HH:MM:SS`, `time.number` — строкой; SDK приводит его к `int`.
