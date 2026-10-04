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
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID контракта |
| `cache` | <code>bool</code> | Нет | `True` | Кеш карт. false или не задан - данные берутся по прямому запросу из процессинга. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/cards?contract_id=1-T000025&cache=true HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-T000025` | string | Да | ID контракта |
| `cache` | строка запроса | `true` | string | Нет | Кеш карт. false или не задан - данные берутся по прямому запросу из процессинга. |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardsListResponse`](../../data-types/cards/CardsListResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 2,
    "result": [
      {
        "id": "900020",
        "group": null,
        "contract_id": "1-T000002",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "comment": "Комментарий",
        "product": "limit",
        "carrier": "Virtual Card",
        "payment_of_tolls": "N",
        "sync_group_state": ""
      },
      {
        "id": "900021",
        "group": "1-2GRP7XQ",
        "contract_id": "1-T000002",
        "number": "7000000000000000",
        "status": "Active",
        "comment": "",
        "product": "wallet",
        "carrier": "Plastic",
        "payment_of_tolls": "Y",
        "sync_group_state": "Синхронизирована"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Всего карт: 2
900020  7000000000000000  Locked(Client)  комментарий: Комментарий
900021  7000000000000000  Active  комментарий:
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`CardsListResponse`](../../data-types/cards/CardsListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>CardsListData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`CardsListData`](../../data-types/cards/CardsListData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Общее количество найденных карт |
| `result` | `data.result` | <code>list[CardInfo] &#124; None</code> | Нет | Список найденных карт |

#### [`CardInfo`](../../data-types/cards/CardInfo.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Уникальный идентификатор карты |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | Идентификатор договора |
| `number` | `data.result[].number` | <code>str</code> | Да | Номер топливной карты |
| `status` | `data.result[].status` | <code>str</code> | Да | Статус карты (например, Active, Locked(Client)) |
| `can_work_offline` | `data.result[].can_work_offline` | <code>bool &#124; None</code> | Нет | Может ли карта работать офлайн |
| `card_auth_type` | `data.result[].card_auth_type` | <code>str &#124; None</code> | Нет | Тип авторизации карты (например, PIN) |
| `comment` | `data.result[].comment` | <code>str &#124; None</code> | Нет | Комментарий к карте |
| `date_expired` | `data.result[].date_expired` | <code>datetime &#124; None</code> | Нет | Дата истечения срока действия карты |
| `date_last_usage` | `data.result[].date_last_usage` | <code>datetime &#124; None</code> | Нет | Дата последнего использования карты |
| `date_released` | `data.result[].date_released` | <code>datetime &#124; None</code> | Нет | Дата выпуска карты |
| `servicecenter_last_usage_name` | `data.result[].servicecenter_last_usage_name` | <code>str &#124; None</code> | Нет | Название последней АЗС, где использовалась карта |
| `transaction_last_detail` | `data.result[].transaction_last_detail` | <code>str &#124; None</code> | Нет | Информация о последней транзакции |
| `transaction_timeout` | `data.result[].transaction_timeout` | <code>TransactionTimeout &#124; None</code> | Нет | Таймаут последней транзакции |
| `product` | `data.result[].product` | <code>str</code> | Да | Тип продукта (limit/wallet) |
| `payment_of_tolls` | `data.result[].payment_of_tolls` | <code>str</code> | Да | Оплата платных дорог ('Y' или 'N') |

#### [`TransactionTimeout`](../../data-types/cards/TransactionTimeout.md) · `data.result[].transaction_timeout`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `type` | `data.result[].transaction_timeout.type` | <code>int &#124; str &#124; None</code> | Да | Единица таймаута: буквенный код (например, H, D, M) или null, если не задан |
| `value` | `data.result[].transaction_timeout.value` | <code>int &#124; str</code> | Да | Значение таймаута (число единиц) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

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

## Что важно знать

- Метод возвращает все карты сразу, без пагинации: на договорах с тысячами карт ответ большой. Для таких договоров удобнее `get_cards_v2` с `onpage`.
- `cache=True` (по умолчанию в SDK) — данные из кэша карт; `cache=False` — прямой запрос в процессинг за актуальными данными.
- В ответе нет `can_work_offline`, `card_auth_type`, `date_expired` и дат использования: в модели они остаются `None`. Эти данные возвращает `get_card_detail()`.
- API присылает также `group`, `carrier` (`Plastic` или `Virtual Card`) и `sync_group_state`; в модели SDK их нет, они доступны через `card.model_extra`.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
- Поле `data.result[].can_work_offline`, `card_auth_type`, `date_expired`: поля могут отсутствовать. Тип в модели SDK: необязательные, по умолчанию `None`.
