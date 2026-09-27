---
description: "Выпуск виртуальной карты по типу или шаблону: пример client.virtual_cards.release_virtual_card() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Выпуск виртуальной карты по типу или шаблону

`client.virtual_cards.release_virtual_card()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/release_virtual_card.py)

Выпустить виртуальную карту, указав её тип (`limit` или `wallet`) либо шаблон виртуальной карты.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/release` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Выпуск виртуальной карты по типу или шаблону: client.virtual_cards.release_virtual_card().

Выпустить виртуальную карту, указав её тип (`limit` или `wallet`) либо шаблон
виртуальной карты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/release_virtual_card.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/release_virtual_card/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.release_virtual_card(type_="wallet")
    print(f"Выпущена карта {response.data.id}, статус {response.data.status}")


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
| `type_` | `str | None` | Нет | `None` | Тип карты: `limit` — лимитная схема, `wallet` — электронный кошелёк. Обязателен, если не указан `template_id`; не передаётся, если указан `template_id`. |
| `template_id` | `str | None` | Нет | `None` | ID шаблона ВК Обязателен, если не указан type - Тип карты Не указывать, если указан type - Тип карты |
| `user_id` | `str | None` | Нет | `None` | ID пользователя (Если указан, то выпущенная карта будет привязана к указанному клиенту) |
| `contract_id` | `str | None` | Нет | `None` | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`VirtualCardReleaseRequest`](../../data-types/virtual_cards/VirtualCardReleaseRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | минимальная длина: 1; — | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `type` | `Literal[limit, wallet] | None` | Нет | допустимые значения: 'limit', 'wallet'; — | Тип карты (limit – лимитная схема, wallet – электронный кошелек) Обязателен, если не указан template_id - ID шаблона Не указывать, если указан template_id - ID шаблона |
| `template_id` | `str | None` | Нет | минимальная длина: 1; — | ID шаблона ВК Обязателен, если не указан type - Тип карты Не указывать, если указан type - Тип карты |
| `user_id` | `str | None` | Нет | минимальная длина: 1; — | ID пользователя (Если указан, то выпущенная карта будет привязана к указанному клиенту) |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/release HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

type=wallet
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `type` | форма | `wallet` | string | Нет | Тип карты (limit – лимитная схема, wallet – электронный кошелек) Обязателен, если не указан template_id - ID шаблона Не указывать, если указан template_id - ID шаблона |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`VirtualCardResponse`](../../data-types/virtual_cards/VirtualCardResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "id": "15054450",
    "number": "7000000000000000",
    "carrier": "Virtual Card",
    "product": "wallet",
    "status": "Active"
  },
  "timestamp": 1588540016
}
```

Вывод примера на этом ответе:

```text
Выпущена карта 15054450, статус Active
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`VirtualCardResponse`](../../data-types/virtual_cards/VirtualCardResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `StatusModel` | Да | Статус ответа от сервера |
| `data` | `data` | `VirtualCardData` | Да | Информация о выпущенной виртуальной карте |
| `timestamp` | `timestamp` | `int | None` | Нет | Время ответа сервера в формате Unix Timestamp |

#### [`StatusModel`](../../data-types/virtual_cards/StatusModel.md) · `status`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `status.code` | `int` | Да | Код статуса ответа (200 — успешно, иное — ошибка) |
| `errors` | `status.errors` | `list[dict[str, object]] | None` | Нет | Массив ошибок операции |

#### [`VirtualCardData`](../../data-types/virtual_cards/VirtualCardData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.id` | `str` | Да | ID виртуальной карты |
| `number` | `data.number` | `str | None` | Нет | Номер виртуальной карты |
| `carrier` | `data.carrier` | `str | None` | Нет | Тип носителя, обычно 'Virtual Card' |
| `product` | `data.product` | `str | None` | Нет | Тип продукта карты ('wallet' или 'limit') |
| `status` | `data.status` | `str | None` | Нет | Статус карты (например, 'Active', 'Blocked', 'Pending') |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Для договора не подключён выпуск виртуальных карт.

**Что делать:** Обратитесь к менеджеру договора.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Выпуск виртуальных карт недоступен"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении release_virtual_card Сообщение сервера: Выпуск виртуальных карт недоступен. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.virtual_cards.release_virtual_card(type_="wallet", template_id="1-3BE470B")
```

Нельзя одновременно передать тип карты и шаблон. Исключение `pydantic.ValidationError`:

```text
1 validation error for VirtualCardReleaseRequest
  Value error, Необходимо указать ровно один параметр: type или template_id [type=value_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Нужно указать ровно один источник: `type_` или `template_id`. SDK проверяет это до отправки запроса.
