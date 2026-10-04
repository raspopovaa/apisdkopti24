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
CONTRACT_ID = "1-T000025"


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
| `data` | <code>InviteCreateRequest &#124; Mapping[str, object]</code> | Да | — | Данные приглашения: роль, телефон или email, список карт и список договоров с возможным `template_id`. |
| `with_send` | <code>bool</code> | Нет | `True` | — |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`InviteCreateRequest`](../../data-types/invites/InviteCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `role` | <code>Literal[Driver, Supervisor]</code> | Да | допустимые значения: 'Driver', 'Supervisor' | ID роли |
| `mobile` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | Номер телефона |
| `email` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | Email |
| `cards` | <code>list[str]</code> | Нет | — | ID прикрепляемых карт |
| `contracts` | <code>list[&#95;InviteContractRequest]</code> | Нет | — | Договоры, прикрепляемые после регистрации |

#### [`_InviteContractRequest`](../../data-types/invites/_InviteContractRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str</code> | Да | — | ID договора |
| `template_id` | <code>str &#124; None</code> | Нет | — | ID шаблона виртуальной карты |

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
      "id": "1-T000025"
    }
  ]
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `role` | тело JSON | `"Driver"` | string | Да | ID роли |
| `mobile` | тело JSON | `"79990000000"` | string | Нет | Номер телефона. Обязательный, если не заполнено поле email. |
| `contracts` | тело JSON | `[{"id": "1-T000025"}]` | array | Нет | Массив договоров, к которым будет привязан пользователь после регистрации. [{“id”:”1-FFFFF”,”template_id”:”1-KKKK”},{“id”:”1-RRRRR”,”template_id”:null}] |

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
    "id": "000000000000000000000001",
    "url": "https://lk.opti-24.ru/invite/?hash=000000000000000000000001",
    "attempts": 2,
    "expired_at": 1574965330
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Приглашение 000000000000000000000001: https://lk.opti-24.ru/invite/?hash=000000000000000000000001
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`InviteResponse`](../../data-types/invites/InviteResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>InviteActionResult</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`InviteActionResult`](../../data-types/invites/InviteActionResult.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.id` | <code>str</code> | Да | ID приглашения |
| `url` | `data.url` | <code>str</code> | Да | Ссылка на приглашение |
| `attempts` | `data.attempts` | <code>int</code> | Да | Количество попыток отправки |
| `expired_at` | `data.expired_at` | <code>int</code> | Да | Дата истечения срока действия ссылки (timestamp) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Неверный формат телефона.

**Что делать:** Проверьте номер телефона.

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
ValidationError: [400] Некорректные параметры запроса при выполнении create_invite Сообщение сервера: Некорректное значение.. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
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

```python
await client.invites.create_invite(data={"role": "Readonly", "mobile": "79990000000"})
```

Приглашение принимает только роли `Driver` и `Supervisor`. Исключение `pydantic.ValidationError`:

```text
1 validation error for InviteCreateRequest
role
  Input should be 'Driver' or 'Supervisor' [type=literal_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Нужен `mobile` или `email`: модель запроса не пропустит приглашение без получателя, с пустой строкой или с неверным адресом email.
- `role` — `Driver` или `Supervisor`: другие роли сервер отклоняет ответом `400` без списка допустимых, поэтому модель запроса проверяет роль до отправки.
- `with_send=False` создаёт приглашение без отправки SMS или письма — ссылку из ответа можно передать своим способом.
- Приглашение без привязанных карт и без шаблона виртуальной карты API не отправляет: отвечает `500` «Приглашение не готово к отправке».
- Формат `mobile` в приглашении отличается от `create_user`: здесь API принимает номер с `+` (`+79990000000`) и без ведущей `8`, тогда как `create_user` требует ровно 11–13 цифр без `+`. Не используйте один и тот же способ нормализации номера для обоих методов.
- `attempts` в ответе — сколько отправок приглашения осталось на день: у приглашения без отправки — `3`, с отправкой — `2`. Следующую отправку (`resend_invite`, `prolong_invite(with_send=True)`) API примет не раньше чем через минуту, иначе ответит `429`.
- Параметр `role`: принимаются `Driver` и `Supervisor`; другое значение — `400` «Некорректное значение.» без списка допустимых. В SDK — принимает только `Driver` и `Supervisor` (`ValidationError` до запроса).
