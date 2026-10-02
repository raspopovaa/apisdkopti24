---
description: "Добавление товарного ограничителя в шаблон: пример client.templates.create_template_restriction() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Добавление товарного ограничителя в шаблон

`client.templates.create_template_restriction()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/create_template_restriction.py)

Разрешить или запретить в шаблоне тип продукта.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/vc/templates/{template_id}/restrictions` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Добавление товарного ограничителя в шаблон: client.templates.create_template_restriction().

Разрешить или запретить в шаблоне тип продукта.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/create_template_restriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/create_template_restriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-3BDZMRJ"


async def example(client: APIClient) -> None:
    response = await client.templates.create_template_restriction(
        template_id=TEMPLATE_ID,
        payload={"product_type": "1-276PF01", "product_group": "1-276PF0E", "restriction_type": 1},
    )
    print(f"ID ограничителя: {response.data}")


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
| `payload` | <code>TemplateRestrictionCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Параметры ограничителя: `contract_id`, `product_type`, `product_group`, `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`TemplateRestrictionCreateRequest`](../../data-types/templates/TemplateRestrictionCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | Идентификатор договора |
| `product_type` | <code>str</code> | Да | — | Тип продукта (например, '1-276PF01') |
| `product_group` | <code>str &#124; None</code> | Нет | — | Группа продукта (например, '1-276PF0E') |
| `restriction_type` | <code>Literal[1, 2]</code> | Да | допустимые значения: 1, 2 | Тип ограничителя |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/vc/templates/1-3BDZMRJ/restrictions HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "product_type": "1-276PF01",
  "product_group": "1-276PF0E",
  "restriction_type": 1,
  "contract_id": "1-2Q4CN99"
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-3BDZMRJ` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `product_type` | тело JSON | `"1-276PF01"` | string | Да | ID типа продукта |
| `product_group` | тело JSON | `"1-276PF0E"` | string | Нет | ID группы продукта |
| `restriction_type` | тело JSON | `1` | number | Да | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель |
| `contract_id` | тело JSON | `"1-2Q4CN99"` | string | Да | ID договора |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateRestrictionCreateResponse`](../../data-types/templates/TemplateRestrictionCreateResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": "1-3BE2GMK",
  "timestamp": 1586308843
}
```

Вывод примера на этом ответе:

```text
ID ограничителя: 1-3BE2GMK
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TemplateRestrictionCreateResponse`](../../data-types/templates/TemplateRestrictionCreateResponse.md)

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
ValidationError: [400] Некорректные параметры запроса при выполнении create_template_restriction Сообщение сервера: Некорректный тип продукта. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.templates.create_template_restriction(template_id=TEMPLATE_ID, payload={"product_type": "1-276PF01", "restriction_type": 3})
```

Тип ограничителя может быть только 1 или 2. Исключение `pydantic.ValidationError`:

```text
1 validation error for TemplateRestrictionCreateRequest
restriction_type
  Input should be 1 or 2 [type=literal_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `restriction_type`: 1 — разрешающий ограничитель, 2 — запрещающий.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
