---
description: "Выпуск виртуальной карты: пример client.virtual_cards.create_virtual_card() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Выпуск виртуальной карты

`client.virtual_cards.create_virtual_card()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/create_virtual_card.py)

Выпустить виртуальную карту для пользователя. По спецификации для выпуска у пользователя API должен быть указан номер телефона.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Выпуск виртуальной карты: client.virtual_cards.create_virtual_card().

Выпустить виртуальную карту для пользователя. По спецификации для выпуска у пользователя
API должен быть указан номер телефона.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/create_virtual_card.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/create_virtual_card/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
USER_ID = "1-2Q468ZB"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.create_virtual_card(user_id=USER_ID)
    card = response.data
    print(f"Карта {card.id}: {card.carrier}, продукт {card.product}, статус {card.status}")


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
| `user_id` | `str | None` | Нет | `None` | ID пользователя (Если указан, то выпуск карты производится с использванием данных указанного клиента пользователя) |
| `contract_id` | `str | None` | Нет | `None` | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `template_id` | `str | None` | Нет | `None` | ID шаблона ВК (Не обязателен, если шаблон ВК был ранее закреплен за пользователем) |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`VirtualCardCreateRequest`](../../data-types/virtual_cards/VirtualCardCreateRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | минимальная длина: 1; — | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `template_id` | `str | None` | Нет | минимальная длина: 1; — | ID шаблона ВК (Не обязателен, если шаблон ВК был ранее закреплен за пользователем) |
| `user_id` | `str | None` | Нет | минимальная длина: 1; — | ID пользователя (Если указан, то выпуск карты производится с использванием данных указанного клиента пользователя) |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

user_id=1-2Q468ZB
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `user_id` | форма | `1-2Q468ZB` | string | Нет | ID пользователя (Если указан, то выпуск карты производится с использванием данных указанного клиента пользователя) |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`VirtualCardResponse`](../../data-types/virtual_cards/VirtualCardResponse.md).
Пример ответа взят из спецификации API 1.1.60.

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
Карта 15054450: Virtual Card, продукт wallet, статус Active
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`VirtualCardResponse`](../../data-types/virtual_cards/VirtualCardResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `StatusModel` | Да | — | Статус ответа от сервера |
| `data` | `data` | `VirtualCardData` | Да | — | Информация о выпущенной виртуальной карте |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Время ответа сервера в формате Unix Timestamp |

#### [`StatusModel`](../../data-types/virtual_cards/StatusModel.md) · `status`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `code` | `status.code` | `int` | Да | — | Код статуса ответа (200 — успешно, иное — ошибка) |
| `errors` | `status.errors` | `list[dict[str, object]] | None` | Нет | — | Массив ошибок операции |

#### [`VirtualCardData`](../../data-types/virtual_cards/VirtualCardData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `id` | `data.id` | `str` | Да | string, обязательное | ID виртуальной карты |
| `number` | `data.number` | `str | None` | Нет | string, необязательное | Номер виртуальной карты |
| `carrier` | `data.carrier` | `str | None` | Нет | string, необязательное | Тип носителя, обычно 'Virtual Card' |
| `product` | `data.product` | `str | None` | Нет | string, необязательное | Тип продукта карты ('wallet' или 'limit') |
| `status` | `data.status` | `str | None` | Нет | string, необязательное | Статус карты (например, 'Active', 'Blocked', 'Pending') |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Для выпуска карты у пользователя должен быть номер телефона.

**Что делать:** Проверьте данные пользователя в `client.users.get_users()`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "У пользователя не указан телефон"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении create_virtual_card Сообщение сервера: У пользователя не указан телефон. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Запрос на выпуск виртуальной карты». Запрос в спецификации: `POST http://localhost/vip/v2/cards`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- Описание в спецификации: «Администратор API может выпускать новые виртуальные карты, настраивать их и привязывать к пользователям. Для выпуска карты необходимо наличие номера телефона у пользователя API. На текущий момент установка и изменение номера телефона доступны через персонального менеджера по договору. Выпуск виртуальных карт осуществляется с использованием методов: Запрос на выпуск виртуальной карты или Запрос на выпуск виртуальной карты (v.2). Для обслуживания по виртуальным картам используется мобильный профиль карты (МПК) – security величины для генерации QR-кодов. МПК хранится на мобильном устройстве держателя карты. Администратор может удалить МПК по карте методом deleteMPC. При выпуске МПК требуется подтвердить операцию СМС – кодом. В сутки доступно 5 попыток активации МПК, администратор API может сбросить счетчик методом resetMPC.»

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
POST: http://localhost/vip/v2/cards
BODY:
{
" user_id ": "1-2Q468ZB"
}
```

## Что важно знать

- `template_id` можно не передавать, если шаблон виртуальной карты уже закреплён за пользователем через `client.users.attach_contracts()`.
