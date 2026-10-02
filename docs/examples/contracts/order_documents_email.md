---
description: "Отправка документов на email: пример client.contracts.order_documents_email() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/contracts.yaml. Не редактируйте вручную. -->

# Отправка документов на email

`client.contracts.order_documents_email()` · [справочник метода](../../methods/contracts.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/contracts/order_documents_email.py)

Отправить выбранные документы в PDF или XLSX на один или несколько адресов.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/documents` | Да | Да | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Отправка документов на email: client.contracts.order_documents_email().

Отправить выбранные документы в PDF или XLSX на один или несколько адресов.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/order_documents_email.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/order_documents_email/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
DOCUMENT_ID = "6fffd550-b55f-11e9-8123-005056a969a3"


async def example(client: APIClient) -> None:
    response = await client.contracts.order_documents_email(
        ids=[DOCUMENT_ID], fmt="pdf", emails=["accounting@example.org"]
    )
    print("Документы отправлены" if response.data else "Сервер не подтвердил отправку")


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
| `ids` | <code>list[str]</code> | Да | — | Список ID документов. В API параметр называется `id`. |
| `fmt` | <code>Literal[pdf, xlsx]</code> | Да | — | Формат документа: `pdf` или `xlsx`. В API параметр называется `format`. |
| `emails` | <code>list[str]</code> | Да | — | Список email-адресов для отправки документов, не более пяти. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/documents HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "id": [
    "6fffd550-b55f-11e9-8123-005056a969a3"
  ],
  "format": "pdf",
  "emails": [
    "accounting@example.org"
  ]
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `id` | тело JSON | `["6fffd550-b55f-11e9-8123-005056a969a3"]` | array | Да | ID документов |
| `format` | тело JSON | `"pdf"` | string | Да | Формат документа (pdf/xlsx) |
| `emails` | тело JSON | `["accounting@example.org"]` | array | Да | Список email – адресов, на которые будут отправлены документы (до 5) |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`DocumentsOrderResponse`](../../data-types/contracts/DocumentsOrderResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": true,
  "timestamp": 1591148656
}
```

Вывод примера на этом ответе:

```text
Документы отправлены
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`DocumentsOrderResponse`](../../data-types/contracts/DocumentsOrderResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>bool</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Документа с таким ID нет в договоре.

**Что делать:** Возьмите `id` из `get_documents()` для того же договора.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Документ не найден"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении order_documents_email Сообщение сервера: Документ не найден. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.contracts.order_documents_email(ids=[DOCUMENT_ID], fmt="pdf", emails=["не-email"])
```

SDK проверяет адреса email до отправки запроса. Исключение `RequestValidationError`:

```text
email: ожидается корректный адрес электронной почты
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- ID документов берутся из `get_documents()`. Параметр `fmt` в запросе называется `format`, `ids` — `id`.
