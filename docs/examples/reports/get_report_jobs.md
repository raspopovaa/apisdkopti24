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
    for job in response.data.result:
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
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

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
Пример ответа взят из спецификации API 1.1.60; списки сокращены до 2 элементов.

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
        "client_id": "1-37PCTRD",
        "user_id": "1-37R882C",
        "contract_id": "1-380B94P",
        "contract_name": "01014043578",
        "job_id": "1-425XN6L",
        "report_name": "Транзакционный отчет за период",
        "report_format": "xlsx",
        "available_after": 123
      },
      {
        "date": "2022-12-13 01:19:15",
        "client_id": "1-37PCTRD",
        "user_id": "1-37R882C",
        "contract_id": "1-380B94P",
        "contract_name": "01014043578",
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
1-425XN6L  Транзакционный отчет за период  xlsx  готов через 123 с
1-425XN39  Транзакционный отчет за период  xlsx  готов через 0 с
1-421ZA1J  Транзакционный отчет за период  xlsx  готов через 0 с
1-421Z9ZV  Транзакционный отчет за период  xlsx  готов через 0 с
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`ReportJobListResponse`](../../data-types/reports/ReportJobListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `ReportJobList` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`ReportJobList`](../../data-types/reports/ReportJobList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `total_count` | `data.total_count` | `int` | Да | uint, обязательное | Количество найденных отчетов |
| `result` | `data.result` | `list[ReportJobItem] | None` | Нет | json, необязательное | Список заказанных отчетов |

#### [`ReportJobItem`](../../data-types/reports/ReportJobItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `date` | `data.result[].date` | `str` | Да | string, обязательное | Дата создания заказа отчета |
| `client_id` | `data.result[].client_id` | `str` | Да | string, обязательное | ID клиента |
| `user_id` | `data.result[].user_id` | `str` | Да | string, обязательное | ID пользователя |
| `contract_id` | `data.result[].contract_id` | `str` | Да | string, обязательное | ID договора |
| `contract_name` | `data.result[].contract_name` | `str | None` | Нет | — | Название договора |
| `job_id` | `data.result[].job_id` | `str` | Да | string, обязательное | Идентификатор задания (Job ID) |
| `report_name` | `data.result[].report_name` | `str` | Да | string, обязательное | Название отчета |
| `report_format` | `data.result[].report_format` | `str` | Да | string, обязательное | Формат отчета (pdf, xlsx и т.д.) |
| `available_after` | `data.result[].available_after` | `int` | Да | uint, обязательное | Количество секунд до доступности отчета |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

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

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Список ранее заказанных отчетов по ссылке (v.2)». Запрос в спецификации: `GET http://localhost/vip/v2/reports/jobs`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- Описание в спецификации: «После заказа можно запросить все отчеты заказанные по ссылке в последние 14 дней и повторно их скачать.»

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET: http://localhost/vip/v2/reports/jobs
```

## Что важно знать

- `available_after` — через сколько секунд отчёт будет готов; `0` — файл можно скачивать сейчас.
