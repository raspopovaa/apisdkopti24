---
description: "Список пользователей: пример client.users.get_users() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/users.yaml. Не редактируйте вручную. -->

# Список пользователей

`client.users.get_users()` · [справочник метода](../../methods/users.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/users/get_users.py)

Получить пользователей клиента с ролью, контактами и признаком активности. Поддерживает поиск, фильтр и пагинацию.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/users` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Список пользователей: client.users.get_users().

Получить пользователей клиента с ролью, контактами и признаком активности. Поддерживает
поиск, фильтр и пагинацию.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/users/get_users.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/users/get_users/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.users.get_users(
        filter={"role": "Driver", "active": True}, page=1, on_page=20
    )
    print(f"Пользователей: {response.data.total_count}")
    for user in response.data.result:
        print(f"{user.id}  {user.last_name} {user.first_name}  роль: {user.role.name}")


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
| `sort` | <code>str &#124; None</code> | Нет | `None` | Поля пользователя через запятую, «-» перед полем — по убыванию. Неизвестное поле SDK отклоняет до запроса: сервер молча проигнорировал бы его. |
| `page` | <code>int &#124; None</code> | Нет | `None` | Номер страницы (Пагинация) |
| `on_page` | <code>int &#124; None</code> | Нет | `None` | Количество элементов на странице. |
| `q` | <code>str &#124; None</code> | Нет | `None` | Поисковый запрос (Ищет по Фамилия, Имя, Отчество, Логин, Электронный ящик, Номер мобильного телефона) |
| `filter` | <code>UserFilter &#124; Mapping[str, object] &#124; None</code> | Нет | `None` | Объект фильтрации пользователей, например `{"role": "Driver", "active": true}`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Оставить пользователей с этим привязанным договором. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`UserFilter`](../../data-types/users/UserFilter.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `role` | <code>Literal[Supervisor, Regulatory, Driver, Readonly] &#124; None</code> | Нет | допустимые значения: 'Supervisor', 'Regulatory', 'Driver', 'Readonly'; — | — |
| `active` | <code>bool &#124; None</code> | Нет | — | — |

#### [`UserItem`](../../data-types/users/UserItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str</code> | Да | — | ID пользователя в системе |
| `login` | <code>str</code> | Да | — | Логин пользователя (обычно номер телефона) |
| `first_name` | <code>str</code> | Да | — | Имя пользователя |
| `last_name` | <code>str</code> | Да | — | Фамилия пользователя |
| `middle_name` | <code>str</code> | Да | — | Отчество пользователя |
| `date` | <code>str &#124; None</code> | Да | — | Дата рождения в формате MM/DD/YYYY; может быть null |
| `position` | <code>str</code> | Да | — | Должность или UUID должности |
| `role` | <code>UserRole</code> | Да | — | Роль пользователя |
| `active` | <code>bool &#124; None</code> | Нет | — | Активен ли пользователь |
| `access` | <code>UserAccess</code> | Да | — | Информация о доступах пользователя |
| `mobile_phone` | <code>str &#124; None</code> | Нет | — | Мобильный телефон пользователя |
| `email` | <code>str &#124; None</code> | Нет | — | Email пользователя |
| `contracts` | <code>list[UserContractItem]</code> | Нет | — | Список договоров пользователя |
| `cards` | <code>list[UserCardItem]</code> | Нет | — | Список карт пользователя |

#### [`UsersQuery`](../../data-types/users/UsersQuery.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `sort` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | Сортировка. Сортировка осуществляется формированием строки вида: sort=title,name,-date Поля для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC) |
| `filter` | <code>UserFilter &#124; None</code> | Нет | — | Объект фильтрации ({"role":"Driver", "active":true}) |
| `q` | <code>str &#124; None</code> | Нет | — | Поисковый запрос (Ищет по Фамилия, Имя, Отчество, Логин, Электронный ящик, Номер мобильного телефона) |
| `page` | <code>int &#124; None</code> | Нет | минимум: 1; — | Номер страницы (Пагинация) |
| `on_page` | <code>int &#124; None</code> | Нет | минимум: 1; — | Элементов на странице (Пагинация) |
| `contract_id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | Вывести пользователей с этим привязанным договором |

