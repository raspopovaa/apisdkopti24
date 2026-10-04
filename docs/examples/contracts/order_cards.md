---
description: "Заказ новых карт: пример client.contracts.order_cards() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/contracts.yaml. Не редактируйте вручную. -->

# Заказ новых карт

`client.contracts.order_cards()` · [справочник метода](../../methods/contracts.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/contracts/order_cards.py)

Заказать выпуск пластиковых карт с получением в офисе продаж.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/orderCards` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Заказ новых карт: client.contracts.order_cards().

Заказать выпуск пластиковых карт с получением в офисе продаж.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/order_cards.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/order_cards/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
OFFICE_ID = "1-13HF"


async def example(client: APIClient) -> None:
    response = await client.contracts.order_cards(count=5, office_id=OFFICE_ID)
    print("Заявка принята" if response.data else "Сервер не подтвердил заявку")


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
| `count` | <code>int</code> | Да | — | Количество заказываемых карт. |
| `office_id` | <code>str</code> | Да | — | ID офиса продаж из справочника `Office`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/orderCards HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

count=5&office_id=1-13HF
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `count` | форма | `5` | string | Да | Количество карт |
| `office_id` | форма | `1-13HF` | string | Да | ID офиса продаж (Берется из справочника Office) |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`OrderCardsResponse`](../../data-types/contracts/OrderCardsResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": true,
  "timestamp": 1591167315
}
```

Вывод примера на этом ответе:

```text
Заявка принята
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`OrderCardsResponse`](../../data-types/contracts/OrderCardsResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>bool</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Офиса с таким ID нет в справочнике `Office`.

**Что делать:** Возьмите ID из справочника `Office`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Офис продаж не найден"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении order_cards Сообщение сервера: Офис продаж не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.contracts.order_cards(count=0, office_id=OFFICE_ID)
```

Количество карт должно быть больше нуля. Исключение `RequestValidationError`:

```text
count должен быть больше нуля
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- ID офиса продаж берётся из справочника `Office`: `client.dictionaries.get_dictionary(name="Office")`.
- SDK не повторяет метод автоматически, чтобы не заказать карты дважды.
- Проверить заказ через API нельзя: метода со списком заказов карт нет, а ответ содержит только `data: true`. При сетевой ошибке с неизвестным результатом уточните заказ в личном кабинете или у менеджера, прежде чем повторять.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
