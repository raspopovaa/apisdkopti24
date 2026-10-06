---
description: "Изменение шаблона: пример client.templates.update_template() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Изменение шаблона

`client.templates.update_template()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/update_template.py)

Изменить имя или тип шаблона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/vc/templates/{template_id}` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Изменение шаблона: client.templates.update_template().

Изменить имя или тип шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/update_template.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/update_template/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000042"


async def example(client: APIClient) -> None:
    response = await client.templates.update_template(
        template_id=TEMPLATE_ID, type_="Wallet", name="Водители Москва и МО"
    )
    print(f"Шаблон обновлён: {response.data}")


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
| `type_` | <code>Literal[Limit, Wallet]</code> | Да | — | Тип карты: `Limit` — лимитная схема, `Wallet` — электронный кошелёк. |
| `name` | <code>str</code> | Да | — | Имя шаблона ВК, уникальное в рамках договора. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора (Изменить нельзя) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `True` | — |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`TemplateCreateRequest`](../../data-types/templates/TemplateCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | Идентификатор договора |
| `type` | <code>Literal[Limit, Wallet]</code> | Да | допустимые значения: 'Limit', 'Wallet' | Тип создаваемого шаблона |
| `name` | <code>str</code> | Да | минимальная длина: 1; максимальная длина: 30 | Имя (название) нового шаблона ВК |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/vc/templates/1-T000042 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-T000025&type=Wallet&name=Водители Москва и МО&_method=PUT
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-T000042` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `contract_id` | форма | `1-T000025` | string | Да | ID договора (Изменить нельзя) |
| `type` | форма | `Wallet` | string | Да | Тип карты (Limit – лимитная схема, Wallet – электронный кошелек) |
| `name` | форма | `Водители Москва и МО` | string | Да | Имя шаблона ВК (Уникальное в рамках договора) |
| `_method` | форма | `PUT` | string | — | — |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateCreateResponse`](../../data-types/templates/TemplateCreateResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": "1-T000042",
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Шаблон обновлён: 1-T000042
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TemplateCreateResponse`](../../data-types/templates/TemplateCreateResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>str</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

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
NotFoundError: [404] Объект или маршрут не найден при выполнении update_template Сообщение сервера: Шаблон не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.templates.update_template(template_id=TEMPLATE_ID, type_="Wallet", name="")
```

Пустое имя шаблона отклоняется моделью запроса. Исключение `RequestValidationError`:

```text
name: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Сервер принимает изменение шаблона только методом PUT. По умолчанию SDK отправляет POST с полем `_method=PUT` (`use_post=True`); `use_post=False` отправляет запрос PUT.
- Имя шаблона — от 1 до 30 символов: более длинное API отклоняет с ошибкой `400`, поэтому SDK проверяет длину до платного запроса.
- В описании API тело запроса — JSON, но SDK отправляет форму: сервер её принимает.
- Параметр HTTP-метод: POST без `_method=PUT` отклоняется с кодом 405. В SDK — по умолчанию POST с `_method=PUT`; `use_post=False` отправляет PUT.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
