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
CARD_ID = "989666"
POI_ID = "366038"


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
| `card_id` | `str` | Да | — | Идентификатор топливной карты. |
| `poi_id` | `str` | Да | — | ID точки обслуживания. |
| `goods` | `list[str]` | Да | — | Массив идентификаторов продуктов. |
| `contract_id` | `str | None` | Нет | `None` | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/989666/calculatePrices HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

poi_id=366038&goods=00000000000007&goods=00000000000009
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `989666` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `poi_id` | форма | `366038` | string | Да | ID точки обслуживания |
| `goods` | форма | `00000000000007` | string | Да | Массив идентикаторов продуктов |
| `goods` | форма | `00000000000009` | string | Да | Массив идентикаторов продуктов |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

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
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `FinalPricesData` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`FinalPricesData`](../../data-types/final_prices/FinalPricesData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Количество товарных позиций в ответе |
| `goods` | `data.goods` | `list[FinalPriceItem]` | Да | Список товарных позиций с рассчитанными финальными ценами |

#### [`FinalPriceItem`](../../data-types/final_prices/FinalPriceItem.md) · `data.goods[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `data.goods[].code` | `str` | Да | Код товарной позиции |
| `price` | `data.goods[].price` | `float` | Да | Финальная цена товара (с учетом всех скидок и тарифов) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Точки с таким `poi_id` нет или она не принимает карты.

**Что делать:** Возьмите `id` точки из `get_azs_list_v2()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Торговая точка не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении get_final_prices Сообщение сервера: Торговая точка не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `poi_id` — ID торговой точки из `client.dictionaries.get_azs_list_v2()`, коды товаров — из справочника `Goods`.
- Метод только читает данные, хотя отправляется запросом POST, поэтому пример не спрашивает подтверждение.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
- В примере ответа поля `data.gooods`, `response` заполнены условными значениями.