#### [`UserRole`](../../data-types/users/UserRole.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str</code> | Да | — | ID роли пользователя (Driver, Manager и т.д.) |
| `name` | <code>str</code> | Да | — | Название роли пользователя |

#### [`UserAccess`](../../data-types/users/UserAccess.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `web` | <code>bool</code> | Да | — | Доступ через веб-интерфейс |
| `api` | <code>bool</code> | Да | — | Доступ через API |
| `mobile` | <code>bool</code> | Да | — | Доступ через мобильное приложение |

#### [`UserContractItem`](../../data-types/users/UserContractItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `sid` | <code>str</code> | Да | — | ID договора |
| `number` | <code>str</code> | Да | — | Номер договора |
| `available` | <code>bool &#124; str</code> | Да | — | Доступен ли договор пользователю |
| `template_id` | <code>str &#124; None</code> | Нет | — | ID шаблона договора, если есть |
| `cards_count` | <code>int &#124; None</code> | Нет | — | Количество карт по договору |
| `status` | <code>UserStatus</code> | Да | — | Статус договора |

#### [`UserCardItem`](../../data-types/users/UserCardItem.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `sid` | <code>str</code> | Да | — | SID карты |
| `number` | <code>str</code> | Да | — | Номер карты |
| `mpc` | <code>bool</code> | Да | — | Признак мультикарты |
| `product` | <code>str &#124; None</code> | Нет | — | Тип продукта карты (например, limit, wallet, virtual card) |
| `comment` | <code>str &#124; None</code> | Нет | — | Комментарий к карте |
| `status` | <code>str &#124; None</code> | Нет | — | Статус карты (например, Active, Locked(Client)) |
| `contract_id` | <code>str</code> | Да | — | ID договора, к которому привязана карта |
| `contract_name` | <code>str</code> | Да | — | Название договора |
| `available` | <code>bool &#124; str</code> | Да | — | Доступна ли карта пользователю |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/users?filter={"role":"Driver","active":true}&page=1&on_page=20 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `filter` | строка запроса | `{"role":"Driver","active":true}` | string | Нет | Объект фильтрации ({"role":"Driver", "active":true}) |
| `page` | строка запроса | `1` | string | Нет | Номер страницы (Пагинация) |
| `on_page` | строка запроса | `20` | string | Нет | Элементов на странице (Пагинация) |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`UserListResponse`](../../data-types/users/UserListResponse.md).
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
        "id": "1-T000035",
        "contracts": [
          {
            "sid": "1-T000032",
            "number": "ДГ000000005",
            "parent_contract_id": "",
            "available": true,
            "template_id": null,
            "cards_count": 1,
            "status": {
              "id": "Active",
              "name": "Активен"
            }
          },
          {
            "sid": "1-T000036",
            "number": "ДГ000000006",
            "parent_contract_id": "",
            "available": true,
            "template_id": null,
            "cards_count": 4,
            "status": {
              "id": "Active",
              "name": "Активен"
            }
          }
        ],
        "cards": [
          {
            "sid": "90000006",
            "number": "7000000000000000",
            "mpc": true,
            "product": "limit",
            "carrier": "Virtual Card",
            "comment": "есть пластик, плачу NFC",
            "status": "Active",
            "contract_id": "1-T000036",
            "contract_name": "90000000001",
            "available": true
          }
        ],
        "login": "79990000000",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "date": "07/12/1991",
        "position": "Ведущий дальнобойщик",
        "role": {
          "id": "Driver",
          "name": "Водитель"
        },
        "active": true,
        "access": {
          "web": false,
          "api": false,
          "mobile": true
        },
        "mobile_phone": "79990000000",
        "email": "user@example.com"
      },
      {
        "id": "1-T000038",
        "contracts": [
          {
            "sid": "1-T000031",
            "number": "ДГ000000004",
            "parent_contract_id": "",
            "available": true,
            "template_id": null,
            "cards_count": 1,
            "status": {
              "id": "Active",
              "name": "Активен"
            }
          }
        ],
        "cards": [
          {
            "sid": "90000004",
            "number": "7000000000000000",
            "mpc": true,
            "product": "limit",
            "carrier": "Virtual Card",
            "comment": "",
            "status": "Active",
            "contract_id": "1-T000031",
            "contract_name": "ДГ000000004",
            "available": true
          }
        ],
        "login": "79990000000",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "date": "01/01/1991",
        "position": "Водитель",
        "role": {
          "id": "Driver",
          "name": "Водитель"
        },
        "active": true,
        "access": {
          "web": false,
          "api": false,
          "mobile": true
        },
        "mobile_phone": "79990000000",
        "email": "user@example.com"
      }
    ]
  },
  "timestamp": 1585191856
}
```

Вывод примера на этом ответе:

```text
Пользователей: 2
1-T000035  Иванов Иван  роль: Водитель
1-T000038  Иванов Иван  роль: Водитель
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`UserListResponse`](../../data-types/users/UserListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>UserList &#124; None</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`UserList`](../../data-types/users/UserList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Общее количество пользователей |
| `result` | `data.result` | <code>list[UserItem] &#124; None</code> | Нет | Список пользователей |

#### [`UserItem`](../../data-types/users/UserItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | ID пользователя в системе |
| `login` | `data.result[].login` | <code>str</code> | Да | Логин пользователя (обычно номер телефона) |
| `first_name` | `data.result[].first_name` | <code>str</code> | Да | Имя пользователя |
| `last_name` | `data.result[].last_name` | <code>str</code> | Да | Фамилия пользователя |
| `middle_name` | `data.result[].middle_name` | <code>str</code> | Да | Отчество пользователя |
| `date` | `data.result[].date` | <code>str &#124; None</code> | Да | Дата рождения в формате MM/DD/YYYY; может быть null |
| `position` | `data.result[].position` | <code>str</code> | Да | Должность или UUID должности |
| `role` | `data.result[].role` | <code>UserRole</code> | Да | Роль пользователя |
| `active` | `data.result[].active` | <code>bool &#124; None</code> | Нет | Активен ли пользователь |
| `access` | `data.result[].access` | <code>UserAccess</code> | Да | Информация о доступах пользователя |
| `mobile_phone` | `data.result[].mobile_phone` | <code>str &#124; None</code> | Нет | Мобильный телефон пользователя |
| `email` | `data.result[].email` | <code>str &#124; None</code> | Нет | Email пользователя |
| `contracts` | `data.result[].contracts` | <code>list[UserContractItem]</code> | Нет | Список договоров пользователя |
| `cards` | `data.result[].cards` | <code>list[UserCardItem]</code> | Нет | Список карт пользователя |

#### [`UserRole`](../../data-types/users/UserRole.md) · `data.result[].role`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].role.id` | <code>str</code> | Да | ID роли пользователя (Driver, Manager и т.д.) |
| `name` | `data.result[].role.name` | <code>str</code> | Да | Название роли пользователя |

#### [`UserAccess`](../../data-types/users/UserAccess.md) · `data.result[].access`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `web` | `data.result[].access.web` | <code>bool</code> | Да | Доступ через веб-интерфейс |
| `api` | `data.result[].access.api` | <code>bool</code> | Да | Доступ через API |
| `mobile` | `data.result[].access.mobile` | <code>bool</code> | Да | Доступ через мобильное приложение |

#### [`UserContractItem`](../../data-types/users/UserContractItem.md) · `data.result[].contracts[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `sid` | `data.result[].contracts[].sid` | <code>str</code> | Да | ID договора |
| `number` | `data.result[].contracts[].number` | <code>str</code> | Да | Номер договора |
| `available` | `data.result[].contracts[].available` | <code>bool &#124; str</code> | Да | Доступен ли договор пользователю |
| `template_id` | `data.result[].contracts[].template_id` | <code>str &#124; None</code> | Нет | ID шаблона договора, если есть |
| `cards_count` | `data.result[].contracts[].cards_count` | <code>int &#124; None</code> | Нет | Количество карт по договору |
| `status` | `data.result[].contracts[].status` | <code>UserStatus</code> | Да | Статус договора |

#### [`UserCardItem`](../../data-types/users/UserCardItem.md) · `data.result[].cards[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `sid` | `data.result[].cards[].sid` | <code>str</code> | Да | SID карты |
| `number` | `data.result[].cards[].number` | <code>str</code> | Да | Номер карты |
| `mpc` | `data.result[].cards[].mpc` | <code>bool</code> | Да | Признак мультикарты |
| `product` | `data.result[].cards[].product` | <code>str &#124; None</code> | Нет | Тип продукта карты (например, limit, wallet, virtual card) |
| `comment` | `data.result[].cards[].comment` | <code>str &#124; None</code> | Нет | Комментарий к карте |
| `status` | `data.result[].cards[].status` | <code>str &#124; None</code> | Нет | Статус карты (например, Active, Locked(Client)) |
| `contract_id` | `data.result[].cards[].contract_id` | <code>str</code> | Да | ID договора, к которому привязана карта |
| `contract_name` | `data.result[].cards[].contract_name` | <code>str</code> | Да | Название договора |
| `available` | `data.result[].cards[].available` | <code>bool &#124; str</code> | Да | Доступна ли карта пользователю |

#### [`UserStatus`](../../data-types/users/UserStatus.md) · `data.result[].contracts[].status`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].contracts[].status.id` | <code>str</code> | Да | ID статуса договора, например Active |
| `name` | `data.result[].contracts[].status.name` | <code>str</code> | Да | Название статуса договора, например Активен |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Роль пользователя API не позволяет управлять пользователями.

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_users Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.users.get_users(filter={"status": "Active"})
```

Фильтр поддерживает только поля `role` и `active`. Исключение `pydantic.ValidationError`:

```text
1 validation error for UsersQuery
filter.status
  Extra inputs are not permitted [type=extra_forbidden]
```

```python
await client.users.get_users(filter={"role": "Admin"})
```

Сервер молча вернул бы пустой список. Исключение `pydantic.ValidationError`:

```text
1 validation error for UsersQuery
filter.role
  Input should be 'Supervisor', 'Regulatory', 'Driver' or 'Readonly' [type=literal_error]
```

```python
await client.users.get_users(sort="name")
```

У пользователя нет поля `name`; сервер молча проигнорировал бы сортировку. Исключение `RequestValidationError`:

```text
sort: у пользователя нет поля 'name'; допустимые поля: access, active, cards, contracts, date, email, first_name, id, last_name, login, middle_name, mobile_phone, position, role; «-» перед полем — по убыванию
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Ответ содержит персональные данные: телефоны и email. Не пишите его в журналы целиком.
- `date` (дата рождения) приходит в формате `MM/DD/YYYY` или `null`. У карт пользователя `product` и `status` могут быть `null`.
- `q` ищет по фамилии, имени, отчеству, логину, email и телефону. `contract_id` оставляет пользователей с этим привязанным договором.
- `filter` — `role` (`Supervisor`, `Regulatory`, `Driver` или `Readonly`) и `active` (`True`/`False`). На неизвестную роль сервер молча отвечает пустым списком, поэтому SDK проверяет роль до запроса.
- `sort` — поля пользователя через запятую, `-` перед полем — по убыванию, например `"login,-id"`. Неизвестное поле сервер молча игнорирует, поэтому SDK сверяет поля с моделью `UserItem` до запроса.
- Параметр `sort`, `filter.role`: неизвестное поле сортировки молча игнорируется, неизвестная роль даёт пустой список. В SDK — проверяет поля по модели `UserItem` и роль до запроса.
- Параметр `contract_id`: с ID несуществующего договора вернулся тот же пользователь, что и без фильтра. В SDK — передаёт значение как есть.
- Поле `data.result[].contracts[].cards_count`: поле может отсутствовать у части договоров. Тип в модели SDK: <code>int &#124; None</code>, по умолчанию `None`.
- Поле `data.result[].cards[].product`, `status`: бывает `null`. Тип в модели SDK: <code>str &#124; None</code>.
- Поле `data.result[].cards[].available`, `contracts[].available`: `bool`. Тип в модели SDK: <code>bool &#124; str</code>.
- Поле `data.result[].date`: `null`. Тип в модели SDK: <code>str &#124; None</code>.
