---
description: "Добавление географического ограничения в шаблон: пример client.templates.create_template_georestriction() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Добавление географического ограничения в шаблон

`client.templates.create_template_georestriction()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/create_template_georestriction.py)

Разрешить или запретить картам шаблона работу в стране, регионе или на АЗС.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/vc/templates/{template_id}/georestrictions` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Добавление географического ограничения в шаблон: client.templates.create_template_georestriction().

Разрешить или запретить картам шаблона работу в стране, регионе или на АЗС.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/create_template_georestriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/create_template_georestriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-3BDZMRJ"


async def example(client: APIClient) -> None:
    response = await client.templates.create_template_georestriction(
        template_id=TEMPLATE_ID,
        payload={"country": "RUS", "region": "45", "restriction_type": 1},
    )
    print(f"ID ограничения: {response.data}")


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
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `payload` | `TemplateGeoRestrictionCreateRequest | Mapping[str, Any]` | Да | — | Параметры геоограничителя: `contract_id`, `country`, `region`, `partner`, `service_center`, `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | `str | None` | Нет | `None` | ID договора |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

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
POST /vip/v2/vc/templates/1-3BDZMRJ/georestrictions HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "country": "RUS",
  "region": "45",
  "restriction_type": 1,
  "contract_id": "1-2Q4CN99"
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-3BDZMRJ` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `country` | тело JSON | `"RUS"` | string | Да | ID страны |
| `region` | тело JSON | `"45"` | string | Нет | ID региона |
| `restriction_type` | тело JSON | `1` | number | Да | 1 – Разрешающий геоограничитель, 2 – Запрещающий геоограничитель |
| `contract_id` | тело JSON | `"1-2Q4CN99"` | string | Да | ID договора |
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
ID ограничения: 1-3BE55MK
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

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Код страны или региона не найден в справочниках.

**Что делать:** Возьмите коды из справочников `Country` и `Region`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Неизвестный регион"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении create_template_georestriction Сообщение сервера: Неизвестный регион. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.templates.create_template_georestriction(template_id=TEMPLATE_ID, payload={"region": "45", "restriction_type": 1})
```

Страна `country` обязательна. Исключение `pydantic.ValidationError`:

```text
1 validation error for TemplateGeoRestrictionCreateRequest
country
  Field required [type=missing]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Коды стран и регионов берутся из справочников `Country` и `Region`, партнёров — из `POIPartner`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
