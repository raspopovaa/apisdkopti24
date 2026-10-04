---
description: "Установка продуктового лимита: пример client.limits.set_limit() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/limits.yaml. Не редактируйте вручную. -->

# Установка продуктового лимита

`client.limits.set_limit()` · [справочник метода](../../methods/limits.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/limits/set_limit.py)

Ограничить расход по карте: например, не больше 100 литров топлива в сутки. Тот же метод с `id` существующего лимита изменяет его.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/setLimit` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Установка продуктового лимита: client.limits.set_limit().

Ограничить расход по карте: например, не больше 100 литров топлива в сутки. Тот же метод
с `id` существующего лимита изменяет его.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/limits/set_limit.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/limits/set_limit/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.limits import LimitRequestItem

# Условные значения: замените своими.
CARD_ID = "900030"
FUEL_GROUP = "1-CK235"
FUEL_TYPE = "1-CK231"


async def example(client: APIClient) -> None:
    limit = LimitRequestItem.model_validate(
        {
            "card_id": CARD_ID,
            "productGroup": FUEL_GROUP,
            "productType": FUEL_TYPE,
            "amount": {"value": 100, "unit": "LIT"},
            "time": {"number": 1, "type": 3},
        }
    )
    response = await client.limits.set_limit(limits=[limit])
    print(f"ID лимитов: {', '.join(response.data or [])}")


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
| `limits` | <code>list[LimitRequestItem]</code> | Да | — | — |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`LimitRequestItem`](../../data-types/limits/LimitRequestItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID изменяемого лимита |
| `contract_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID договора |
| `card_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID карты |
| `group_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID группы карт |
| `productType` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID типа продукта |
| `productGroup` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID группы продуктов |
| `amount` | <code>LimitAmountRequest &#124; None</code> | Нет | — | Объёмный лимит |
| `sum` | <code>LimitSumRequest &#124; None</code> | Нет | — | Денежный лимит |
| `term` | <code>LimitTermRequest &#124; None</code> | Нет | — | Условия действия лимита |
| `transactions` | <code>LimitTransactionsRequest &#124; None</code> | Нет | — | Лимит количества транзакций |
| `time` | <code>LimitTimeRequest</code> | Да | — | Период действия лимита |

#### [`SetLimitRequest`](../../data-types/limits/SetLimitRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `limits` | <code>list[LimitRequestItem]</code> | Да | минимум элементов: 1 | — |

#### [`LimitAmountRequest`](../../data-types/limits/LimitAmountRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `unit` | <code>str</code> | Да | минимальная длина: 1 | Единица измерения |
| `value` | <code>float</code> | Да | строго больше: 0 | Размер объёмного лимита |

#### [`LimitSumRequest`](../../data-types/limits/LimitSumRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `currency` | <code>str</code> | Да | минимальная длина: 1 | Код валюты |
| `value` | <code>Decimal</code> | Да | строго больше: 0.0; шаблон: '^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d{0,2}0*$' | Размер денежного лимита в рублях, не больше двух знаков после запятой |

#### [`LimitTermRequest`](../../data-types/limits/LimitTermRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `days` | <code>str &#124; None</code> | Нет | шаблон: '^[01]{7}$'; — | Маска дней недели |
| `type` | <code>Literal[1, 2, 3]</code> | Да | допустимые значения: 1, 2, 3 | Тип применения ограничения |
| `time` | <code>LimitTermTimeRequest &#124; None</code> | Нет | — | Интервал обслуживания |

#### [`LimitTransactionsRequest`](../../data-types/limits/LimitTransactionsRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `count` | <code>int</code> | Да | строго больше: 0 | Количество транзакций |

#### [`LimitTimeRequest`](../../data-types/limits/LimitTimeRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `number` | <code>int</code> | Да | строго больше: 0 | Количество периодов |
| `type` | <code>Literal[2, 3, 4, 5, 6, 7]</code> | Да | допустимые значения: 2, 3, 4, 5, 6, 7 | Тип периода |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/setLimit HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

limit=[{"card_id":"900030","productType":"1-CK231","productGroup":"1-CK235","amount":{"unit":"LIT","value":100.0},"time":{"number":1,"type":3},"contract_id":"1-T000025"}]
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `limit` | форма | `[{"card_id":"900030","productType":"1-CK231","productGroup":"1-CK235","amount":{"unit":"LIT","value":100.0},"time":{"number":1,"type":3},"contract_id":"1-T000025"}]` | string | Да | Массив данных лимита |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`SetLimitResponse`](../../data-types/limits/SetLimitResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    "1-T000062"
  ]
}
```

Вывод примера на этом ответе:

```text
ID лимитов: 1-T000062
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`SetLimitResponse`](../../data-types/limits/SetLimitResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>list[str]</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Тип или группа продукта не найдены в справочниках.

**Что делать:** Возьмите коды из справочников `ProductType` и `ProductGroup`.

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
ValidationError: [400] Некорректные параметры запроса при выполнении set_limit Сообщение сервера: Некорректный тип продукта. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.limits.set_limit(limits=[LimitRequestItem.model_validate({"card_id": CARD_ID, "productType": FUEL_TYPE, "time": {"number": 1, "type": 3}})])
```

Не задан ни объём `amount`, ни сумма `sum`. Исключение `pydantic.ValidationError`:

```text
1 validation error for LimitRequestItem
  Value error, Необходимо указать amount или sum [type=value_error]
```

```python
await client.limits.set_limit(limits=[LimitRequestItem.model_validate({"card_id": CARD_ID, "productType": FUEL_TYPE, "amount": {"value": 100, "unit": "LIT"}, "time": {"number": 1, "type": 1}})])
```

Тип периода 1 не существует — допустимы значения от 2 до 7. Исключение `pydantic.ValidationError`:

```text
1 validation error for LimitRequestItem
time.type
  Input should be 2, 3, 4, 5, 6 or 7 [type=literal_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Лимит задаётся объёмом (`amount`) или суммой (`sum`) и периодом `time`. Тип периода: 2 — разовый, 3 — сутки, 4 — неделя, 5 — месяц, 6 — квартал, 7 — год.
- Коды групп и типов продуктов (`productGroup`, `productType`) берутся из справочников `ProductGroup` и `ProductType`.
- Все лимиты пакета SDK отправляет одним полем формы `limit` со строкой JSON-массива.
- Поле `data[]`: ID лимита в формате `1-…`; ID регионального лимита — строка из цифр. Тип в модели SDK: строки.
