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
| `role` | <code>Literal[Supervisor, Regulatory, Driver, Readonly] &#124; None</code> | Нет | `None` | Фильтр по ID роли: `Supervisor`, `Regulatory`, `Driver` или `Readonly`. |
| `user_id` | <code>bool &#124; None</code> | Нет | `None` | Флаг, а не ID: True показывает приглашения, по которым зарегистрировался пользователь. SDK отправляет true или false. |
| `sort` | <code>str &#124; None</code> | Нет | `None` | Поля приглашения через запятую, «-» перед полем — по убыванию. Неизвестное поле SDK отклоняет до запроса: сервер ответил бы 500. |
| `status` | <code>Literal[Active, Expired, Finished] &#124; None</code> | Нет | `None` | Фильтр по статусу приглашения: `Active`, `Expired` или `Finished`. |
| `q` | <code>str &#124; None</code> | Нет | `None` | Поисковый запрос (Ищет email и mobile) |
| `filter` | <code>Mapping[str, object] &#124; None</code> | Нет | `None` | Объект фильтрации ({“status”:”Finished”,”role”:”Driver”}) |
| `page` | <code>int &#124; None</code> | Нет | `None` | Номер страницы (Пагинация) |
| `on_page` | <code>int &#124; None</code> | Нет | `None` | Количество элементов на странице. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`InviteItem`](../../data-types/invites/InviteItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str</code> | Да | — | ID приглашения |
| `user_id` | <code>str &#124; None</code> | Нет | — | ID пользователя, если уже создан |
| `url` | <code>str</code> | Да | — | Ссылка на регистрацию (уникальная, активна 3 дня) |
| `status` | <code>str</code> | Да | — | Технический статус приглашения (Active, Finished и т.п.) |
| `status_name` | <code>str</code> | Да | — | Отображаемое название статуса |
| `role` | <code>str</code> | Да | — | Роль пользователя ('Driver', 'Admin' и т.п.) |
| `role_name` | <code>str</code> | Да | — | Название роли |
| `attempts` | <code>int</code> | Да | — | Количество отправок приглашения |
| `cards` | <code>list[InviteCard]</code> | Да | — | Список карт, связанных с приглашением |
| `initiator` | <code>str</code> | Да | — | Пользователь, создавший приглашение |
| `contracts` | <code>list[InviteContract]</code> | Да | — | Список договоров, привязанных к приглашению |
| `mobile` | <code>str &#124; None</code> | Нет | — | Номер телефона приглашенного |
| `email` | <code>str &#124; None</code> | Нет | — | Email приглашенного |
| `communication_type` | <code>str</code> | Да | — | Тип отправки ('sms', 'email' и т.п.) |
| `sended_at` | <code>int &#124; None</code> | Нет | — | Время отправки (timestamp) |
| `expired_at` | <code>int</code> | Да | — | Время истечения срока действия ссылки (timestamp) |

#### [`InviteCard`](../../data-types/invites/InviteCard.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `sid` | <code>str</code> | Да | — | ID карты (SID) |
| `number` | <code>str</code> | Да | — | Номер карты |
| `product` | <code>str &#124; None</code> | Нет | — | Тип продукта ('wallet' и т.п.) |
| `comment` | <code>str &#124; None</code> | Нет | — | Комментарий к карте (например, имя водителя) |
| `status` | <code>str &#124; None</code> | Нет | — | Технический статус карты |
| `status_name` | <code>str</code> | Да | — | Отображаемое название статуса |
| `contract_id` | <code>str</code> | Да | — | ID договора, к которому относится карта |
| `contract_name` | <code>str</code> | Да | — | Номер договора |

