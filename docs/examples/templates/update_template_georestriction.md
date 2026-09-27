---
description: "Изменение географического ограничения шаблона: пример client.templates.update_template_georestriction() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Изменение географического ограничения шаблона

`client.templates.update_template_georestriction()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/update_template_georestriction.py)

Изменить страну, регион или вид географического ограничения шаблона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | — | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Изменение географического ограничения шаблона: client.templates.update_template_georestriction().

Изменить страну, регион или вид географического ограничения шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/update_template_georestriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/update_template_georestriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-3BDZMRJ"
GEORESTRICTION_ID = "1-3BE55MK"


async def example(client: APIClient) -> None:
    response = await client.templates.update_template_georestriction(
        template_id=TEMPLATE_ID,
        georestriction_id=GEORESTRICTION_ID,
        payload={"country": "RUS", "region": "50", "restriction_type": 1},
    )
    print(f"Ограничение обновлено: {response.data}")


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
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `georestriction_id` | `str` | Да | — | ID геоограничителя шаблона ВК. |
| `payload` | `TemplateGeoRestrictionCreateRequest | Mapping[str, Any]` | Да | — | Изменяемые параметры геоограничителя: `country`, `region`, `partner`, `service_center`, `restriction_type`; `contract_id` изменить нельзя. |
| `contract_id` | `str | None` | Нет | `None` | ID договора (Изменить нельзя) |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | `bool` | Нет | `True` | — |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`TemplateGeoRestrictionCreateRequest`](../../data-types/templates/TemplateGeoRestrictionCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | минимальная длина: 1; — | Идентификатор договора |
| `country` | `str` | Да | — | Код страны (например, 'RUS') |
| `region` | `str | None` | Нет | — | Код региона (например, '45') |
| `partner` | `str | None` | Нет | — | Код партнера (АЗС) |
| `service_center` | `str | None` | Нет | — | Код сервисного центра |
| `restriction_type` | `Literal[1, 2]` | Да | допустимые значения: 1, 2 | Тип геоограничителя |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/vc/templates/1-3BDZMRJ/georestrictions/1-3BE55MK HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "country": "RUS",
  "region": "50",
  "restriction_type": 1,
  "contract_id": "1-2Q4CN99",
  "_method": "PUT"
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-3BDZMRJ` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `georestriction_id` | путь | `1-3BE55MK` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `country` | тело JSON | `"RUS"` | string | Да | ID страны |
| `region` | тело JSON | `"50"` | string | Нет | ID региона |
| `restriction_type` | тело JSON | `1` | number | Да | 1 – Разрешающий геоограничитель, 2 – Запрещающий геоограничитель |
| `contract_id` | тело JSON | `"1-2Q4CN99"` | string | Да | ID договора (Изменить нельзя) |
| `_method` | тело JSON | `"PUT"` | string | — | — |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateGeoRestrictionCreateResponse`](../../data-types/templates/TemplateGeoRestrictionCreateResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": "1-3BE55MK",
  "timestamp": 1586308843
}
```

Вывод примера на этом ответе:

```text
Ограничение обновлено: 1-3BE55MK
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TemplateGeoRestrictionCreateResponse`](../../data-types/templates/TemplateGeoRestrictionCreateResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `str` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Ограничения с таким ID нет в шаблоне.

**Что делать:** Возьмите ID из `get_template_georestrictions()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Ограничение не найдено"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении update_template_georestriction Сообщение сервера: Ограничение не найдено. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
