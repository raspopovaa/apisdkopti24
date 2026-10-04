---
description: "Добавление и удаление карт в группе: пример client.card_groups.set_cards_to_group() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/card_groups.yaml. Не редактируйте вручную. -->

# Добавление и удаление карт в группе

`client.card_groups.set_cards_to_group()` · [справочник метода](../../methods/card_groups.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/card_groups/set_cards_to_group.py)

Добавить карты в группу или убрать их из неё одним запросом. Для каждой карты указывается действие `Attach` или `Detach`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v1/setCardsToGroup` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Добавление и удаление карт в группе: client.card_groups.set_cards_to_group().

Добавить карты в группу или убрать их из неё одним запросом. Для каждой карты
указывается действие `Attach` или `Detach`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/card_groups/set_cards_to_group.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/card_groups/set_cards_to_group/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider
from apisdkopti24.models.card_group import CardGroupAssignmentRequest

# Условные значения: замените своими.
GROUP_ID = "1-T000017"
ATTACH_CARD_ID = "9000016"
DETACH_CARD_ID = "9000017"


async def example(client: APIClient) -> None:
    cards = [
        CardGroupAssignmentRequest(id=ATTACH_CARD_ID, type="Attach"),
        CardGroupAssignmentRequest(id=DETACH_CARD_ID, type="Detach"),
    ]
    response = await client.card_groups.set_cards_to_group(group_id=GROUP_ID, cards_list=cards)
    print("Состав группы изменён" if response.data else "Сервер не подтвердил изменение")


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
| `cards_list` | <code>list[CardGroupAssignmentRequest &#124; Mapping[str, object]]</code> | Да | — | Список карт договора, добавляемых в группу или удаляемых из неё. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`CardGroupAssignmentRequest`](../../data-types/card_group/CardGroupAssignmentRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str</code> | Да | — | ID карты |
| `type` | <code>Literal[Attach, Detach]</code> | Да | допустимые значения: 'Attach', 'Detach' | Действие с картой |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v1/setCardsToGroup HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

contract_id=1-T000025&group_id=1-T000017&cards_list=[{"id":"9000016","type":"Attach"},{"id":"9000017","type":"Detach"}]
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | форма | `1-T000025` | string | Да | ID договора |
| `group_id` | форма | `1-T000017` | string | Да | ID группы карт |
| `cards_list` | форма | `[{"id":"9000016","type":"Attach"},{"id":"9000017","type":"Detach"}]` | string | Да | Cписок ID карт по данному договору, добавляемых или удаляемых из группы карт |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`SetCardsToGroupResponse`](../../data-types/card_group/SetCardsToGroupResponse.md).
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
Состав группы изменён
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`SetCardsToGroupResponse`](../../data-types/card_group/SetCardsToGroupResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>bool</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Группа удалена или принадлежит другому договору.

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
NotFoundError: [404] Объект или маршрут не найден при выполнении set_cards_to_group Сообщение сервера: Группа карт не найдена. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.card_groups.set_cards_to_group(group_id=GROUP_ID, cards_list=[{"id": "9000016", "type": "Move"}])
```

Допустимы только действия `Attach` и `Detach`. Исключение `pydantic.ValidationError`:

```text
1 validation error for CardGroupAssignmentRequest
type
  Input should be 'Attach' or 'Detach' [type=literal_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Вместо моделей можно передать словари `{"id": ..., "type": ...}`: SDK проверит их той же моделью.
- Список SDK отправляет одним полем формы со строкой JSON-массива: `cards_list=[{"id":...,"type":"Attach"}]`.
- Изменение состава применяется не сразу: `data: true` означает, что запрос принят, но карта может не появиться (или не исчезнуть) в `get_card_groups()` и `get_cards_v1(group_id=...)` ещё до нескольких десятков секунд. Не считайте привязку неудавшейся по первому же чтению сразу после вызова.
- `contract_id` можно не передавать: SDK подставит договор, выбранный при авторизации.
