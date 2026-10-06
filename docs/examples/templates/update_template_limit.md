---
description: "Изменение лимита шаблона: пример client.templates.update_template_limit() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Изменение лимита шаблона

`client.templates.update_template_limit()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/update_template_limit.py)

Изменить сумму, объём или период лимита шаблона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/vc/templates/{template_id}/limits/{limit_id}` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Изменение лимита шаблона: client.templates.update_template_limit().

Изменить сумму, объём или период лимита шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/update_template_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/update_template_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000042"
LIMIT_ID = "1-T000045"


async def example(client: APIClient) -> None:
    limit = {
        "product_type": "1-276PF01",
        "sum": {"currency": "810", "value": 7000},
        "time": {"type": 5, "number": 1},
    }
    response = await client.templates.update_template_limit(
        template_id=TEMPLATE_ID, limit_id=LIMIT_ID, limit=limit
    )
    print(f"Лимит обновлён: {response.data}")


async def main() -> None:
    answer = input("Вызов изменяет данные и тарифицируется на реальном API. Продолжить? [yes/no] ")
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
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `limit_id` | <code>str</code> | Да | — | ID лимита шаблона ВК. |
| `limit` | <code>TemplateLimitCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Параметры изменения лимита: ограничение `amount` или `sum`, `time`/`term`, `product_type`, `product_group`; `contract_id` изменить нельзя. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора (Изменить нельзя) |
| `use_post` | <code>bool</code> | Нет | `True` | — |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`TemplateLimitCreateRequest`](../../data-types/templates/TemplateLimitCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | Идентификатор договора |
| `product_type` | <code>str</code> | Да | — | Тип продукта (например, '1-276PF01') |
| `product_group` | <code>str &#124; None</code> | Нет | — | Группа продукта (например, '1-276PF0E') |
| `sum` | <code>LimitSumRequest &#124; None</code> | Нет | — | Суммовой лимит |
| `amount` | <code>LimitAmountRequest &#124; None</code> | Нет | — | Объемный лимит |
| `time` | <code>LimitTimeRequest</code> | Да | — | Период лимита |
| `term` | <code>LimitTermRequest &#124; None</code> | Нет | — | Дополнительные временные ограничения |
| `create_restriction` | <code>bool &#124; None</code> | Нет | — | Создать ограничитель автоматически |

#### [`LimitSumRequest`](../../data-types/limits/LimitSumRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `currency` | <code>str</code> | Да | минимальная длина: 1 | Код валюты |
| `value` | <code>Decimal</code> | Да | строго больше: 0.0; шаблон: '^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d{0,2}0*$' | Размер денежного лимита в рублях, не больше двух знаков после запятой |

#### [`LimitAmountRequest`](../../data-types/limits/LimitAmountRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `unit` | <code>str</code> | Да | минимальная длина: 1 | Единица измерения |
| `value` | <code>float</code> | Да | строго больше: 0 | Размер объёмного лимита |

#### [`LimitTimeRequest`](../../data-types/limits/LimitTimeRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `number` | <code>int</code> | Да | строго больше: 0 | Количество периодов |
| `type` | <code>Literal[2, 3, 4, 5, 6, 7]</code> | Да | допустимые значения: 2, 3, 4, 5, 6, 7 | Тип периода |

#### [`LimitTermRequest`](../../data-types/limits/LimitTermRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `days` | <code>str &#124; None</code> | Нет | шаблон: '^[01]{7}$'; — | Маска дней недели |
| `type` | <code>Literal[1, 2, 3]</code> | Да | допустимые значения: 1, 2, 3 | Тип применения ограничения |
| `time` | <code>LimitTermTimeRequest &#124; None</code> | Нет | — | Интервал обслуживания |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/vc/templates/1-T000042/limits/1-T000045 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "product_type": "1-276PF01",
  "sum": {
    "currency": "810",
    "value": 7000.0
  },
  "time": {
    "number": 1,
    "type": 5
  },
  "contract_id": "1-T000025",
  "_method": "PUT"
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-T000042` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `limit_id` | путь | `1-T000045` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `product_type` | тело JSON | `"1-276PF01"` | string | Да | ID типа продукта |
| `sum` | тело JSON | `{"currency": "810", "value": 7000.0}` | object | Нет | Ограничение по сумме (Обязательный параметр, если не заполнено amount) |
| `time` | тело JSON | `{"number": 1, "type": 5}` | object | Да | Длительность, период времени |
| `contract_id` | тело JSON | `"1-T000025"` | string | Да | ID договора (Изменить нельзя) |
| `_method` | тело JSON | `"PUT"` | string | — | — |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateLimitCreateResponse`](../../data-types/templates/TemplateLimitCreateResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": "1-T000045",
  "timestamp": 1586308843
}
```

Вывод примера на этом ответе:

```text
Лимит обновлён: 1-T000045
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TemplateLimitCreateResponse`](../../data-types/templates/TemplateLimitCreateResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>str</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Лимита с таким ID нет в шаблоне.

**Что делать:** Возьмите ID из `get_template_limits()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Лимит не найден"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении update_template_limit Сообщение сервера: Лимит не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.templates.update_template_limit(template_id=TEMPLATE_ID, limit_id=LIMIT_ID)
```

Не переданы новые параметры лимита `limit`. Исключение `TypeError`:

```text
_TemplateLimitOperations.update_template_limit() missing 1 required keyword-only argument: 'limit'
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- По умолчанию SDK отправляет изменение запросом POST с полем `_method=PUT` (`use_post=True`); `use_post=False` отправляет запрос PUT.
- `limit` — новые параметры лимита `limit_id`. В теле запроса SDK отправляет объект лимита, а не массив: массив сервер отклоняет с кодом `405`.
- Параметр тело запроса: массив отклоняется с кодом 405. В SDK — отправляет объект из параметра `limit`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
