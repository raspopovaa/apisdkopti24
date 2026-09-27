---
description: "Создание приглашения: пример client.invites.create_invite() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/invites.yaml. Не редактируйте вручную. -->

# Создание приглашения

`client.invites.create_invite()` · [справочник метода](../../methods/invites.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/invites/create_invite.py)

Пригласить водителя или другого пользователя зарегистрироваться. Приглашение уходит по SMS или email; ссылку из ответа можно отправить и самостоятельно.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/invites` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Создание приглашения: client.invites.create_invite().

Пригласить водителя или другого пользователя зарегистрироваться. Приглашение уходит по
SMS или email; ссылку из ответа можно отправить и самостоятельно.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/invites/create_invite.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/invites/create_invite/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.invites import InviteCreateRequest

# Условные значения: замените своими.
CONTRACT_ID = "1-2Q4CN99"


async def example(client: APIClient) -> None:
    request = InviteCreateRequest(
        role="Driver", mobile="79990000000", contracts=[{"id": CONTRACT_ID}]
    )
    response = await client.invites.create_invite(data=request, with_send=True)
    print(f"Приглашение {response.data.id}: {response.data.url}")


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
| `data` | `InviteCreateRequest | Mapping[str, object]` | Да | — | Данные приглашения: роль, телефон или email, список карт и список договоров с возможным `template_id`. |
| `with_send` | `bool` | Нет | `True` | — |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`InviteCreateRequest`](../../data-types/invites/InviteCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `role` | `str` | Да | — | ID роли |
| `mobile` | `str | None` | Нет | — | Номер телефона |
| `email` | `str | None` | Нет | — | Email |
| `cards` | `list[str]` | Нет | — | ID прикрепляемых карт |
| `contracts` | `list[_InviteContractRequest]` | Нет | — | Договоры, прикрепляемые после регистрации |

#### [`_InviteContractRequest`](../../data-types/invites/_InviteContractRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | `str` | Да | — | ID договора |
| `template_id` | `str | None` | Нет | — | ID шаблона виртуальной карты |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/invites HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "role": "Driver",
  "mobile": "79990000000",
  "contracts": [
    {
      "id": "1-2Q4CN99"
    }
  ]
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `role` | тело JSON | `"Driver"` | string | Да | ID роли |
| `mobile` | тело JSON | `"79990000000"` | string | Нет | Номер телефона. Обязательный, если не заполнено поле email. |
| `contracts` | тело JSON | `[{"id": "1-2Q4CN99"}]` | array | Нет | Массив договоров, к которым будет привязан пользователь после регистрации. [{“id”:”1-FFFFF”,”template_id”:”1-KKKK”},{“id”:”1-RRRRR”,”template_id”:null}] |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`InviteResponse`](../../data-types/invites/InviteResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "id": "5ddc1bd27f6e1101316dace6",
    "url": "https://lk.opti-24.ru/invite/?hash=5ddc1bd27f6e1101316dace6",
    "attempts": 2,
    "expired_at": 1574965330
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Приглашение 5ddc1bd27f6e1101316dace6: https://lk.opti-24.ru/invite/?hash=5ddc1bd27f6e1101316dace6
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`InviteResponse`](../../data-types/invites/InviteResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `InviteActionResult` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`InviteActionResult`](../../data-types/invites/InviteActionResult.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.id` | `str` | Да | ID приглашения |
| `url` | `data.url` | `str` | Да | Ссылка на приглашение |
| `attempts` | `data.attempts` | `int` | Да | Количество попыток отправки |
| `expired_at` | `data.expired_at` | `int` | Да | Дата истечения срока действия ссылки (timestamp) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Указана роль, которой нет у договора, или неверный формат телефона.

**Что делать:** Проверьте `role` и номер телефона.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректная роль"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении create_invite Сообщение сервера: Некорректная роль. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.invites.create_invite(data={"role": "Driver"})
```

Не указан ни телефон, ни email получателя. Исключение `pydantic.ValidationError`:

```text
1 validation error for InviteCreateRequest
  Value error, Необходимо указать mobile или email [type=value_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Нужен `mobile` или `email`: модель запроса не пропустит приглашение без получателя.
- `with_send=False` создаёт приглашение без отправки SMS или письма — ссылку из ответа можно передать своим способом.
