---
description: "Установка регионального ограничения: пример client.region_limits.set_region_limit() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/region_limits.yaml. Не редактируйте вручную. -->

# Установка регионального ограничения

`client.region_limits.set_region_limit()` · [справочник метода](../../methods/region_limits.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/region_limits/set_region_limit.py)

Разрешить карте работать только в одном регионе или запретить конкретную страну, регион или АЗС.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/setRegionLimit` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Установка регионального ограничения: client.region_limits.set_region_limit().

Разрешить карте работать только в одном регионе или запретить конкретную страну, регион
или АЗС.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/region_limits/set_region_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/region_limits/set_region_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.region_limits import RegionLimitRequestItem

# Условные значения: замените своими.
CARD_ID = "2725116"


async def example(client: APIClient) -> None:
    limit = RegionLimitRequestItem(card_id=CARD_ID, country="RUS", region="04", limit_type=1)
    response = await client.region_limits.set_region_limit(region_limits=[limit])
    print(f"ID ограничений: {', '.join(response.data or [])}")


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
| `region_limits` | `list[RegionLimitRequestItem]` | Да | — | Массив параметров регионального лимита: ID лимита, карты, группы и договора, страна, регион, АЗС, партнёр и `limit_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`RegionLimitRequestItem`](../../data-types/region_limits/RegionLimitRequestItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | `str | None` | Нет | минимальная длина: 1; — | ID регионального лимита при изменении существующей записи |
| `contract_id` | `str | None` | Нет | минимальная длина: 1; — | ID договора |
| `card_id` | `str | None` | Нет | минимальная длина: 1; — | ID карты |
| `group_id` | `str | None` | Нет | минимальная длина: 1; — | ID группы карт |
| `country` | `str` | Да | минимальная длина: 1 | Код страны обслуживания |
| `region` | `str | None` | Нет | минимальная длина: 1; — | Код региона обслуживания |
| `service_center` | `str | None` | Нет | минимальная длина: 1; — | ID точки обслуживания |
| `partner` | `str | None` | Нет | минимальная длина: 1; — | ID партнёра |
| `limit_type` | `Literal[1, 2]` | Да | допустимые значения: 1, 2 | Тип лимита: 1 — разрешающий, 2 — запрещающий |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/setRegionLimit HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

region_limit=[{"card_id":"2725116","country":"RUS","region":"04","limit_type":1,"contract_id":"1-2Q4CN99"}]
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `region_limit` | форма | `[{"card_id":"2725116","country":"RUS","region":"04","limit_type":1,"contract_id":"1-2Q4CN99"}]` | string | Да | Массив параметров |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`RegionLimitSetResponse`](../../data-types/region_limits/RegionLimitSetResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    "6358201"
  ],
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
ID ограничений: 6358201
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`RegionLimitSetResponse`](../../data-types/region_limits/RegionLimitSetResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `list[str] | None` | Нет | ID сохранённых региональных лимитов |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `TypeError`

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
region_limits[0] должен быть экземпляром RegionLimitRequestItem
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.region_limits.set_region_limit(region_limits=[{"card_id": CARD_ID, "country": "RUS", "limit_type": 3}])
```

Тип ограничения может быть только 1 (разрешающий) или 2 (запрещающий). Исключение `TypeError`:

```text
region_limits[0] должен быть экземпляром RegionLimitRequestItem
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Коды стран и регионов берутся из справочников `Country` и `Region`.
