---
description: "Географические ограничения шаблона: пример client.templates.get_template_georestrictions() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Географические ограничения шаблона

`client.templates.get_template_georestrictions()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/get_template_georestrictions.py)

Получить страны, регионы и АЗС, где разрешено или запрещено пользоваться картами шаблона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/vc/templates/{template_id}/georestrictions` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Географические ограничения шаблона: client.templates.get_template_georestrictions().

Получить страны, регионы и АЗС, где разрешено или запрещено пользоваться картами
шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/get_template_georestrictions.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/get_template_georestrictions/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-T000043"


async def example(client: APIClient) -> None:
    response = await client.templates.get_template_georestrictions(template_id=TEMPLATE_ID)
    for item in response.data.result or []:
        print(f"{item.id}: {item.countryName}, {item.regionName}")


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
GET /vip/v2/vc/templates/1-T000043/georestrictions HTTP/1.1
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

SDK проверяет ответ моделью [`TemplateGeoRestrictionListResponse`](../../data-types/templates/TemplateGeoRestrictionListResponse.md).
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
        "id": "1-T000071",
        "template_id": "1-T000070",
        "contract_id": "1-T000004",
        "date": "03/26/2020 05:59:58",
        "country": "RUS",
        "countryName": "Россия",
        "region": "45",
        "regionName": "Москва",
        "partner": null,
        "partnerName": null,
        "service_center": null,
        "service_centerName": "",
        "restriction_type": 1
      }
    ]
  },
  "timestamp": 1585191856
}
```

Вывод примера на этом ответе:

```text
1-T000071: Россия, Москва
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TemplateGeoRestrictionListResponse`](../../data-types/templates/TemplateGeoRestrictionListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>TemplateGeoRestrictionListData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`TemplateGeoRestrictionListData`](../../data-types/templates/TemplateGeoRestrictionListData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество найденных геоограничителей |
| `result` | `data.result` | <code>list[TemplateGeoRestriction] &#124; None</code> | Нет | Список геоограничителей шаблона |

#### [`TemplateGeoRestriction`](../../data-types/templates/TemplateGeoRestriction.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Идентификатор геоограничителя шаблона |
| `template_id` | `data.result[].template_id` | <code>str</code> | Да | Идентификатор шаблона |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | Идентификатор договора |
| `date` | `data.result[].date` | <code>str</code> | Да | Дата создания записи (MM/DD/YYYY HH:MM:SS) |
| `country` | `data.result[].country` | <code>str</code> | Да | Код страны (например, 'RUS') |
| `countryName` | `data.result[].countryName` | <code>str</code> | Да | Название страны |
| `region` | `data.result[].region` | <code>str &#124; None</code> | Нет | Код региона |
| `regionName` | `data.result[].regionName` | <code>str &#124; None</code> | Нет | Название региона |
| `partner` | `data.result[].partner` | <code>str &#124; None</code> | Нет | Код партнера (АЗС) |
| `partnerName` | `data.result[].partnerName` | <code>str &#124; None</code> | Нет | Название партнера (АЗС) |
| `service_center` | `data.result[].service_center` | <code>str &#124; None</code> | Нет | Код сервисного центра |
| `service_centerName` | `data.result[].service_centerName` | <code>str &#124; None</code> | Нет | Название сервисного центра |
| `restriction_type` | `data.result[].restriction_type` | <code>int</code> | Да | Тип геоограничителя (1 — разрешение, 2 — запрет) |

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
NotFoundError: [404] Объект или маршрут не найден при выполнении get_template_georestrictions Сообщение сервера: Шаблон не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).
