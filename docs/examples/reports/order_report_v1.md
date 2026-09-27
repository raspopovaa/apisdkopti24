---
description: "Заказ транзакционного отчёта (API v1): пример client.reports.order_report_v1() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/reports.yaml. Не редактируйте вручную. -->

# Заказ транзакционного отчёта (API v1)

`client.reports.order_report_v1()` · [справочник метода](../../methods/reports.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/reports/order_report_v1.py)

Заказать транзакционный отчёт за период по договору, списку карт или группам карт через первую версию API.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/reports` | Да | Да | Нет | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Заказ транзакционного отчёта (API v1): client.reports.order_report_v1().

Заказать транзакционный отчёт за период по договору, списку карт или группам карт через
первую версию API.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/reports/order_report_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/reports/order_report_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CONTRACT_ID = "1-2Q4CN99"


async def example(client: APIClient) -> None:
    response = await client.reports.order_report_v1(
        contract_id=CONTRACT_ID,
        start="2026-09-01",
        end="2026-09-30",
        report_format="xlsx",
        email="accounting@example.org",
    )
    print(f"Задачи отчёта: {', '.join(response.data or [])}")


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
| `contract_id` | `str` | Да | — | ID договора |
| `start` | `str` | Да | — | Дата начала отчётного периода. |
| `end` | `str` | Да | — | Дата окончания отчётного периода. |
| `report_format` | `str` | Да | — | Формат отчёта: `xlsx`, `xml`, `pdf` или `csv`. |
| `email` | `str | None` | Нет | `None` | Email-адреса для отправки отчёта. |
| `cards_list` | `list[str] | None` | Нет | `None` | Список 16-значных номеров карт для формирования отчёта. Если список не передан, отчёт формируется по указанной группе карт либо по всем картам договора. |
| `group_id` | `list[str] | None` | Нет | `None` | Список ID группы карт. Если данный параметр пустой или не передан – будет сформирован отчет либо по списку карт, если указан cards_list, либо по всем картам для указанного договора |
| `archive` | `bool` | Нет | `False` | — |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/reports?contract_id=1-2Q4CN99&start=2026-09-01&end=2026-09-30&report_format=xlsx&email=accounting@example.org HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID договора |
| `start` | строка запроса | `2026-09-01` | string | Да | Дата начала отчетного периода |
| `end` | строка запроса | `2026-09-30` | string | Да | Дата окончания отчетного периода |
| `report_format` | строка запроса | `xlsx` | string | Да | Формат отчета, необходимо передавать "xlsx" "xml" "pdf" "csv" |
| `email` | строка запроса | `accounting@example.org` | string | Да | Адреса для отправки на email |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`ReportV1OrderResponse`](../../data-types/reports/ReportV1OrderResponse.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    "1-2DJ1PK1"
  ],
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Задачи отчёта: 1-2DJ1PK1
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`ReportV1OrderResponse`](../../data-types/reports/ReportV1OrderResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `list[str]` | Да | [string], обязательное | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Период отчёта задан неверно.

**Что делать:** Передайте даты в формате `YYYY-MM-DD`, начало не позже конца.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректный период"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении order_report_v1 Сообщение сервера: Некорректный период. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.reports.order_report_v1(contract_id=CONTRACT_ID, start="2026-09-30", end="2026-09-01", report_format="xlsx")
```

Дата окончания не может быть раньше даты начала. Исключение `RequestValidationError`:

```text
date_end не может предшествовать date_start
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Запрос транзакционного отчета за период на email и по ссылке». Запрос в спецификации: `GET http://localhost/vip/v1/reports`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- Реальный API отличается от спецификации: параметр `email` — в спецификации обязательный, фактически запрос без `email` принят, задача отчёта создана. SDK: необязательный параметр. Проверено запросом к реальному API.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
Заказ отчета по договору на почту
GET: http://localhost/vip/v1/reports?contract_id=1-13WR9S2&start=2017-01-01&end=2017-01-31&email=mail%40mail.ru&report_format=xlsx
Заказ отчета по списку карт на почту
GET: http://localhost/vip/v1/reports?contract_id=1-13WR9S2&cards_list=["7005830003470036","7005830003470028","7005830003470010"]&start=2017-01-01&end=2017-01-31&email=mail%40mail.ru&report_format=pdf
Заказ отчета по списку групп карт на почту
GET: http://localhost/vip/v1/reports?contract_id=1-13WR9S2&group_id=[“1-2656PK1”,”1-2656PK2”,”1-2656PK3”]&start=2017-01-01&end=2017-01-31&email=mail%40mail.ru&report_format=xml
Заказ файла отчета по договору
GET: http://localhost/vip/v1/reports?contract_id=1-13WR9S2&start=2017-01-01&end=2017-01-31&report_format=xlsx
Заказ файла отчета по списку карт
GET: http://localhost/vip/v1/reports?contract_id=1-13WR9S2&cards_list=["7005830003470036","7005830003470028","7005830003470010"]&start=2017-01-01&end=2017-01-31&report_format=pdf
Заказ файла отчета по списку групп карт
GET: http://localhost/vip/v1/reports?contract_id=1-13WR9S2&group_id=[“1-2656PK1”,”1-2656PK2”,”1-2656PK3”]&start=2017-01-01&end=2017-01-31&report_format=xml
```

## Что важно знать

- Метод отправляется запросом GET, но создаёт задачу отчёта, поэтому пример спрашивает подтверждение.
- `cards_list` и `group_id` SDK передаёт строками JSON-массива.
