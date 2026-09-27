---
description: "Список приглашений: пример client.invites.get_invites() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/invites.yaml. Не редактируйте вручную. -->

# Список приглашений

`client.invites.get_invites()` · [справочник метода](../../methods/invites.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/invites/get_invites.py)

Посмотреть приглашения с их статусом: действует, истекло или завершено регистрацией.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/invites` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Список приглашений: client.invites.get_invites().

Посмотреть приглашения с их статусом: действует, истекло или завершено регистрацией.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/invites/get_invites.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/invites/get_invites/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.invites.get_invites(status="Active", page=1, on_page=20)
    for invite in response.data.result:
        print(f"{invite.id}  {invite.role_name}  {invite.status_name}  {invite.mobile}")


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
| `role` | `str | None` | Нет | `None` | Фильтр по ID роли: `Supervisor`, `Regulatory`, `Driver` или `Readonly`. |
| `user_id` | `str | None` | Нет | `None` | Отобразить инвайты по которым произошла регистрация пользователя (true) |
| `sort` | `str | None` | Нет | `None` | Сортировка. Сортировка осуществляется формированием строки вида: sort=title,name,-date Поля для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC) |
| `status` | `str | None` | Нет | `None` | Фильтр по статусу приглашения: `Active`, `Expired` или `Finished`. |
| `q` | `str | None` | Нет | `None` | Поисковый запрос (Ищет email и mobile) |
| `filter` | `Mapping[str, object] | None` | Нет | `None` | Объект фильтрации ({“status”:”Finished”,”role”:”Driver”}) |
| `page` | `int | None` | Нет | `None` | Номер страницы (Пагинация) |
| `on_page` | `int | None` | Нет | `None` | Количество элементов на странице. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/invites?status=Active&page=1&on_page=20 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `status` | строка запроса | `Active` | string | Нет | Фильтрация по статусу заявки (Active, Expired, Finished) |
| `page` | строка запроса | `1` | string | Нет | Номер страницы (Пагинация) |
| `on_page` | строка запроса | `20` | string | Нет | Элементов на странице (Пагинация) |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`InviteListResponse`](../../data-types/invites/InviteListResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 1,
    "result": [
      {
        "id": "5ddc1bd27f6e1101316dace6",
        "user_id": "1-FFKR79",
        "url": "https://lk.opti-24.ru/invite/?hash=5ddc1bd27f6e1101316dace6",
        "status": "Finished",
        "status_name": "Завершен",
        "role": "Driver",
        "role_name": "Водитель",
        "attempts": 2,
        "cards": [
          {
            "sid": "79000001",
            "number": "7000000000000000",
            "product": "wallet",
            "comment": "Смирнов Антон Павлович",
            "status": "Active",
            "status_name": "Активна",
            "contract_id": "1-2SY666F",
            "contract_name": "НВ01409999"
          }
        ],
        "initiator": "demo",
        "contracts": [
          {
            "sid": "1-2SY666F",
            "number": "НВ01409999",
            "status": "Active",
            "status_name": "Активен",
            "template_id": null,
            "cards_count": 3
          }
        ],
        "mobile": "79990000000",
        "email": null,
        "communication_type": "sms",
        "sended_at": 1574965330,
        "expired_at": 1574965330
      }
    ]
  },
  "timestamp": 1591147422
}
```

Вывод примера на этом ответе:

```text
5ddc1bd27f6e1101316dace6  Водитель  Завершен  79990000000
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`InviteListResponse`](../../data-types/invites/InviteListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `InviteList` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`InviteList`](../../data-types/invites/InviteList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Общее количество приглашений |
| `result` | `data.result` | `list[InviteItem] | None` | Нет | Список приглашений |

#### [`InviteItem`](../../data-types/invites/InviteItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `str` | Да | ID приглашения |
| `user_id` | `data.result[].user_id` | `str | None` | Нет | ID пользователя, если уже создан |
| `url` | `data.result[].url` | `str` | Да | Ссылка на регистрацию (уникальная, активна 3 дня) |
| `status` | `data.result[].status` | `str` | Да | Технический статус приглашения (Active, Finished и т.п.) |
| `status_name` | `data.result[].status_name` | `str` | Да | Отображаемое название статуса |
| `role` | `data.result[].role` | `str` | Да | Роль пользователя ('Driver', 'Admin' и т.п.) |
| `role_name` | `data.result[].role_name` | `str` | Да | Название роли |
| `attempts` | `data.result[].attempts` | `int` | Да | Количество отправок приглашения |
| `cards` | `data.result[].cards` | `list[InviteCard]` | Да | Список карт, связанных с приглашением |
| `initiator` | `data.result[].initiator` | `str` | Да | Пользователь, создавший приглашение |
| `contracts` | `data.result[].contracts` | `list[InviteContract]` | Да | Список договоров, привязанных к приглашению |
| `mobile` | `data.result[].mobile` | `str | None` | Нет | Номер телефона приглашенного |
| `email` | `data.result[].email` | `str | None` | Нет | Email приглашенного |
| `communication_type` | `data.result[].communication_type` | `str` | Да | Тип отправки ('sms', 'email' и т.п.) |
| `sended_at` | `data.result[].sended_at` | `int | None` | Нет | Время отправки (timestamp) |
| `expired_at` | `data.result[].expired_at` | `int` | Да | Время истечения срока действия ссылки (timestamp) |

#### [`InviteCard`](../../data-types/invites/InviteCard.md) · `data.result[].cards[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `sid` | `data.result[].cards[].sid` | `str` | Да | ID карты (SID) |
| `number` | `data.result[].cards[].number` | `str` | Да | Номер карты |
| `product` | `data.result[].cards[].product` | `str` | Да | Тип продукта ('wallet' и т.п.) |
| `comment` | `data.result[].cards[].comment` | `str | None` | Нет | Комментарий к карте (например, имя водителя) |
| `status` | `data.result[].cards[].status` | `str` | Да | Технический статус карты |
| `status_name` | `data.result[].cards[].status_name` | `str` | Да | Отображаемое название статуса |
| `contract_id` | `data.result[].cards[].contract_id` | `str` | Да | ID договора, к которому относится карта |
| `contract_name` | `data.result[].cards[].contract_name` | `str` | Да | Номер договора |

#### [`InviteContract`](../../data-types/invites/InviteContract.md) · `data.result[].contracts[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `sid` | `data.result[].contracts[].sid` | `str` | Да | ID договора |
| `number` | `data.result[].contracts[].number` | `str` | Да | Номер договора |
| `status` | `data.result[].contracts[].status` | `str` | Да | Технический статус договора |
| `status_name` | `data.result[].contracts[].status_name` | `str` | Да | Название статуса |
| `template_id` | `data.result[].contracts[].template_id` | `str | None` | Нет | ID шаблона виртуальной карты, если есть |
| `cards_count` | `data.result[].contracts[].cards_count` | `int` | Да | Количество карт по договору |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Роль пользователя не позволяет работать с приглашениями.

**Что делать:** Проверьте роль пользователя API.

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_invites Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Ответ содержит телефоны и email получателей. Не пишите его в журналы целиком.
