---
description: "Создание и переименование группы карт: пример client.card_groups.set_card_group() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/card_groups.yaml. Не редактируйте вручную. -->

# Создание и переименование группы карт

`client.card_groups.set_card_group()` · [справочник метода](../../methods/card_groups.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/card_groups/set_card_group.py)

Создать группу карт с заданным именем. Если передать `group_id`, тот же метод переименует существующую группу.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/setCardGroup` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Создание и переименование группы карт: client.card_groups.set_card_group().

Создать группу карт с заданным именем. Если передать `group_id`, тот же метод
переименует существующую группу.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/card_groups/set_card_group.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/card_groups/set_card_group/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.card_groups.set_card_group(name="Самосвалы")
    print(f"ID группы: {response.data.id}")


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
| `name` | <code>str</code> | Да | — | Имя группы карт. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | ID группы карт |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`ContractForm`](../../data-types/request_parts/ContractForm.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str</code> | Да | — | ID договора |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/setCardGroup HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-2Q4CN99&name=Самосвалы
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | форма | `1-2Q4CN99` | string | Да | ID договора |
| `name` | форма | `Самосвалы` | string | Да | Имя группы карт |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`SetCardGroupResponse`](../../data-types/card_group/SetCardGroupResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "id": "1-2645PK1"
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
ID группы: 1-2645PK1
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`SetCardGroupResponse`](../../data-types/card_group/SetCardGroupResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>SetCardGroupData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`SetCardGroupData`](../../data-types/card_group/SetCardGroupData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.id` | <code>str</code> | Да | Идентификатор созданной или изменённой группы |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Имя пустое или длиннее 50 символов.

**Что делать:** Сократите имя группы до 50 символов.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Количество символов в поле Имя должно быть между 1 и 50"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении set_card_group Сообщение сервера: Количество символов в поле Имя должно быть между 1 и 50. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.card_groups.set_card_group(name="  ")
```

Пустое имя группы отклоняется до отправки запроса. Исключение `RequestValidationError`:

```text
name: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Имя группы не обязано быть уникальным: сервер не отклоняет повтор и создаёт новую группу с тем же именем и новым `id`. SDK не проверяет уникальность и не повторяет метод автоматически — при сетевой ошибке сначала проверьте список групп через `get_card_groups()`, иначе можно случайно создать вторую группу с тем же именем.
- Имя — от 1 до 50 символов. Двоеточие в имени сервер не отклоняет с понятной ошибкой: запрос завершается `500 internalError`. Если имя формируется автоматически (например, включает время), избегайте `:` и других специальных символов.
- Параметр `name`: от 1 до 50 символов; двоеточие в имени приводит к `500`. В SDK — передаёт значение как есть.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
