---
description: "Заказанные отчёты (API v1): пример client.reports.get_report_job_list_v1() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/reports.yaml. Не редактируйте вручную. -->

# Заказанные отчёты (API v1)

`client.reports.get_report_job_list_v1()` · [справочник метода](../../methods/reports.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/reports/get_report_job_list_v1.py)

Получить отчёты, заказанные за последние 7 дней, через первую версию API.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/getReportJobList` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Заказанные отчёты (API v1): client.reports.get_report_job_list_v1().

Получить отчёты, заказанные за последние 7 дней, через первую версию API.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/reports/get_report_job_list_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/reports/get_report_job_list_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.reports.get_report_job_list_v1()
    for job in response.data:
        print(f"{job.job_id}  {job.date}  {job.report_name}  {job.report_format}")


async def main() -> None:
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
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/getReportJobList HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`ReportV1JobListResponse`](../../data-types/reports/ReportV1JobListResponse.md).
Пример ответа.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    {
      "date": "2018-03-01 12:57:06",
      "client_id": "1-T000003",
      "user_id": "1-T000013",
      "contract_id": "1-T000008",
      "job_id": "1-T000020",
      "report_name": "Транзакционный отчет за период",
      "report_format": "pdf"
    },
    {
      "date": "2018-02-27 12:04:38",
      "client_id": "1-T000003",
      "user_id": "1-T000013",
      "contract_id": "1-T000008",
      "job_id": "1-2EQH7OL",
      "report_name": "Транзакционный отчет за период",
      "report_format": "pdf"
    }
  ],
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
1-T000020  2018-03-01 12:57:06  Транзакционный отчет за период  pdf
1-2EQH7OL  2018-02-27 12:04:38  Транзакционный отчет за период  pdf
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`ReportV1JobListResponse`](../../data-types/reports/ReportV1JobListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>list[ReportV1JobItem] &#124; None</code> | Нет | Массив заданий отчётов |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`ReportV1JobItem`](../../data-types/reports/ReportV1JobItem.md) · `data[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `date` | `data[].date` | <code>str</code> | Да | Дата создания отчета |
| `client_id` | `data[].client_id` | <code>str</code> | Да | ID клиента |
| `user_id` | `data[].user_id` | <code>str</code> | Да | ID пользователя |
| `contract_id` | `data[].contract_id` | <code>str</code> | Да | ID договора |
| `job_id` | `data[].job_id` | <code>str</code> | Да | Идентификатор задания (Job ID) |
| `report_name` | `data[].report_name` | <code>str</code> | Да | Название отчета |
| `report_format` | `data[].report_format` | <code>str</code> | Да | Формат отчета (pdf, xlsx, xml и т.д.) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Роль пользователя не позволяет работать с отчётами.

**Что делать:** Проверьте роль пользователя API.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Доступ запрещён"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_report_job_list_v1 Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Задача появляется в списке сразу после `order_report_v1()`. `available_after` — обратный отсчёт в секундах до ожидаемой готовности: отчёт за месяц бывает готов примерно через 5 минут. `0` не гарантирует, что файл сформирован: скачивание может отвечать `404` «Формирование отчета не завершено» и спустя полчаса. Повторяйте скачивание с паузой в несколько минут, а не сразу. Список задач общий с `get_report_jobs()`.
