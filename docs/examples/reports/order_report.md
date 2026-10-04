---
description: "Заказ отчёта: пример client.reports.order_report() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/reports.yaml. Не редактируйте вручную. -->

# Заказ отчёта

`client.reports.order_report()` · [справочник метода](../../methods/reports.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/reports/order_report.py)

Заказать формирование отчёта. Отчёт формируется асинхронно: метод возвращает `job_id`, по которому потом скачивается файл.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/reports` | Да | Да | Да | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные и тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Заказ отчёта: client.reports.order_report().

Заказать формирование отчёта. Отчёт формируется асинхронно: метод возвращает `job_id`,
по которому потом скачивается файл.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/reports/order_report.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/reports/order_report/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CONTRACT_ID = "1-T000025"


async def example(client: APIClient) -> None:
    response = await client.reports.order_report(
        report_id="tsc_report_transaction_reriod",
        format="xlsx",
        params={
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "id_agreement": [CONTRACT_ID],
        },
    )
    print(f"Задачи отчёта: {', '.join(response.data.job_id or [])}")


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
| `report_id` | <code>str</code> | Да | — | Идентификатор отчета. |
| `format` | <code>str</code> | Да | — | Формат отчёта; допустимые форматы приведены в поле `formats` метода получения списка доступных отчётов. |
| `params` | <code>dict[str, Any]</code> | Да | — | Параметры отчёта; набор параметров приведён в поле `parameters` метода получения списка доступных отчётов. |
| `emails` | <code>list[str] &#124; None</code> | Нет | `None` | Список email-адресов получателей отчёта. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`ReportOrderRequest`](../../data-types/reports/ReportOrderRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `id` | <code>str</code> | Да | — | Идентификатор отчета |
| `format` | <code>str</code> | Да | — | Формат отчета (pdf, xlsx и т.д.) |
| `emails` | <code>list[str] &#124; None</code> | Нет | — | Email-адреса для отправки отчета |
| `params` | <code>ReportOrderParams</code> | Да | — | Параметры отчета |

#### [`ReportOrderParams`](../../data-types/reports/ReportOrderParams.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `start_date` | <code>str &#124; None</code> | Нет | — | Дата начала периода |
| `end_date` | <code>str &#124; None</code> | Нет | — | Дата окончания периода |
| `id_agreement` | <code>list[str] &#124; None</code> | Нет | — | Список ID договоров |
| `id_card` | <code>list[str] &#124; None</code> | Нет | — | Список карт |
| `card_group_code` | <code>list[str] &#124; None</code> | Нет | — | Список групп карт |
| `id_client` | <code>list[str] &#124; None</code> | Нет | — | Список клиентов |
| `additional` | <code>dict[str, object] &#124; None</code> | Нет | — | Дополнительные параметры |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/reports HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
Content-Type: application/json

{
  "id": "tsc_report_transaction_reriod",
  "format": "xlsx",
  "params": {
    "start_date": "2026-09-01",
    "end_date": "2026-09-30",
    "id_agreement": [
      "1-T000025"
    ]
  }
}
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `id` | тело JSON | `"tsc_report_transaction_reriod"` | string | Да | ID отчета (ID отчетов находятся в поле id метода Список доступных отчетов) |
| `format` | тело JSON | `"xlsx"` | string | Да | Формат отчета (доступные форматы находятся в поле formats метода Список доступных отчетов) |
| `params` | тело JSON | `{"start_date": "2026-09-01", "end_date": "2026-09-30", "id_agreement": ["1-T000025"]}` | object | Да | Параметры отчета (параметры находятся в поле parameters метода Список доступных отчетов) |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`ReportOrderResponse`](../../data-types/reports/ReportOrderResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "job_id": [
      "1-T000054"
    ]
  },
  "timestamp": 1670883905
}
```

Вывод примера на этом ответе:

```text
Задачи отчёта: 1-T000054
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`ReportOrderResponse`](../../data-types/reports/ReportOrderResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>ReportOrderData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`ReportOrderData`](../../data-types/reports/ReportOrderData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `job_id` | `data.job_id` | <code>list[str] &#124; None</code> | Нет | Идентификаторы созданных заданий на генерацию отчета |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Отчёта с таким ID нет или он недоступен договору.

**Что делать:** Возьмите `id` отчёта из `get_reports()`.

Ответ API:

```json
{
  "status": {
    "code": 404,
    "errors": [
      {
        "type": "notFound",
        "message": "Не найден отчет"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
NotFoundError: [404] Объект или маршрут не найден при выполнении order_report Сообщение сервера: Не найден отчет. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.reports.order_report(report_id="", format="xlsx", params={})
```

Пустой ID отчёта отклоняется до отправки запроса. Исключение `RequestValidationError`:

```text
report_id: значение не может быть пустым
```

```python
await client.reports.order_report(report_id="tsc_report_transaction_reriod", format="xlsx", params={"start_date": "2026-09-01", "end_date": "2026-10-15"})
```

Период длиннее 1 календарного месяца сервер молча сократил бы. Исключение `RequestValidationError`:

```text
Период start_date–end_date длиннее 1 календарного месяца
```

```python
await client.reports.order_report(report_id="tsc_report_transaction_reriod", format="xlsx", params={}, emails="accounting@example.org")
```

`emails` — список адресов, а не строка. Исключение `RequestValidationError`:

```text
emails: ожидается непустой список адресов
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- ID отчёта, форматы и имена параметров берутся из `get_reports()`.
- Списочные параметры — `id_agreement`, `id_card`, `card_group_code`, `id_client` — передаются массивами строк, даже если значение одно.
- Если передать `emails` — список адресов, — готовый отчёт придёт и на почту. Отправка на почту ограничена 15 МБ.
- Период `start_date`–`end_date` — не длиннее 1 календарного месяца: конец не позже той же даты следующего месяца (например, с 2026-09-01 по 2026-10-01). Более длинный период сервер не отклоняет, а молча сокращает, поэтому SDK отклоняет его до запроса (`RequestValidationError`), так же как неверный формат дат и конец раньше начала. Отчёт за месяц формируется около 5 минут.
- Тарификация зависит от способа доставки. Таблица тарификации в `get_info().data.methods_info` относит заказ с отправкой на email (`reports_post`) к платным действиям, а заказ только по ссылке, без `emails` (`reports_post_file`), — к бесплатным. SDK помечает метод платным по худшему случаю.
- Ответ `{"job_id": []}` означает, что задача не создана: новой записи в `get_report_jobs()` не появится. Так отвечает DEMO-стенд, и так же API отвечает на заказ транзакционного отчёта без `id_agreement`. С `id_agreement` задача появляется в списке сразу. После любого заказа проверяйте, что задача появилась в списке.
