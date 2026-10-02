---
description: "Товарные ограничители шаблона: пример client.templates.get_template_restrictions() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/templates.yaml. Не редактируйте вручную. -->

# Товарные ограничители шаблона

`client.templates.get_template_restrictions()` · [справочник метода](../../methods/templates.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/templates/get_template_restrictions.py)

Получить товарные ограничители шаблона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/vc/templates/{template_id}/restrictions` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Товарные ограничители шаблона: client.templates.get_template_restrictions().

Получить товарные ограничители шаблона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/templates/get_template_restrictions.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/templates/get_template_restrictions/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
TEMPLATE_ID = "1-3BDZMRJ"


async def example(client: APIClient) -> None:
    response = await client.templates.get_template_restrictions(template_id=TEMPLATE_ID)
    for item in response.data.result:
        kind = "разрешено" if item.restriction_type == 1 else "запрещено"
        print(f"{item.id}: {item.productTypeName} — {kind}")


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
GET /vip/v2/vc/templates/1-3BDZMRJ/restrictions HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `template_id` | путь | `1-3BDZMRJ` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`TemplateRestrictionListResponse`](../../data-types/templates/TemplateRestrictionListResponse.md).
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
        "id": "1-3BE2H2O",
        "template_id": "1-3BDZMRJ",
        "contract_id": "1-380B94P",
        "date": "12/17/2019 19:19:14",
        "productType": "1-276PF01",
        "productGroup": null,
        "productTypeName": "Топливо",
        "productGroupName": null,
        "restriction_type": 1
      },
      {
        "id": "1-3BDZNJY",
        "template_id": "1-3BDZMRJ",
        "contract_id": "1-380B94P",
        "date": "12/17/2019 13:07:30",
        "productType": "1-276PF01",
        "productGroup": "1-276PF0E",
        "productTypeName": "Топливо",
        "productGroupName": "G-95",
        "restriction_type": 1
      }
    ]
  },
  "timestamp": 1585191856
}
```

Вывод примера на этом ответе:

```text
1-3BE2H2O: Топливо — разрешено
1-3BDZNJY: Топливо — разрешено
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`TemplateRestrictionListResponse`](../../data-types/templates/TemplateRestrictionListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>TemplateRestrictionListData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`TemplateRestrictionListData`](../../data-types/templates/TemplateRestrictionListData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество найденных ограничителей |
| `result` | `data.result` | <code>list[TemplateRestriction] &#124; None</code> | Нет | Список ограничителей шаблона |

#### [`TemplateRestriction`](../../data-types/templates/TemplateRestriction.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Идентификатор ограничителя шаблона |
| `template_id` | `data.result[].template_id` | <code>str</code> | Да | Идентификатор шаблона |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | Идентификатор договора |
| `date` | `data.result[].date` | <code>str</code> | Да | Дата создания ограничителя (MM/DD/YYYY HH:MM:SS) |
| `productType` | `data.result[].productType` | <code>str</code> | Да | Тип продукта |
| `productGroup` | `data.result[].productGroup` | <code>str &#124; None</code> | Нет | Группа продукта |
| `productTypeName` | `data.result[].productTypeName` | <code>str</code> | Да | Название типа продукта |
| `productGroupName` | `data.result[].productGroupName` | <code>str &#124; None</code> | Нет | Название группы продукта |
| `restriction_type` | `data.result[].restriction_type` | <code>int</code> | Да | Тип ограничителя (1 — разрешение, 2 — запрет) |

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
NotFoundError: [404] Объект или маршрут не найден при выполнении get_template_restrictions Сообщение сервера: Шаблон не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).
