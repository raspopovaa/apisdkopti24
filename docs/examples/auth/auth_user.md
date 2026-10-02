---
description: "Авторизация и выбор договора: пример client.auth.auth_user() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/auth.yaml. Не редактируйте вручную. -->

# Авторизация и выбор договора

`client.auth.auth_user()` · [справочник метода](../../methods/auth.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/auth/auth_user.py)

Войти в API и выбрать договор, с которым будут работать остальные методы. Обычно этот метод вызывать не нужно: SDK авторизуется сам при первом запросе. Явный вызов полезен, чтобы получить список договоров и данные пользователя.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/authUser` | Нет | Нет | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

## Пример

```python
"""Авторизация и выбор договора: client.auth.auth_user().

Войти в API и выбрать договор, с которым будут работать остальные методы. Обычно этот
метод вызывать не нужно: SDK авторизуется сам при первом запросе. Явный вызов полезен,
чтобы получить список договоров и данные пользователя.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/auth/auth_user.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/auth/auth_user/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    ContractSelectionError,
    EnvironmentCredentialsProvider,
)

# Условные значения: замените своими.
CONTRACT_ID = "1-2Q4CN99"


async def example(client: APIClient) -> None:
    try:
        response = await client.auth.auth_user(contract_id=CONTRACT_ID)
    except ContractSelectionError as error:
        print("Договор не найден. Доступные договоры:")
        for contract_id, number in error.available_contracts:
            print(f"  {contract_id}  {number}")
        return
    print(f"Организация: {response.data.org_name}")
    for contract in response.data.contracts:
        print(f"Договор {contract.number} ({contract.id}), карт: {contract.cards_count}")


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
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Локально выбрать договор по ID после получения ответа. Параметр не отправляется в authUser. |
| `contract_number` | <code>str &#124; None</code> | Нет | `None` | Локально выбрать договор по номеру после получения ответа. Параметр не отправляется в authUser. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/authUser HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

login=demo-login&password=***
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `login` | форма | `demo-login` | string | Да | Логин пользователя |
| `password` | форма | `***` | string | Да | Пароль пользователя, захешированный функцией SHA-512 по стандарту SHS - FIPS 180-4, результат хеширования в нижнем регистре |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`AuthUserResponse`](../../data-types/auth/AuthUserResponse.md).
Пример ответа; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "client_id": "1-2Q45DA8",
    "client_status": "Active",
    "org_name": "Клиент ЛК АО",
    "session_id": "<SESSION_ID>",
    "user_id": "1-2Q468ZB",
    "contracts": [
      {
        "id": "1-2Q4CNBH",
        "number": "ЯР4030436",
        "mpc": true,
        "template_id": "1-3BDZMRJ",
        "cards_count": 11,
        "one_price": false
      },
      {
        "id": "1-2Q4CN99",
        "number": "ЯР4030435",
        "mpc": false,
        "template_id": null,
        "cards_count": 401,
        "one_price": false
      }
    ],
    "role_id": "Supervisor",
    "role_name": "Администратор",
    "read_only": false,
    "user_name": "Иван",
    "user_patronymic": "Иванович",
    "user_surname": "Иванов",
    "last_contract": "1-2Q4CNBH",
    "access": {
      "web": true,
      "api": true,
      "mobile": true
    },
    "email": "user@example.com",
    "phone": "79990000000"
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Организация: Клиент ЛК АО
Договор ЯР4030436 (1-2Q4CNBH), карт: 11
Договор ЯР4030435 (1-2Q4CN99), карт: 401
Договор ЯР4030434 (1-2Q4C2L2), карт: 155
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`AuthUserResponse`](../../data-types/auth/AuthUserResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>AuthUserData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`AuthUserData`](../../data-types/auth/AuthUserData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `client_id` | `data.client_id` | <code>str</code> | Да | ID клиента |
| `client_status` | `data.client_status` | <code>str</code> | Да | Статус пользователя (Active, Blocked, и т.п.) |
| `org_name` | `data.org_name` | <code>str</code> | Да | Наименование организации |
| `session_id` | `data.session_id` | <code>str</code> | Да | ID текущей сессии пользователя |
| `user_id` | `data.user_id` | <code>str</code> | Да | ID пользователя |
| `contracts` | `data.contracts` | <code>list[ContractInfo]</code> | Да | Список доступных договоров |
| `role_id` | `data.role_id` | <code>str</code> | Да | ID роли пользователя (например, Supervisor) |
| `role_name` | `data.role_name` | <code>str</code> | Да | Название роли пользователя (например, Администратор) |
| `read_only` | `data.read_only` | <code>bool</code> | Да | Флаг режима только чтение |
| `user_name` | `data.user_name` | <code>str &#124; None</code> | Нет | Имя пользователя |
| `user_patronymic` | `data.user_patronymic` | <code>str &#124; None</code> | Нет | Отчество пользователя |
| `user_surname` | `data.user_surname` | <code>str &#124; None</code> | Нет | Фамилия пользователя |
| `last_contract` | `data.last_contract` | <code>str &#124; None</code> | Нет | ID последнего использованного договора |
| `access` | `data.access` | <code>AccessRights</code> | Да | Права доступа (ЛК/МП/API) |
| `email` | `data.email` | <code>str</code> | Да | Электронная почта |
| `phone` | `data.phone` | <code>str &#124; None</code> | Нет | Телефон |

#### [`ContractInfo`](../../data-types/auth/ContractInfo.md) · `data.contracts[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.contracts[].id` | <code>str</code> | Да | ID договора |
| `number` | `data.contracts[].number` | <code>str</code> | Да | Номер договора |
| `mpc` | `data.contracts[].mpc` | <code>bool</code> | Да | Возможность выпуска МПК |
| `template_id` | `data.contracts[].template_id` | <code>str &#124; None</code> | Нет | ID шаблона ВК |
| `cards_count` | `data.contracts[].cards_count` | <code>int</code> | Да | Количество карт на договоре |
| `one_price` | `data.contracts[].one_price` | <code>bool</code> | Да | Признак единой цены |

#### [`AccessRights`](../../data-types/auth/AccessRights.md) · `data.access`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `web` | `data.access.web` | <code>bool</code> | Да | Доступ к ЛК |
| `api` | `data.access.api` | <code>bool</code> | Да | Доступ к API |
| `mobile` | `data.access.mobile` | <code>bool</code> | Да | Доступ к МП |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 401 · `NotAuthenticatedError`

**Почему:** Логин или пароль не подходят, либо пользователю закрыт доступ к API.

**Что делать:** Проверьте `API_LOGIN` и `API_PASSWORD`. Доступ к API включается для пользователя в личном кабинете (`access.api` в ответе авторизации).

Ответ API:

```json
{
  "status": {
    "code": 401,
    "errors": [
      {
        "type": "notAuthenticated",
        "message": "Неверный логин или пароль"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotAuthenticatedError: [401] Необходима авторизация при выполнении auth_user Сообщение сервера: Неверный логин или пароль. Подсказка: Проверьте, что пользователь авторизован и передан корректный session_id.
```

### 403 · `AccessDeniedError`

**Почему:** Ключ `api_key` неверный, не активен или запрос пришёл с неразрешённого IP.

**Что делать:** Проверьте `API_KEY` и список разрешённых IP-адресов для ключа.

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
AccessDeniedError: [403] Доступ запрещён при выполнении auth_user Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.auth.auth_user(contract_id=CONTRACT_ID, contract_number="ЯР4030435")
```

Договор выбирают одним способом — по ID или по номеру, но не обоими сразу. Исключение `ContractSelectionError`:

```text
Укажите только один параметр: contract_id или contract_number
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Логин и пароль SDK берёт из поставщика учётных данных. Пароль отправляется как хэш SHA-512 в нижнем регистре — так его ожидает API. На странице и в журналах SDK значение скрыто.
- Если у пользователя несколько договоров, передайте `contract_id` или `contract_number`. Без них SDK выбросит `ContractSelectionError` со списком доступных договоров в `available_contracts`.
- `session_id` из ответа SDK хранит сам и подставляет в следующие запросы. Не выводите его в журналы.
