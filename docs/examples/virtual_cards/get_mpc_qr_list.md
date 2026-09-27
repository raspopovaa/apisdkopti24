---
description: "Список мобильных профилей карт: пример client.virtual_cards.get_mpc_qr_list() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Список мобильных профилей карт

`client.virtual_cards.get_mpc_qr_list()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/get_mpc_qr_list.py)

Получить выпущенные мобильные профили карт (МПК): на каком устройстве выпущен профиль, сколько попыток оплаты разрешено и работает ли он.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/MPC` | Нет | Нет | Нет | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Список мобильных профилей карт: client.virtual_cards.get_mpc_qr_list().

Получить выпущенные мобильные профили карт (МПК): на каком устройстве выпущен профиль,
сколько попыток оплаты разрешено и работает ли он.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/get_mpc_qr_list.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/get_mpc_qr_list/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.get_mpc_qr_list()
    for item in response.data.result:
        state = "работает" if item.use_mpc else "отключён"
        print(f"Карта {item.card_id} на устройстве «{item.device_name}» — {state}")


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
| `contract_id` | `str | None` | Нет | `None` | ID договора; если не указан, возвращаются все МПК клиента |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/MPC HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`MPCListResponse`](../../data-types/virtual_cards/MPCListResponse.md).
Пример ответа условный: спецификация сервиса API QR 1.0.4 описывает только таблицу полей. Структура совпадает с ней и с моделью SDK..

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 1,
    "result": [
      {
        "_id": "64f0c2a1e4b0a1b2c3d4e5f6",
        "client_id": "1-2Q45DA8",
        "user_id": "1-2Q468ZB",
        "login": "79990000000",
        "role": "Driver",
        "contract_id": "1-2Q4CN99",
        "card_id": "15054450",
        "card_number": "7000000000000000",
        "device_id": "device-example",
        "device_name": "Pixel Example",
        "tries": 3,
        "transaction_count": 0,
        "use_mpc": true,
        "created_at": "2026-09-01 10:00:00"
      }
    ]
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Карта 15054450 на устройстве «Pixel Example» — работает
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`MPCListResponse`](../../data-types/virtual_cards/MPCListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `MPCListData` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`MPCListData`](../../data-types/virtual_cards/MPCListData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `total_count` | `data.total_count` | `int` | Да | uint, обязательное | Количество найденных МПК |
| `result` | `data.result` | `list[MPCItem]` | Да | json, обязательное | Список выпущенных МПК |

#### [`MPCItem`](../../data-types/virtual_cards/MPCItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `_id` | `data.result[]._id` | `str` | Да | string, обязательное | ID записи МПК |
| `client_id` | `data.result[].client_id` | `str` | Да | string, обязательное | ID клиента |
| `user_id` | `data.result[].user_id` | `str` | Да | string, обязательное | ID пользователя |
| `login` | `data.result[].login` | `str` | Да | string, обязательное | Логин пользователя |
| `role` | `data.result[].role` | `str` | Да | string, обязательное | Роль пользователя |
| `contract_id` | `data.result[].contract_id` | `str` | Да | string, обязательное | ID договора |
| `card_id` | `data.result[].card_id` | `str` | Да | string, обязательное | ID топливной карты |
| `card_number` | `data.result[].card_number` | `str` | Да | string, обязательное | Номер топливной карты |
| `device_id` | `data.result[].device_id` | `str` | Да | string, обязательное | ID устройства |
| `device_name` | `data.result[].device_name` | `str` | Да | string, обязательное | Название устройства |
| `tries` | `data.result[].tries` | `int` | Да | uint, обязательное | Максимальное число попыток оплаты |
| `transaction_count` | `data.result[].transaction_count` | `int` | Да | uint, обязательное | Число проведённых транзакций |
| `use_mpc` | `data.result[].use_mpc` | `bool` | Да | bool, обязательное | Признак работоспособности МПК |
| `updated_at` | `data.result[].updated_at` | `str | None` | Нет | string, необязательное | Время обновления записи |
| `created_at` | `data.result[].created_at` | `str` | Да | string, обязательное | Время создания записи |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Сервис QR не подключён для клиента или ключа API.

**Что делать:** Уточните подключение сервиса у менеджера.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Доступ запрещён"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_mpc_qr_list Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Метод описан в отдельной спецификации сервиса API QR 1.0.4, а не в основной спецификации 1.1.60. Запрос в спецификации: `GET /v2/MPC`.

## Что важно знать

- Без `contract_id` метод вернёт профили по всем договорам клиента.
