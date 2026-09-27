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
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

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
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": [
    {
      "date": "2018-03-01 12:57:06",
      "client_id": "1-1FLRGZ1",
      "user_id": "1-25PPQUX",
      "contract_id": "1-1N7MWYG",
      "job_id": "1-2EVN64V",
      "report_name": "Транзакционный отчет за период",
      "report_format": "pdf"
    },
    {
      "date": "2018-02-27 12:04:38",
      "client_id": "1-1FLRGZ1",
      "user_id": "1-25PPQUX",
      "contract_id": "1-1N7MWYG",
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
1-2EVN64V  2018-03-01 12:57:06  Транзакционный отчет за период  pdf
1-2EQH7OL  2018-02-27 12:04:38  Транзакционный отчет за период  pdf
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`ReportV1JobListResponse`](../../data-types/reports/ReportV1JobListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `list[ReportV1JobItem] | None` | Нет | json, необязательное | Массив заданий отчётов |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`ReportV1JobItem`](../../data-types/reports/ReportV1JobItem.md) · `data[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `date` | `data[].date` | `str` | Да | string, обязательное | Дата создания отчета |
| `client_id` | `data[].client_id` | `str` | Да | string, обязательное | ID клиента |
| `user_id` | `data[].user_id` | `str` | Да | string, обязательное | ID пользователя |
| `contract_id` | `data[].contract_id` | `str` | Да | string, обязательное | ID договора |
| `job_id` | `data[].job_id` | `str` | Да | string, обязательное | Идентификатор задания (Job ID) |
| `report_name` | `data[].report_name` | `str` | Да | string, обязательное | Название отчета |
| `report_format` | `data[].report_format` | `str` | Да | string, обязательное | Формат отчета (pdf, xlsx, xml и т.д.) |

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_report_job_list_v1 Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Список ранее заказанных отчетов по ссылке». Запрос в спецификации: `GET http://localhost/vip/v1/getReportJobList`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- Описание в спецификации: «После заказа можно запросить все отчеты заказанные по ссылке в последние 7 дней и повторно их скачать.»

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET: http://localhost/vip/v1/getReportJobList
```
