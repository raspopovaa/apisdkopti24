---
description: "Заказ счёта на оплату: пример client.contracts.order_invoice() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/contracts.yaml. Не редактируйте вручную. -->

# Заказ счёта на оплату

`client.contracts.order_invoice()` · [справочник метода](../../methods/contracts.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/contracts/order_invoice.py)

Сформировать счёт на пополнение договора на заданную сумму и отправить его на email.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/invoice` | Да | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Заказ счёта на оплату: client.contracts.order_invoice().

Сформировать счёт на пополнение договора на заданную сумму и отправить его на email.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/order_invoice.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/order_invoice/
"""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
AMOUNT = Decimal("50000.00")
EMAIL = "billing@example.org"


async def example(client: APIClient) -> None:
    response = await client.contracts.order_invoice(amount=AMOUNT, email=EMAIL)
    print("Счёт заказан" if response.data else "Сервер не подтвердил заказ")


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
| `amount` | <code>Decimal</code> | Да | — | Сумма счёта в рублях. В API параметр называется `sum`. |
| `email` | <code>str</code> | Да | — | Email-адрес для отправки счёта. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/invoice HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

sum=50000.00&email=billing@example.org
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `sum` | форма | `50000.00` | string | Да | Сумма в рублях |
| `email` | форма | `billing@example.org` | string | Да | Емейл |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`InvoiceOrderResponse`](../../data-types/contracts/InvoiceOrderResponse.md).
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
Счёт заказан
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`InvoiceOrderResponse`](../../data-types/contracts/InvoiceOrderResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>bool</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Сумма или email не прошли проверку сервера.

**Что делать:** Проверьте сумму и адрес получателя.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректная сумма"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении order_invoice Сообщение сервера: Некорректная сумма. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.contracts.order_invoice(amount=Decimal("0"), email=EMAIL)
```

Сумма должна быть больше нуля. Исключение `RequestValidationError`:

```text
amount: значение должно быть больше нуля
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Сумма передаётся как `Decimal`: так SDK не теряет копейки при переводе в строку. В запросе поле называется `sum`.
- SDK не повторяет метод автоматически. При сетевой ошибке проверьте список счетов через `get_invoices()`, прежде чем заказывать снова: повтор создаст второй счёт. Заказанный счёт появляется в списке не сразу — через несколько секунд после заказа его ещё может не быть, поэтому пустой результат сразу после заказа не означает, что заказ не прошёл.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
