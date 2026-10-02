---
description: "Удаление группы карт: пример client.card_groups.remove_card_group() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/card_groups.yaml. Не редактируйте вручную. -->

# Удаление группы карт

`client.card_groups.remove_card_group()` · [справочник метода](../../methods/card_groups.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/card_groups/remove_card_group.py)

Удалить группу карт. Сами карты остаются в договоре.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/removeCardGroup` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Удаление группы карт: client.card_groups.remove_card_group().

Удалить группу карт. Сами карты остаются в договоре.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/card_groups/remove_card_group.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/card_groups/remove_card_group/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
GROUP_ID = "1-2645PK1"


async def example(client: APIClient) -> None:
    response = await client.card_groups.remove_card_group(group_id=GROUP_ID)
    print("Группа удалена" if response.data else "Сервер не подтвердил удаление")


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
| `group_id` | <code>str</code> | Да | — | ID группы карт |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |
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
POST /vip/v1/removeCardGroup HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-2Q4CN99&group_id=1-2645PK1
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | форма | `1-2Q4CN99` | string | Да | ID договора |
| `group_id` | форма | `1-2645PK1` | string | Да | ID группы карт |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`RemoveCardGroupResponse`](../../data-types/card_group/RemoveCardGroupResponse.md).
Пример ответа.

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
Группа удалена
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`RemoveCardGroupResponse`](../../data-types/card_group/RemoveCardGroupResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>bool</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Группа уже удалена или принадлежит другому договору.

**Что делать:** Обновите список групп через `get_card_groups()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Группа карт не найдена"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении remove_card_group Сообщение сервера: Группа карт не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.card_groups.remove_card_group(group_id="")
```

Пустой `group_id` отклоняется до отправки запроса. Исключение `RequestValidationError`:

```text
group_id: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Метод заметно медленнее других изменяющих вызовов: ответ обычно приходит через 9–11 секунд, а бывает, что его нет и через 90 секунд, хотя группа уже удалена. SDK ждёт ответа до 120 секунд (класс таймаута `read_heavy`), после этого поднимает `APIResponseTimeoutError` и метод не повторяет. Такая ошибка не значит, что группа осталась: проверьте `get_card_groups()`. При необходимости увеличьте `TimeoutPolicy.read_heavy`.
- Если клиент не дождался ответа и повторяет запрос, повторный вызов на уже удалённую группу может прийти как `403 accessDenied` («Нет доступа»), а не `404 notFound`. Перед повтором обновите список групп через `get_card_groups()` и убедитесь, что группа ещё существует.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
