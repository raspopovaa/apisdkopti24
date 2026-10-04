---
description: "Изменение товарного ограничителя шаблона: пример client.templates.update_template_restriction() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Изменение товарного ограничителя шаблона

`client.templates.update_template_restriction()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/update_template_restriction.py)

Изменить тип продукта или вид товарного ограничителя шаблона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/vc/templates/{template_id}/restrictions/{restriction_id}` | Да | — | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Изменение товарного ограничителя шаблона: client.templates.update_template_restriction().

Изменить тип продукта или вид товарного ограничителя шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/update_template_restriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/update_template_restriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000043"
RESTRICTION_ID = "1-T000047"


async def example(client: APIClient) -> None:
    response = await client.templates.update_template_restriction(
        template_id=TEMPLATE_ID,
        restriction_id=RESTRICTION_ID,
        payload={"product_type": "1-276PF01", "restriction_type": 2},
    )
    print(f"Ограничитель обновлён: {response.data}")


async def main() -> None:
    answer = input("Вызов изменяет данные на реальном API. Продолжить? [yes/no] ")
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
| `restriction_id` | <code>str</code> | Да | — | ID ограничителя шаблона ВК. |
| `payload` | <code>TemplateRestrictionCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Изменяемые параметры ограничителя: `product_type`, `product_group`, `restriction_type`; `contract_id` изменить нельзя. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора (Изменить нельзя) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `True` | — |

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
POST /vip/v2/vc/templates/1-T000043/restrictions/1-T000047 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "product_type": "1-276PF01",
  "restriction_type": 2,
  "contract_id": "1-T000025",
  "_method": "PUT"
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-T000043` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `restriction_id` | путь | `1-T000047` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `product_type` | тело JSON | `"1-276PF01"` | string | Да | ID типа продукта |
| `restriction_type` | тело JSON | `2` | number | Да | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель |
| `contract_id` | тело JSON | `"1-T000025"` | string | Да | ID договора (Изменить нельзя) |
| `_method` | тело JSON | `"PUT"` | string | — | — |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateRestrictionCreateResponse`](../../data-types/templates/TemplateRestrictionCreateResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": "1-T000047",
  "timestamp": 1586308843
}
```

Вывод примера на этом ответе:

```text
Ограничитель обновлён: 1-T000047
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

### 404 · `NotFoundError`

**Почему:** Ограничителя с таким ID нет в шаблоне.

**Что делать:** Возьмите ID из `get_template_restrictions()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Ограничитель не найден"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении update_template_restriction Сообщение сервера: Ограничитель не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
