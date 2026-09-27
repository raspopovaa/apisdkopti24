---
description: "Скачивание файла отчёта: пример client.reports.download_report_file() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/reports.yaml. Не редактируйте вручную. -->

# Скачивание файла отчёта

`client.reports.download_report_file()` · [справочник метода](../../methods/reports.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/reports/download_report_file.py)

Скачать готовый файл отчёта по `job_id`. Имя, формат и сохранение файла — на стороне приложения.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/reports/jobs/{job_id}` | Нет | Да | Нет | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Скачивание файла отчёта: client.reports.download_report_file().

Скачать готовый файл отчёта по `job_id`. Имя, формат и сохранение файла — на стороне
приложения.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/reports/download_report_file.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/reports/download_report_file/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
JOB_ID = "1-425XN6L"


async def example(client: APIClient) -> None:
    content = await client.reports.download_report_file(job_id=JOB_ID)
    print(f"Получено {len(content)} байт")


async def main() -> None:
    answer = input("Вызов тарифицируется на реальном API. Продолжить? [yes/no] ")
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
| `job_id` | `str` | Да | — | Job_ID отчета |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/reports/jobs/1-425XN6L HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `job_id` | путь | `1-425XN6L` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

Метод возвращает файл: SDK отдаёт его содержимое как `bytes`, без проверки моделью. Если API вместо файла ответил ошибкой в JSON, SDK выбросит исключение, как для обычных методов.

В примере сервер отвечает файлом с `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.

Вывод примера на этом ответе:

```text
Получено 44 байт
```

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 404 · `NotFoundError`

**Почему:** Задачи с таким `job_id` нет или отчёт ещё не сформирован.

**Что делать:** Проверьте `job_id` в `get_report_jobs()` и дождитесь, когда `available_after` станет `0`.

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
NotFoundError: [404] Объект или маршрут не найден при выполнении download_report_file Сообщение сервера: Не найден отчет. Подсказка: Проверьте идентификаторы и маршрут: запрашиваемый ресурс не найден.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.reports.download_report_file(job_id="")
```

Пустой `job_id` отклоняется до отправки запроса. Исключение `RequestValidationError`:

```text
job_id: значение не может быть пустым
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Метод загружает файл в память. Для больших отчётов используйте `download_report_file_to(job_id=..., destination="report.xlsx")`: он записывает файл на диск частями.
- Размер файла в памяти ограничен настройкой `max_in_memory_response_bytes` (по умолчанию 64 МиБ).
