---
description: "Заказанные отчёты: пример client.reports.get_report_jobs() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/reports.yaml. Не редактируйте вручную. -->

# Заказанные отчёты

`client.reports.get_report_jobs()` · [справочник метода](../../methods/reports.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/reports/get_report_jobs.py)

Получить отчёты, заказанные за последние 14 дней, с их `job_id` и тем, через сколько секунд файл можно будет скачать.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/reports/jobs` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Заказанные отчёты: client.reports.get_report_jobs().

Получить отчёты, заказанные за последние 14 дней, с их `job_id` и тем, через сколько
секунд файл можно будет скачать.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/reports/get_report_jobs.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/reports/get_report_jobs/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.reports.get_report_jobs()
    for job in response.data.result or []:
        print(
            f"{job.job_id}  {job.report_name}  {job.report_format}  готов через {job.available_after} с"
        )


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
GET /vip/v2/reports/jobs HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`ReportJobListResponse`](../../data-types/reports/ReportJobListResponse.md).
Пример ответа; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 4,
    "result": [
      {
        "date": "2022-12-13 01:25:05",
        "client_id": "1-T000030",
        "user_id": "1-T000033",
        "contract_id": "1-T000036",
        "contract_name": "90000000001",
        "job_id": "1-T000054",
        "report_name": "Транзакционный отчет за период",
        "report_format": "xlsx",
        "available_after": 123
      },
      {
        "date": "2022-12-13 01:19:15",
        "client_id": "1-T000030",
        "user_id": "1-T000033",
        "contract_id": "1-T000036",
        "contract_name": "90000000001",
        "job_id": "1-425XN39",
        "report_name": "Транзакционный отчет за период",
        "report_format": "xlsx",
        "available_after": 0
      }
    ]
  },
  "timestamp": 1670884198
}
```

Вывод примера на этом ответе:

```text
1-T000054  Транзакционный отчет за период  xlsx  готов через 123 с
1-425XN39  Транзакционный отчет за период  xlsx  готов через 0 с
1-421ZA1J  Транзакционный отчет за период  xlsx  готов через 0 с
1-421Z9ZV  Транзакционный отчет за период  xlsx  готов через 0 с
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`ReportJobListResponse`](../../data-types/reports/ReportJobListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>ReportJobList</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`ReportJobList`](../../data-types/reports/ReportJobList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество найденных отчетов |
| `result` | `data.result` | <code>list[ReportJobItem] &#124; None</code> | Нет | Список заказанных отчетов |

#### [`ReportJobItem`](../../data-types/reports/ReportJobItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `date` | `data.result[].date` | <code>str</code> | Да | Дата создания заказа отчета |
| `client_id` | `data.result[].client_id` | <code>str</code> | Да | ID клиента |
| `user_id` | `data.result[].user_id` | <code>str</code> | Да | ID пользователя |
| `contract_id` | `data.result[].contract_id` | <code>str</code> | Да | ID договора |
| `contract_name` | `data.result[].contract_name` | <code>str &#124; None</code> | Нет | Название договора |
| `job_id` | `data.result[].job_id` | <code>str</code> | Да | Идентификатор задания (Job ID) |
| `report_name` | `data.result[].report_name` | <code>str</code> | Да | Название отчета |
| `report_format` | `data.result[].report_format` | <code>str</code> | Да | Формат отчета (pdf, xlsx и т.д.) |
| `available_after` | `data.result[].available_after` | <code>int</code> | Да | Количество секунд до доступности отчета |

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_report_jobs Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- `available_after` — через сколько секунд отчёт ожидается готовым. Значение `0` не гарантирует, что файл сформирован: скачивание может ещё долго отвечать `404` «Формирование отчета не завершено». Список задач общий с `get_report_job_list_v1()`: там видны и задачи, заказанные через `order_report_v1()`.
