---
description: "Заказ отчетов, просмотр заданий и скачивание сформированных файлов."
---

# `client.reports`

Заказ отчетов, просмотр заданий и скачивание сформированных файлов.

## `client.reports.download_report_file()`

Скачать файл сформированного отчета.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `reports/jobs/{job_id}` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `job_id` | `str` | Да | — | Идентификатор задания формирования отчета. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `bytes`

**Pydantic-модель:** нет.

SDK возвращает значение указанного Python-типа; отдельная модель ответа не применяется.

Возвращает бинарное содержимое файла отчета.

### Пример

```python
result = await client.reports.download_report_file(
    job_id="job-id",
)
print(result)
```

## `client.reports.download_report_file_v1()`

Скачать сформированный отчёт v1 в память.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getReportFile` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `job_id` | `str` | Да | — | Идентификатор задания формирования отчета. |
| `archive` | `bool` | Нет | `False` | Архивировать отчёт в ZIP. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `bytes`

**Pydantic-модель:** нет.

SDK возвращает значение указанного Python-типа; отдельная модель ответа не применяется.

### Пример

```python
result = await client.reports.download_report_file_v1(
    job_id="job-id",
    archive=False,
)
print(result)
```

## `client.reports.get_report_job_list_v1()`

Получить список задач формирования отчётов v1.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getReportJobList` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportV1JobListResponse`

**Pydantic-модель:** [`ReportV1JobListResponse`](../data-types/reports/ReportV1JobListResponse.md)

Ответ передаётся в `ReportV1JobListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `list[ReportV1JobItem] \| None` | `array[object (ReportV1JobItem)] \| null` | Нет | Да | Массив заданий отчётов |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ReportV1JobItem`](../data-types/reports/ReportV1JobItem.md)

### Пример

```python
result = await client.reports.get_report_job_list_v1(
)
print(result)
```

## `client.reports.get_report_jobs()`

Получить список задач формирования отчётов v2.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `reports/jobs` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportJobListResponse`

**Pydantic-модель:** [`ReportJobListResponse`](../data-types/reports/ReportJobListResponse.md)

Ответ передаётся в `ReportJobListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `ReportJobList` | `object (ReportJobList)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ReportJobList`](../data-types/reports/ReportJobList.md)

### Пример

```python
result = await client.reports.get_report_jobs(
)
print(result)
```

## `client.reports.get_reports()`

Получить список доступных отчётов v2.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `reports` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportListResponse`

**Pydantic-модель:** [`ReportListResponse`](../data-types/reports/ReportListResponse.md)

Ответ передаётся в `ReportListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `ReportList` | `object (ReportList)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ReportList`](../data-types/reports/ReportList.md)

### Пример

```python
result = await client.reports.get_reports(
)
print(result)
```

## `client.reports.order_report()`

Создать задание на формирование отчета.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `reports` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `report_id` | `str` | Да | — | Идентификатор отчета. |
| `format` | `str` | Да | — | Формат отчёта; допустимые форматы приведены в поле `formats` метода получения списка доступных отчётов. |
| `params` | `dict[str, Any]` | Да | — | Параметры отчёта; набор параметров приведён в поле `parameters` метода получения списка доступных отчётов. |
| `emails` | `str | None` | Нет | `None` | Список email-адресов получателей отчёта. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportOrderResponse`

**Pydantic-модель:** [`ReportOrderResponse`](../data-types/reports/ReportOrderResponse.md)

Ответ передаётся в `ReportOrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `ReportOrderData` | `object (ReportOrderData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ReportOrderData`](../data-types/reports/ReportOrderData.md)

### Пример

```python
result = await client.reports.order_report(
    report_id="report-id",
    format="format",
    params={},
)
print(result)
```

## `client.reports.order_report_v1()`

Заказать транзакционный отчёт v1.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `reports` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str` | Да | — | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `start` | `str` | Да | — | Дата начала отчётного периода. |
| `end` | `str` | Да | — | Дата окончания отчётного периода. |
| `report_format` | `str` | Да | — | Формат отчёта: `xlsx`, `xml`, `pdf` или `csv`. |
| `email` | `str | None` | Нет | `None` | Email-адреса для отправки отчёта. |
| `cards_list` | `list[str] | None` | Нет | `None` | Список 16-значных номеров карт для формирования отчёта. Если список не передан, отчёт формируется по указанной группе карт либо по всем картам договора. |
| `group_id` | `list[str] | None` | Нет | `None` | Идентификатор группы топливных карт. |
| `archive` | `bool` | Нет | `False` | Параметр публичного метода SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportV1OrderResponse`

**Pydantic-модель:** [`ReportV1OrderResponse`](../data-types/reports/ReportV1OrderResponse.md)

Ответ передаётся в `ReportV1OrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `list[str]` | `array[string]` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.reports.order_report_v1(
    contract_id="contract-id",
    start="start",
    end="end",
    report_format="report-format",
    archive=False,
)
print(result)
```
