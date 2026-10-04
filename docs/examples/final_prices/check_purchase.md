---
description: "Проверка возможности покупки: пример client.final_prices.check_purchase() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/final_prices.yaml. Не редактируйте вручную. -->

# Проверка возможности покупки

`client.final_prices.check_purchase()` · [справочник метода](../../methods/final_prices.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/final_prices/check_purchase.py)

Проверить до поездки, пройдёт ли покупка набора товаров по карте на выбранной АЗС: хватит ли лимитов и не запрещены ли товары ограничителями.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/checkPurchase` | Нет | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

## Пример

```python
"""Проверка возможности покупки: client.final_prices.check_purchase().

Проверить до поездки, пройдёт ли покупка набора товаров по карте на выбранной АЗС:
хватит ли лимитов и не запрещены ли товары ограничителями.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/final_prices/check_purchase.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/final_prices/check_purchase/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "900042"
POI_ID = "900019"


async def example(client: APIClient) -> None:
    goods = [{"code": "00000000000007", "quantity": 40, "price": 54.35}]
    response = await client.final_prices.check_purchase(card_id=CARD_ID, poi_id=POI_ID, goods=goods)
    print("Покупка возможна" if response.data else "Покупка не пройдёт")


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
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `poi_id` | <code>str</code> | Да | — | ID точки обслуживания. |
| `goods` | <code>list[dict[str, Any]]</code> | Да | — | Массив данных о товарах; для каждого товара указываются `code`, `quantity` и `price`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`CheckPurchaseRequest`](../../data-types/final_prices/CheckPurchaseRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `poi_id` | <code>str</code> | Да | минимальная длина: 1 | ID точки продажи (АЗС) |
| `goods` | <code>list[PurchaseGoodItem]</code> | Да | — | Список товаров для проверки возможности покупки |

#### [`PurchaseGoodItem`](../../data-types/final_prices/PurchaseGoodItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `code` | <code>str</code> | Да | минимальная длина: 1 | Код товара (SKU или PLU на АЗС) |
| `quantity` | <code>float</code> | Да | строго больше: 0 | Количество товара для покупки |
| `price` | <code>float</code> | Да | строго больше: 0 | Цена за единицу товара |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/900042/checkPurchase HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "poi_id": "900019",
  "goods": [
    {
      "code": "00000000000007",
      "quantity": 40.0,
      "price": 54.35
    }
  ]
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `900042` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `poi_id` | тело JSON | `"900019"` | string | Да | ID Точки обслуживания |
| `goods` | тело JSON | `[{"code": "00000000000007", "quantity": 40.0, "price": 54.35}]` | array | Да | Массив данных о продукте |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CheckPurchaseResponse`](../../data-types/final_prices/CheckPurchaseResponse.md).
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
Покупка возможна
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`CheckPurchaseResponse`](../../data-types/final_prices/CheckPurchaseResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>bool</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Карты с таким `card_id` нет в договоре.

**Что делать:** Возьмите `id` карты из `client.cards.get_cards_v2()`.

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
NotFoundError: [404] Объект или маршрут не найден при выполнении check_purchase Сообщение сервера: Карта не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### 403 · `AccessDeniedError`

**Почему:** Процессинг отклонил проверку покупки. Причина — в тексте после «ОТКАЗ.», а не в роли или ключе API.

**Что делать:** Покажите текст сообщения пользователю.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "ОТКАЗ. Недостаточно средств. [Код ошибки: 51]"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении check_purchase Сообщение сервера: ОТКАЗ. Недостаточно средств. [Код ошибки: 51]. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.final_prices.check_purchase(card_id=CARD_ID, poi_id=POI_ID, goods=[{"code": "00000000000007"}])
```

У товара не указаны количество и цена. Исключение `pydantic.ValidationError`:

```text
2 validation errors for CheckPurchaseRequest
goods.0.quantity
  Field required [type=missing]
goods.0.price
  Field required [type=missing]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Каждый товар описывается кодом, количеством и ценой. SDK проверяет их моделью `PurchaseGoodItem` до входа и запроса: лишние поля (например, опечатка `qty`), пустой код и количество или цена не больше нуля дают `ValidationError`.
- SDK отправляет `poi_id` и `goods` телом JSON.
- Отказ процессинга (например, недостаточно средств) приходит как `403 accessDenied` с кодом причины в тексте сообщения, например «ОТКАЗ. Недостаточно средств. [Код ошибки: 51]» — см. также `get_final_prices`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