#### [`InviteContract`](../../data-types/invites/InviteContract.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `sid` | <code>str</code> | Да | — | ID договора |
| `number` | <code>str</code> | Да | — | Номер договора |
| `status` | <code>str</code> | Да | — | Технический статус договора |
| `status_name` | <code>str</code> | Да | — | Название статуса |
| `template_id` | <code>str &#124; None</code> | Нет | — | ID шаблона виртуальной карты, если есть |
| `cards_count` | <code>int</code> | Да | — | Количество карт по договору |

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
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>InviteList</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`InviteList`](../../data-types/invites/InviteList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Общее количество приглашений |
| `result` | `data.result` | <code>list[InviteItem] &#124; None</code> | Нет | Список приглашений |

#### [`InviteItem`](../../data-types/invites/InviteItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | ID приглашения |
| `user_id` | `data.result[].user_id` | <code>str &#124; None</code> | Нет | ID пользователя, если уже создан |
| `url` | `data.result[].url` | <code>str</code> | Да | Ссылка на регистрацию (уникальная, активна 3 дня) |
| `status` | `data.result[].status` | <code>str</code> | Да | Технический статус приглашения (Active, Finished и т.п.) |
| `status_name` | `data.result[].status_name` | <code>str</code> | Да | Отображаемое название статуса |
| `role` | `data.result[].role` | <code>str</code> | Да | Роль пользователя ('Driver', 'Admin' и т.п.) |
| `role_name` | `data.result[].role_name` | <code>str</code> | Да | Название роли |
| `attempts` | `data.result[].attempts` | <code>int</code> | Да | Количество отправок приглашения |
| `cards` | `data.result[].cards` | <code>list[InviteCard]</code> | Да | Список карт, связанных с приглашением |
| `initiator` | `data.result[].initiator` | <code>str</code> | Да | Пользователь, создавший приглашение |
| `contracts` | `data.result[].contracts` | <code>list[InviteContract]</code> | Да | Список договоров, привязанных к приглашению |
| `mobile` | `data.result[].mobile` | <code>str &#124; None</code> | Нет | Номер телефона приглашенного |
| `email` | `data.result[].email` | <code>str &#124; None</code> | Нет | Email приглашенного |
| `communication_type` | `data.result[].communication_type` | <code>str</code> | Да | Тип отправки ('sms', 'email' и т.п.) |
| `sended_at` | `data.result[].sended_at` | <code>int &#124; None</code> | Нет | Время отправки (timestamp) |
| `expired_at` | `data.result[].expired_at` | <code>int</code> | Да | Время истечения срока действия ссылки (timestamp) |

#### [`InviteCard`](../../data-types/invites/InviteCard.md) · `data.result[].cards[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `sid` | `data.result[].cards[].sid` | <code>str</code> | Да | ID карты (SID) |
| `number` | `data.result[].cards[].number` | <code>str</code> | Да | Номер карты |
| `product` | `data.result[].cards[].product` | <code>str &#124; None</code> | Нет | Тип продукта ('wallet' и т.п.) |
| `comment` | `data.result[].cards[].comment` | <code>str &#124; None</code> | Нет | Комментарий к карте (например, имя водителя) |
| `status` | `data.result[].cards[].status` | <code>str &#124; None</code> | Нет | Технический статус карты |
| `status_name` | `data.result[].cards[].status_name` | <code>str</code> | Да | Отображаемое название статуса |
| `contract_id` | `data.result[].cards[].contract_id` | <code>str</code> | Да | ID договора, к которому относится карта |
| `contract_name` | `data.result[].cards[].contract_name` | <code>str</code> | Да | Номер договора |

#### [`InviteContract`](../../data-types/invites/InviteContract.md) · `data.result[].contracts[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `sid` | `data.result[].contracts[].sid` | <code>str</code> | Да | ID договора |
| `number` | `data.result[].contracts[].number` | <code>str</code> | Да | Номер договора |
| `status` | `data.result[].contracts[].status` | <code>str</code> | Да | Технический статус договора |
| `status_name` | `data.result[].contracts[].status_name` | <code>str</code> | Да | Название статуса |
| `template_id` | `data.result[].contracts[].template_id` | <code>str &#124; None</code> | Нет | ID шаблона виртуальной карты, если есть |
| `cards_count` | `data.result[].contracts[].cards_count` | <code>int</code> | Да | Количество карт по договору |

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

### 400 · `ValidationError`

**Почему:** Значение фильтра не входит в допустимые; список сервер не сообщает.

**Что делать:** Возьмите значения `role` и `status` из описания параметров.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректное значение."
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении get_invites Сообщение сервера: Некорректное значение.. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.invites.get_invites(sort="bogus")
```

У приглашения нет поля `bogus`; сервер ответил бы `500`. Исключение `RequestValidationError`:

```text
sort: у приглашения нет поля 'bogus'; допустимые поля — атрибуты InviteItem, «-» перед полем — по убыванию
```

```python
await client.invites.get_invites(user_id="user-1")
```

`user_id` — флаг `True`/`False`, а не ID пользователя. Исключение `RequestValidationError`:

```text
user_id — флаг True или False, а не ID пользователя
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Ответ содержит телефоны и email получателей. Не пишите его в журналы целиком.
- `role` — `Supervisor`, `Regulatory`, `Driver` или `Readonly`; `status` — `Active`, `Expired` или `Finished`. `user_id` — не ID, а флаг: `user_id=True` показывает приглашения, по которым уже зарегистрировался пользователь. SDK отправляет его как `true`/`false`.
- `sort` — поля приглашения через запятую, `-` перед полем — по убыванию, например `"-sended_at"`. На неизвестное поле сервер отвечает `500`, а не `400`, поэтому SDK проверяет поля по модели `InviteItem` до запроса.
- `iter_invites()` принимает те же фильтры и сортировку и сам листает страницы.
- Параметр `sort`: неизвестное поле — `500` «Некорректные параметры в запросе», а не `400`. В SDK — проверяет поля по модели `InviteItem` до запроса (`RequestValidationError`).
- Параметр `user_id`: `true`, `false` и произвольная строка принимаются без ошибки; смысл не подтверждён. В SDK — `bool`; отправляет `true`/`false`.
- Поле `data.result[].cards[].product`, `status`: `null` (и пустой `status_name`) у карт в приглашении. Тип в модели SDK: <code>str &#124; None</code>.
