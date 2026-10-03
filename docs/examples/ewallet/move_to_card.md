---
description: "Пополнение кошелька карты: пример client.ewallet.move_to_card() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/ewallet.yaml. Не редактируйте вручную. -->

# Пополнение кошелька карты

`client.ewallet.move_to_card()` · [справочник метода](../../methods/ewallet.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/ewallet/move_to_card.py)

Перевести деньги с договора на кошелёк карты.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/moveToCard` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Пополнение кошелька карты: client.ewallet.move_to_card().

Перевести деньги с договора на кошелёк карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/ewallet/move_to_card.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/ewallet/move_to_card/
"""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "11148025"
AMOUNT = Decimal("500.00")


async def example(client: APIClient) -> None:
    response = await client.ewallet.move_to_card(card_id=CARD_ID, amount=AMOUNT)
    print("Перевод выполнен" if response.data else "Сервер не подтвердил перевод")


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
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |
| `card_id` | <code>str</code> | Да | — | ID карты |
| `amount` | <code>Decimal</code> | Да | — | Сумма перевода. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/moveToCard HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-2Q4CN99&card_id=11148025&amount=500.00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | форма | `1-2Q4CN99` | string | Да | ID договора |
| `card_id` | форма | `11148025` | string | Да | ID карты |
| `amount` | форма | `500.00` | string | Да | Сумма |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`MoveToCardResponse`](../../data-types/ewallet/MoveToCardResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": true,
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Перевод выполнен
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`MoveToCardResponse`](../../data-types/ewallet/MoveToCardResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>bool</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Сумма больше доступного остатка договора или карта не на продукте `wallet`.

**Что делать:** Проверьте доступный остаток и продукт карты.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Недостаточно средств на договоре"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении move_to_card Сообщение сервера: Недостаточно средств на договоре. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.ewallet.move_to_card(card_id=CARD_ID, amount=Decimal("-100"))
```

Сумма должна быть больше нуля. Исключение `RequestValidationError`:

```text
amount: значение должно быть больше нуля
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Метод переводит деньги. SDK не повторяет его автоматически: при сетевой ошибке сначала проверьте баланс через `client.contracts.get_contract_data()`.
- Карта должна быть переведена на продукт `wallet` через `set_card_product`.
- На DEMO-стенде метод отвечает `data: true`, но остаток кошелька не меняется: DEMO проверяет только формат запроса. Проверить сам перевод можно только в рабочей среде — чтением остатка после вызова.
- Если на договоре не хватает средств, API отвечает не бизнес-ошибкой, а `500` «У нас возникли технические проблемы. Пожалуйста, попробуйте повторить запрос позднее.» (`ServerError`). Повтор того же перевода не поможет: сначала проверьте остаток договора через `client.contracts.get_contract_data()`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
