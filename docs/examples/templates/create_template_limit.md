---
description: "Добавление лимита в шаблон: пример client.templates.create_template_limit() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Добавление лимита в шаблон

`client.templates.create_template_limit()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/create_template_limit.py)

Добавить лимит в шаблон: например, не больше 5000 рублей на бензин в месяц.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/vc/templates/{template_id}/limits` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Добавление лимита в шаблон: client.templates.create_template_limit().

Добавить лимит в шаблон: например, не больше 5000 рублей на бензин в месяц.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/create_template_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/create_template_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.templates import TemplateLimitCreateRequest

# Условные значения: замените своими.
TEMPLATE_ID = "1-3BDYGX5"


async def example(client: APIClient) -> None:
    payload = TemplateLimitCreateRequest(
        product_type="1-276PF01",
        sum={"currency": "810", "value": 5000},
        time={"type": 5, "number": 1},
    )
    response = await client.templates.create_template_limit(
        template_id=TEMPLATE_ID, payload=payload
    )
    print(f"ID лимита: {response.data}")


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
| `payload` | <code>TemplateLimitCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Параметры лимита шаблона ВК: `contract_id`, ограничение `amount` или `sum`, параметры `time`/`term`, `product_type`, `product_group`, а также `create_restriction`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |
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
POST /vip/v2/vc/templates/1-3BDYGX5/limits HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "product_type": "1-276PF01",
  "sum": {
    "currency": "810",
    "value": 5000.0
  },
  "time": {
    "number": 1,
    "type": 5
  },
  "contract_id": "1-2Q4CN99"
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-3BDYGX5` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `product_type` | тело JSON | `"1-276PF01"` | string | Да | ID типа продукта |
| `sum` | тело JSON | `{"currency": "810", "value": 5000.0}` | object | Нет | Ограничение по сумме (Обязательный параметр, если не заполнено amount) |
| `time` | тело JSON | `{"number": 1, "type": 5}` | object | Да | Длительность, период времени |
| `contract_id` | тело JSON | `"1-2Q4CN99"` | string | Да | ID договора |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateLimitCreateResponse`](../../data-types/templates/TemplateLimitCreateResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": "1-3BDZNGO",
  "timestamp": 1586308843
}
```

Вывод примера на этом ответе:

```text
ID лимита: 1-3BDZNGO
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

### 400 · `ValidationError`

**Почему:** Тип продукта не найден в справочнике.

**Что делать:** Возьмите код из справочника `ProductType`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректный тип продукта"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении create_template_limit Сообщение сервера: Некорректный тип продукта. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.templates.create_template_limit(template_id=TEMPLATE_ID, payload={"sum": {"currency": "810", "value": 5000}, "time": {"type": 5, "number": 1}})
```

Тип продукта `product_type` обязателен. Исключение `pydantic.ValidationError`:

```text
1 validation error for TemplateLimitCreateRequest
product_type
  Field required [type=missing]
```

```python
await client.templates.create_template_limit(template_id=TEMPLATE_ID, payload={"product_type": "1-276PF01", "sum": {"currency": "810", "valeu": 5000}, "time": {"type": 5, "number": 1}})
```

Опечатка в поле суммы (`valeu`) не уходит на сервер молча. Исключение `pydantic.ValidationError`:

```text
2 validation errors for TemplateLimitCreateRequest
sum.value
  Field required [type=missing]
sum.valeu
  Extra inputs are not permitted [type=extra_forbidden]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `create_restriction=True` вместе с лимитом создаёт и товарный ограничитель на тот же продукт.
- Тип периода `time.type`: 2 — разовый, 3 — сутки, 4 — неделя, 5 — месяц, 6 — квартал, 7 — год.
- `sum`, `amount`, `time` и `term` проверяются так же, как у лимитов карт: лишние поля запрещены, сумма — не больше двух знаков после запятой, `term.days` — 7 символов `0` или `1`, `term.type` — 1, 2 или 3.
- Договор задаётся один раз: аргументом `contract_id` или полем `contract_id` в `payload`. Разные значения SDK отклоняет до запроса.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
