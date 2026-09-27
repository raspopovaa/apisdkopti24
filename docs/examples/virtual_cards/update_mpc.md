---
description: "Смена PIN или перевыпуск ключей МПК: пример client.virtual_cards.update_mpc() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Смена PIN или перевыпуск ключей МПК

`client.virtual_cards.update_mpc()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/update_mpc.py)

Сменить PIN мобильного профиля карты. Без нового PIN метод перевыпускает ключи оплаты.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/updateMPC` | Да | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Смена PIN или перевыпуск ключей МПК: client.virtual_cards.update_mpc().

Сменить PIN мобильного профиля карты. Без нового PIN метод перевыпускает ключи оплаты.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/update_mpc.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/update_mpc/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "15054450"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.update_mpc(card_id=CARD_ID, pin="4815", new_pin="162342")
    print("PIN изменён" if response.data else "Сервер не подтвердил изменение")


async def main() -> None:
    answer = input("Вызов изменяет данные на реальном API. Продолжить? [yes/no] ")
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
| `card_id` | `str` | Да | — | ID карты |
| `pin` | `str` | Да | — | Текущий PIN мобильного профиля из 4–8 цифр. |
| `new_pin` | `str | None` | Нет | `None` | Новый PIN из 4–8 цифр. Если не передан, API перевыпускает ключи оплаты без смены PIN. |
| `contract_id` | `str | None` | Нет | `None` | ID договора |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`MPCUpdateRequest`](../../data-types/virtual_cards/MPCUpdateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `pin` | `str` | Да | шаблон: '^[0-9]{4,8}$' | Пин-код МПК |
| `new_pin` | `str | None` | Нет | шаблон: '^[0-9]{4,8}$'; — | Новый пин-код; если не указан |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/15054450/updateMPC HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

pin=***&new_pin=***
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `15054450` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `pin` | форма | `***` | string | Да | Пин-код МПК |
| `new_pin` | форма | `***` | string | Нет | Новый пин-код; если не указан |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`MPCActionResponse`](../../data-types/virtual_cards/MPCActionResponse.md).
Пример ответа условный, по спецификации сервиса API QR 1.0.4..

```json
{
  "status": {
    "code": 200
  },
  "data": true,
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
PIN изменён
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`MPCActionResponse`](../../data-types/virtual_cards/MPCActionResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `bool` | Да | bool, обязательное | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Текущий PIN указан неверно.

**Что делать:** Проверьте текущий PIN.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Неверный PIN МПК"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении update_mpc Сообщение сервера: Ответ API с ошибкой содержал конфиденциальные данные. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.virtual_cards.update_mpc(card_id=CARD_ID, pin="4815", new_pin="1")
```

Новый PIN должен состоять из 4–8 цифр. Исключение `pydantic.ValidationError`:

```text
1 validation error for MPCUpdateRequest
new_pin
  String should match pattern '^[0-9]{4,8}$' [type=string_pattern_mismatch]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Метод описан в отдельной спецификации сервиса API QR 1.0.4, а не в основной спецификации 1.1.60. Запрос в спецификации: `POST /v2/cards/{card_id}/updateMPC`.
- `contract_id` в API обязателен. Если его не передать, SDK подставит договор, выбранный при авторизации.
