---
description: "Смена продукта карты: пример client.ewallet.set_card_product() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/ewallet.yaml. Не редактируйте вручную. -->

# Смена продукта карты

`client.ewallet.set_card_product()` · [справочник метода](../../methods/ewallet.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/ewallet/set_card_product.py)

Перевести карты на электронный кошелёк (`wallet`) или вернуть на лимитную схему (`limit`). У кошелька свой счёт, который пополняется с договора.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/setCardProduct` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Смена продукта карты: client.ewallet.set_card_product().

Перевести карты на электронный кошелёк (`wallet`) или вернуть на лимитную схему
(`limit`). У кошелька свой счёт, который пополняется с договора.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/ewallet/set_card_product.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/ewallet/set_card_product/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "11148025"


async def example(client: APIClient) -> None:
    response = await client.ewallet.set_card_product(card_ids=[CARD_ID], product="wallet")
    print(f"Изменены карты: {', '.join(response.data or [])}")


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
| `contract_id` | `str | None` | Нет | `None` | ID договора |
| `card_ids` | `list[str]` | Да | — | ID карт ([“424234”,”423423”]) |
| `product` | `Literal[wallet, limit]` | Да | — | Тип продукта: `wallet` или `limit`. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/setCardProduct HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-2Q4CN99&card_id=["11148025"]&product=wallet
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | форма | `1-2Q4CN99` | string | Да | ID договора |
| `card_id` | форма | `["11148025"]` | string | Да | ID карт ([“424234”,”423423”]) |
| `product` | форма | `wallet` | string | Да | Тип продукта (wallet или limit) |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`SetCardProductResponse`](../../data-types/ewallet/SetCardProductResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    "11148025"
  ],
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Изменены карты: 11148025
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`SetCardProductResponse`](../../data-types/ewallet/SetCardProductResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `list[str] | None` | Нет | ID карт с изменённым типом продукта |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Роль пользователя не разрешает менять продукт карт.

**Что делать:** Проверьте роль пользователя API.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Недостаточно прав"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении set_card_product Сообщение сервера: Недостаточно прав. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.ewallet.set_card_product(card_ids=[CARD_ID], product="credit")
```

Допустимы только продукты `wallet` и `limit`. Исключение `ValueError`:

```text
product должен быть равен 'wallet' или 'limit'
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Список карт SDK отправляет одной строкой JSON-массива в поле `card_id`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
