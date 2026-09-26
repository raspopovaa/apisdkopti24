---
description: "Список карт договора (API v1): пример client.cards.get_cards_v1() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Список карт договора (API v1)

`client.cards.get_cards_v1()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/get_cards_v1.py)

Получить все карты договора одним запросом через первую версию API. Метод нужен для совместимости; для новых интеграций используйте `get_cards_v2`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/cards` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Список карт договора (API v1): client.cards.get_cards_v1().

Получить все карты договора одним запросом через первую версию API. Метод нужен для
совместимости; для новых интеграций используйте `get_cards_v2`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_cards_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_cards_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.cards.get_cards_v1()
    print(f"Всего карт: {response.total_count}")
    for card in response.result:
        print(f"{card.id}  {card.number}  {card.status}  комментарий: {card.comment}")


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
| `contract_id` | `str | None` | Нет | `None` | ID контракта |
| `cache` | `bool` | Нет | `True` | Кеш карт. false или не задан - данные берутся по прямому запросу из процессинга. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/cards?contract_id=1-2Q4CN99&cache=true HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID контракта |
| `cache` | строка запроса | `true` | string | Нет | Кеш карт. false или не задан - данные берутся по прямому запросу из процессинга. |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardsListResponse`](../../data-types/cards/CardsListResponse.md).
Пример ответа взят из спецификации API 1.1.60; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 3,
    "result": [
      {
        "id": "382359",
        "contract_id": "1-1FLKAJQ",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "can_work_offline": true,
        "card_auth_type": "PIN",
        "comment": "Комментарий",
        "date_expired": "2034-09-30 23:59:59",
        "date_last_usage": "2015-04-27 00:00:00",
        "date_released": "2014-09-24 00:00:00",
        "servicecenter_last_usage_name": "AZS103261",
        "transaction_last_detail": "",
        "transaction_timeout": {
          "type": "H",
          "value": "1"
        },
        "product": "limit",
        "payment_of_tolls": "N"
      },
      {
        "id": "382360",
        "contract_id": "1-1FLKAJQ",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "can_work_offline": true,
        "card_auth_type": "PIN",
        "comment": "Комментарий",
        "date_expired": "2034-09-30 23:59:59",
        "date_last_usage": null,
        "date_released": "2014-09-24 00:00:00",
        "servicecenter_last_usage_name": null,
        "transaction_last_detail": "",
        "transaction_timeout": {
          "type": "N",
          "value": "10"
        },
        "product": "wallet",
        "payment_of_tolls": "N"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Всего карт: 3
382359  7000000000000000  Locked(Client)  комментарий: Комментарий
382360  7000000000000000  Locked(Client)  комментарий: Комментарий
382361  7000000000000000  Active  комментарий: лимиты не работают
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`CardsListResponse`](../../data-types/cards/CardsListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `CardsListData` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`CardsListData`](../../data-types/cards/CardsListData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `total_count` | `data.total_count` | `int` | Да | uint, обязательное | Общее количество найденных карт |
| `result` | `data.result` | `list[CardInfo] | None` | Нет | json, необязательное | Список найденных карт |

#### [`CardInfo`](../../data-types/cards/CardInfo.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `id` | `data.result[].id` | `str` | Да | string, обязательное | Уникальный идентификатор карты |
| `contract_id` | `data.result[].contract_id` | `str` | Да | string, обязательное | Идентификатор договора |
| `number` | `data.result[].number` | `str` | Да | string, обязательное | Номер топливной карты |
| `status` | `data.result[].status` | `str` | Да | string, обязательное | Статус карты (например, Active, Locked(Client)) |
| `can_work_offline` | `data.result[].can_work_offline` | `bool` | Да | bool, обязательное | Может ли карта работать офлайн |
| `card_auth_type` | `data.result[].card_auth_type` | `str` | Да | string, обязательное | Тип авторизации карты (например, PIN) |
| `comment` | `data.result[].comment` | `str | None` | Нет | string, необязательное | Комментарий к карте |
| `date_expired` | `data.result[].date_expired` | `datetime` | Да | string, обязательное | Дата истечения срока действия карты |
| `date_last_usage` | `data.result[].date_last_usage` | `datetime | None` | Нет | string, необязательное | Дата последнего использования карты |
| `date_released` | `data.result[].date_released` | `datetime | None` | Нет | string, необязательное | Дата выпуска карты |
| `servicecenter_last_usage_name` | `data.result[].servicecenter_last_usage_name` | `str | None` | Нет | — | Название последней АЗС, где использовалась карта |
| `transaction_last_detail` | `data.result[].transaction_last_detail` | `str | None` | Нет | string, необязательное | Информация о последней транзакции |
| `transaction_timeout` | `data.result[].transaction_timeout` | `TransactionTimeout | None` | Нет | json, необязательное | Таймаут последней транзакции |
| `product` | `data.result[].product` | `str` | Да | string, обязательное | Тип продукта (limit/wallet) |
| `payment_of_tolls` | `data.result[].payment_of_tolls` | `str` | Да | string, обязательное | Оплата платных дорог ('Y' или 'N') |

#### [`TransactionTimeout`](../../data-types/cards/TransactionTimeout.md) · `data.result[].transaction_timeout`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `type` | `data.result[].transaction_timeout.type` | `int | str | None` | Да | uint, обязательное | Тип таймаута ('H', 'N' или числовое значение) |
| `value` | `data.result[].transaction_timeout.value` | `int | str` | Да | uint, обязательное | Значение таймаута |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Пользователь API не имеет доступа к выбранному договору.

**Что делать:** Проверьте `contract_id` и права пользователя.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Нет доступа к договору"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_cards_v1 Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Список топливных карт (Процессинг)». Запрос в спецификации: `GET http://localhost/vip/v1/cards`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- `contract_id` в API обязателен. Если его не передать, SDK подставит договор, выбранный при авторизации.
- Реальный API отличается от спецификации: поле `data.result[].transaction_timeout.type` — в спецификации число, обязательное, фактически `null`, если таймаут не задан. Модель SDK принимает `int \| str \| None`.
- В таблице полей спецификации указано `data.result[].servicecenter_last_usage`, а в примере ответа спецификации и в модели SDK поле называется `data.result[].servicecenter_last_usage_name`.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET: http://localhost/vip/v1/cards?contract_id=1-B7C8D
GET: http://localhost/vip/v1/cards?contract_id=1-B7C8D&cache=false
```

## Что важно знать

- Метод возвращает все карты сразу, без пагинации: на договорах с тысячами карт ответ большой. Для таких договоров удобнее `get_cards_v2` с `onpage`.
- `cache=True` (по умолчанию в SDK) — данные из кэша карт; `cache=False` — прямой запрос в процессинг за актуальными данными.
