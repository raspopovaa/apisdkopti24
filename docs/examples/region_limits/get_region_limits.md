---
description: "Список региональных ограничений: пример client.region_limits.get_region_limits() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/region_limits.yaml. Не редактируйте вручную. -->

# Список региональных ограничений

`client.region_limits.get_region_limits()` · [справочник метода](../../methods/region_limits.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/region_limits/get_region_limits.py)

Получить региональные ограничения договора, карты или группы карт: страну, регион, АЗС и тип ограничения.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/regionLimit` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Список региональных ограничений: client.region_limits.get_region_limits().

Получить региональные ограничения договора, карты или группы карт: страну, регион, АЗС и
тип ограничения.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/region_limits/get_region_limits.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/region_limits/get_region_limits/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.region_limits.get_region_limits()
    for item in response.data.result:
        kind = "разрешено" if item.limit_type == 1 else "запрещено"
        print(f"{item.id}: {item.country}, регион {item.region} — {kind}")


async def main() -> None:
    answer = input("Вызов тарифицируется на реальном API. Продолжить? [yes/no] ")
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
| `contract_id` | `str | None` | Нет | `None` | ID контракта. |
| `card_id` | `str | None` | Нет | `None` | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все региональные лимиты, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех региональных лимитах по карте |
| `group_id` | `str | None` | Нет | `None` | ID группы карт. Если передан ID группы карты, то будут возвращены все региональные лимиты указанной группы карт. Если передан ID карты и ID группы карт, то будет возвращена информация по карте |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/regionLimit?contract_id=1-2Q4CN99 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID контракта. |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`RegionLimitResponse`](../../data-types/region_limits/RegionLimitResponse.md).
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
        "id": "6355674",
        "card_id": null,
        "group_id": null,
        "contract_id": "1-1N7MWYG",
        "country": "RUS",
        "region": "04",
        "service_center": "2052059",
        "date": "09/03/2018 00:00:00",
        "limit_type": 1
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
6355674: RUS, регион 04 — разрешено
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`RegionLimitResponse`](../../data-types/region_limits/RegionLimitResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `RegionLimitList` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`RegionLimitList`](../../data-types/region_limits/RegionLimitList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Общее количество лимитов |
| `result` | `data.result` | `list[RegionLimit] | None` | Нет | Данные с лимитами |

#### [`RegionLimit`](../../data-types/region_limits/RegionLimit.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `str | None` | Да | ID регионального лимита |
| `contract_id` | `data.result[].contract_id` | `str` | Да | ID договора, к которому относится лимит |
| `card_id` | `data.result[].card_id` | `str | None` | Нет | ID карты, если лимит задан для карты |
| `group_id` | `data.result[].group_id` | `str | None` | Нет | ID группы карт, если лимит задан для группы |
| `country` | `data.result[].country` | `str` | Да | Код страны обслуживания, пример - RUS |
| `region` | `data.result[].region` | `str | None` | Нет | Код регион обслуживания |
| `service_center` | `data.result[].service_center` | `str | None` | Нет | ID АЗС |
| `date` | `data.result[].date` | `str` | Да | Дата последнего изменения |
| `limit_type` | `data.result[].limit_type` | `int` | Да | Тип лимита |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Пользователь API не имеет доступа к договору.

**Что делать:** Проверьте `contract_id` и права пользователя.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Нет доступа к договору"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_region_limits Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `limit_type`: 1 — разрешающее ограничение (картой можно пользоваться только там), 2 — запрещающее.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
