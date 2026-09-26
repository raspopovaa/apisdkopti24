---
description: "Сведения о карте: пример client.cards.get_card_detail() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Сведения о карте

`client.cards.get_card_detail()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/get_card_detail.py)

Получить подробную информацию об одной карте: статус, способ авторизации, дату последнего использования, срок действия и настройки таймаута операций.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/cards` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Сведения о карте: client.cards.get_card_detail().

Получить подробную информацию об одной карте: статус, способ авторизации, дату
последнего использования, срок действия и настройки таймаута операций.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_card_detail.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_card_detail/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    NotFoundError,
)

# Условные значения: замените своими.
CARD_ID = "382359"


async def example(client: APIClient) -> None:
    try:
        response = await client.cards.get_card_detail(card_id=CARD_ID)
    except NotFoundError:
        print("Карта не найдена: проверьте CARD_ID и выбранный договор")
        return
    for card in response.data.result:
        print(f"Карта {card.number}: статус {card.status}")
        print(f"Последнее использование: {card.date_last_usage}")


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
| `card_id` | `str` | Да | — | ID карты |
| `contract_id` | `str | None` | Нет | `None` | ID контракта |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/cards?contract_id=1-2Q4CN99&card_id=382359 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID контракта |
| `card_id` | строка запроса | `382359` | string | Да | ID карты |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardDetailResponse`](../../data-types/cards/CardDetailResponse.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 1,
    "result": [
      {
        "id": "382359",
        "contract_id": "1-1FLKAJQ",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "can_work_offline": true,
        "card_auth_type": "PIN",
        "comment": "Комментарий",
        "date_last_usage": "2015-04-27 00:00:00",
        "date_released": null,
        "servicecenter_last_usage_name": "602881",
        "transaction_timeout": {
          "type": 2,
          "value": "1"
        },
        "product": "limit",
        "carrier": "Virtual Card",
        "available": "40000",
        "currency": "810",
        "payment_of_tolls": "N",
        "mpc": false,
        "pin_reset": 3,
        "pin_counter": 3,
        "previous": "",
        "next": "382360"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Карта 7000000000000000: статус Locked(Client)
Последнее использование: 2015-04-27 00:00:00
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`CardDetailResponse`](../../data-types/cards/CardDetailResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `CardDetailData` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`CardDetailData`](../../data-types/cards/CardDetailData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `total_count` | `data.total_count` | `int` | Да | uint, обязательное | Количество записей |
| `result` | `data.result` | `list[CardDetail] | None` | Нет | json, необязательное | Список карт |

#### [`CardDetail`](../../data-types/cards/CardDetail.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `id` | `data.result[].id` | `str` | Да | string, обязательное | Идентификатор карты |
| `contract_id` | `data.result[].contract_id` | `str` | Да | string, обязательное | ID договора |
| `number` | `data.result[].number` | `str` | Да | string, обязательное | Номер карты |
| `status` | `data.result[].status` | `str` | Да | string, обязательное | Статус карты |
| `can_work_offline` | `data.result[].can_work_offline` | `bool` | Да | bool, обязательное | Может работать офлайн |
| `card_auth_type` | `data.result[].card_auth_type` | `str` | Да | string, обязательное | Тип аутентификации карты |
| `comment` | `data.result[].comment` | `str | None` | Нет | string, необязательное | Комментарий к карте |
| `date_last_usage` | `data.result[].date_last_usage` | `datetime | str | None` | Нет | string, необязательное | Дата последнего использования (может быть пустой строкой) |
| `date_released` | `data.result[].date_released` | `datetime | str | None` | Нет | string, необязательное | Дата выпуска карты |
| `servicecenter_last_usage_name` | `data.result[].servicecenter_last_usage_name` | `str | None` | Нет | — | Название АЗС последнего использования |
| `transaction_timeout` | `data.result[].transaction_timeout` | `TransactionTimeout | None` | Нет | json, необязательное | Таймаут транзакции |
| `product` | `data.result[].product` | `str` | Да | string, обязательное | Тип продукта (limit/wallet) |
| `carrier` | `data.result[].carrier` | `str` | Да | string, обязательное | Тип карты (Plastic/Virtual) |
| `available` | `data.result[].available` | `str` | Да | string, обязательное | Доступный лимит или баланс |
| `currency` | `data.result[].currency` | `str` | Да | string, обязательное | Валюта |
| `payment_of_tolls` | `data.result[].payment_of_tolls` | `str` | Да | string, обязательное | Признак оплаты дорожных сборов |
| `mpc` | `data.result[].mpc` | `bool` | Да | bool, обязательное | Признак доступности мобильного профиля карты |
| `pin_reset` | `data.result[].pin_reset` | `int` | Да | uint, обязательное | Количество доступных попыток сброса PIN |
| `pin_counter` | `data.result[].pin_counter` | `int` | Да | uint, обязательное | Счётчик попыток ввода PIN |
| `previous` | `data.result[].previous` | `str | None` | Нет | string, необязательное | ID предыдущей карты |
| `next` | `data.result[].next` | `str | None` | Нет | string, необязательное | ID следующей карты |

#### [`TransactionTimeout`](../../data-types/cards/TransactionTimeout.md) · `data.result[].transaction_timeout`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `type` | `data.result[].transaction_timeout.type` | `int | str | None` | Да | uint, обязательное | Тип таймаута ('H', 'N' или числовое значение) |
| `value` | `data.result[].transaction_timeout.value` | `int | str` | Да | uint, обязательное | Значение таймаута |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Карты с таким `card_id` нет или она принадлежит другому договору. Частая причина — передан номер карты вместо её ID.

**Что делать:** Возьмите `id` карты из `get_cards_v2` для того же договора.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Карта не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении get_card_detail Сообщение сервера: Карта не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.get_card_detail(card_id="  ")
```

SDK отклоняет пустой идентификатор до отправки запроса, чтобы не тратить лимит запросов API. Исключение `RequestValidationError`:

```text
card_id: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Детальная информация по карте». Запрос в спецификации: `GET http://localhost/vip/v1/cards`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- `contract_id` в API обязателен. Если его не передать, SDK подставит договор, выбранный при авторизации.
- Реальный API отличается от спецификации: поле `data.result[].transaction_timeout.type` — в спецификации число, обязательное, фактически `null`, если таймаут не задан. Модель SDK принимает `int \| str \| None`.
- В таблице полей спецификации указано `data.result[].servicecenter_last_usage`, а в примере ответа спецификации и в модели SDK поле называется `data.result[].servicecenter_last_usage_name`.
- В примере ответа спецификации нет обязательных полей `data.result[].mpc`, `data.result[].pin_reset`, `data.result[].pin_counter`; в пример на этой странице добавлены условные значения.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET: http://localhost/vip/v1/cards?contract_id=1-B7C8D
GET: http://localhost/vip/v1/cards?contract_id=1-B7C8D&cache=false
```

## Что важно знать

- `card_id` — внутренний ID карты из `get_cards_v2`, а не 16-значный номер карты.
