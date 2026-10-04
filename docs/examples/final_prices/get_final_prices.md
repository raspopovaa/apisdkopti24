---
description: "Итоговая цена товаров на АЗС: пример client.final_prices.get_final_prices() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/final_prices.yaml. Не редактируйте вручную. -->

# Итоговая цена товаров на АЗС

`client.final_prices.get_final_prices()` · [справочник метода](../../methods/final_prices.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/final_prices/get_final_prices.py)

Узнать, сколько будет стоить литр топлива по карте на выбранной АЗС с учётом тарифа договора, лимитов и ограничителей карты.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/calculatePrices` | Нет | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

## Пример

```python
"""Итоговая цена товаров на АЗС: client.final_prices.get_final_prices().

Узнать, сколько будет стоить литр топлива по карте на выбранной АЗС с учётом тарифа
договора, лимитов и ограничителей карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/final_prices/get_final_prices.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/final_prices/get_final_prices/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "900042"
POI_ID = "900019"


async def example(client: APIClient) -> None:
    response = await client.final_prices.get_final_prices(
        card_id=CARD_ID, poi_id=POI_ID, goods=["00000000000007", "00000000000009"]
    )
    for item in response.data.goods:
        print(f"{item.code}: {item.price}")


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
| `goods` | <code>list[str]</code> | Да | — | Массив идентификаторов продуктов. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/900042/calculatePrices HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "poi_id": "900019",
  "goods": [
    "00000000000007",
    "00000000000009"
  ]
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `900042` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `poi_id` | тело JSON | `"900019"` | string | Да | ID точки обслуживания |
| `goods` | тело JSON | `["00000000000007", "00000000000009"]` | array | Да | Массив идентикаторов продуктов |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`FinalPricesResponse`](../../data-types/final_prices/FinalPricesResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 2,
    "goods": [
      {
        "code": "00000000000007",
        "price": 48.83
      },
      {
        "code": "00000000000009",
        "price": 54.35
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
00000000000007: 48.83
00000000000009: 54.35
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`FinalPricesResponse`](../../data-types/final_prices/FinalPricesResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>FinalPricesData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`FinalPricesData`](../../data-types/final_prices/FinalPricesData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество товарных позиций в ответе |
| `goods` | `data.goods` | <code>list[FinalPriceItem]</code> | Да | Список товарных позиций с рассчитанными финальными ценами |

#### [`FinalPriceItem`](../../data-types/final_prices/FinalPriceItem.md) · `data.goods[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `data.goods[].code` | <code>str</code> | Да | Код товарной позиции |
| `price` | `data.goods[].price` | <code>float</code> | Да | Финальная цена товара (с учетом всех скидок и тарифов) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** `poi_id` — не числовой ID точки: например, передан `poi_id` из транзакции, номер точки или ID терминала.

**Что делать:** Возьмите числовой `id` точки из `get_azs_list_v1()` или `get_azs_list_v2()`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "АЗС не найдена."
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении get_final_prices Сообщение сервера: АЗС не найдена.. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### 404 · `NotFoundError`

**Почему:** Точка найдена, но сейчас не может провести расчёт по карте.

**Что делать:** Выберите другую точку.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "На АЗС нет рабочих терминалов."
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении get_final_prices Сообщение сервера: На АЗС нет рабочих терминалов.. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### 403 · `AccessDeniedError`

**Почему:** Процессинг отклонил расчёт по этой карте и точке. Причина — в тексте после «ОТКАЗ.», а не в роли или ключе API.

**Что делать:** Покажите текст сообщения пользователю; при необходимости обратитесь к эмитенту карты.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "ОТКАЗ. Обратитесь к персоналу торговой точки для повтора операции. [Код ошибки: 12]"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_final_prices Сообщение сервера: ОТКАЗ. Обратитесь к персоналу торговой точки для повтора операции. [Код ошибки: 12]. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `poi_id` — ID торговой точки из `client.dictionaries.get_azs_list_v2()`, коды товаров — из справочника `Goods`.
- Метод только читает данные, хотя отправляется запросом POST, поэтому пример не спрашивает подтверждение.
- SDK отправляет `poi_id` и `goods` телом JSON: в форме сервер не принимает `goods` как массив и отвечает `400` «Поле goods должно быть массивом».
- ID вида `1-…` (как `poi_id` в транзакциях) метод не принимает — API отвечает `400` «АЗС не найдена». `poi_id` транзакции совпадает с `siebelId` точки в `get_azs_list_v1()`: чтобы узнать цены на АЗС, где была транзакция, найдите точку с таким `siebelId` и передайте её числовой `id`. Номер точки (`contractName`), её код (`contractNumber`) и `terminal_id` метод тоже не принимает.
- Отказ процессинга (например, карта не обслуживается на точке или временно недоступна) тоже приходит как `403 accessDenied`: код причины указан только в тексте сообщения, например «ОТКАЗ. Обратитесь к персоналу торговой точки для повтора операции. [Код ошибки: 12]». Это не связано с правами пользователя API — не проверяйте `api_key` или роль по такому ответу, разбирайте текст сообщения.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
- В примере ответа поля `data.gooods`, `response` заполнены условными значениями.
