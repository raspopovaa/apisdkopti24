---
description: "Установка товарного ограничителя: пример client.restrictions.set_restriction() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/restrictions.yaml. Не редактируйте вручную. -->

# Установка товарного ограничителя

`client.restrictions.set_restriction()` · [справочник метода](../../methods/restrictions.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/restrictions/set_restriction.py)

Разрешить карте покупать только топливо или запретить определённые товары.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/setRestriction` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Установка товарного ограничителя: client.restrictions.set_restriction().

Разрешить карте покупать только топливо или запретить определённые товары.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/restrictions/set_restriction.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/restrictions/set_restriction/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.restrictions import RestrictionRequestItem

# Условные значения: замените своими.
CARD_ID = "9000018"
FUEL_TYPE = "1-CK231"


async def example(client: APIClient) -> None:
    restriction = RestrictionRequestItem.model_validate(
        {"card_id": CARD_ID, "productType": FUEL_TYPE, "restriction_type": 1}
    )
    response = await client.restrictions.set_restriction(restrictions=[restriction])
    print(f"ID ограничителей: {', '.join(response.data or [])}")


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
| `restrictions` | <code>list[RestrictionRequestItem]</code> | Да | — | Массив параметров товарного ограничителя: ID ограничителя, карты, группы и договора, группа и тип продукта, а также `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`RestrictionRequestItem`](../../data-types/restrictions/RestrictionRequestItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID изменяемого ограничителя |
| `contract_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID договора |
| `card_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID карты |
| `group_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID группы карт |
| `productType` | <code>str</code> | Да | минимальная длина: 1 | ID типа продукта |
| `productGroup` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID группы продуктов |
| `restriction_type` | <code>Literal[1, 2]</code> | Да | допустимые значения: 1, 2 | Тип ограничителя: 1 — разрешающий, 2 — запрещающий |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/setRestriction HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

restriction=[{"card_id":"9000018","productType":"1-CK231","restriction_type":1,"contract_id":"1-T000025"}]
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `restriction` | форма | `[{"card_id":"9000018","productType":"1-CK231","restriction_type":1,"contract_id":"1-T000025"}]` | string | Да | Массив параметров |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`RestrictionSetResponse`](../../data-types/restrictions/RestrictionSetResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    18208262
  ]
}
```

Вывод примера на этом ответе:

```text
ID ограничителей: 18208262
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`RestrictionSetResponse`](../../data-types/restrictions/RestrictionSetResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>list[str]</code> | Да | Типизированные данные ответа API |
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
ValidationError: [400] Некорректные параметры запроса при выполнении set_restriction Сообщение сервера: Некорректный тип продукта. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.restrictions.set_restriction(restrictions=[RestrictionRequestItem.model_validate({"card_id": CARD_ID, "restriction_type": 1})])
```

Тип продукта `productType` обязателен. Исключение `pydantic.ValidationError`:

```text
1 validation error for RestrictionRequestItem
productType
  Field required [type=missing]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Коды типов и групп продуктов берутся из справочников `ProductType` и `ProductGroup`. В модели поля называются `product_type` и `product_group`, в запросе — `productType` и `productGroup`.
- Поле `data[]`: ID ограничителей числами. Тип в модели SDK: строки; число приводится к строке.
