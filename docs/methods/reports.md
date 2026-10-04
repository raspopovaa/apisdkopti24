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
| `job_id` | <code>str</code> | Да | — | Идентификатор задания формирования отчета. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

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

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [download_report_file](../examples/reports/download_report_file.md).

## `client.reports.download_report_file_v1()`

Скачать сформированный отчёт v1 в память.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getReportFile` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `job_id` | <code>str</code> | Да | — | Идентификатор задания формирования отчета. |
| `archive` | <code>bool</code> | Нет | `False` | Архивировать отчёт в ZIP. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

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

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [download_report_file_v1](../examples/reports/download_report_file_v1.md).

## `client.reports.get_report_job_list_v1()`

Получить список задач формирования отчётов v1.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getReportJobList` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportV1JobListResponse`

**Pydantic-модель:** [`ReportV1JobListResponse`](../data-types/reports/ReportV1JobListResponse.md)

Ответ передаётся в `ReportV1JobListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>list[ReportV1JobItem] &#124; None</code> | <code>array[object (ReportV1JobItem)] &#124; null</code> | Нет | Да | Массив заданий отчётов |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ReportV1JobItem`](../data-types/reports/ReportV1JobItem.md)

### Пример

```python
result = await client.reports.get_report_job_list_v1(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_report_job_list_v1](../examples/reports/get_report_job_list_v1.md).

## `client.reports.get_report_jobs()`

Получить список задач формирования отчётов v2.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `reports/jobs` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportJobListResponse`

**Pydantic-модель:** [`ReportJobListResponse`](../data-types/reports/ReportJobListResponse.md)

Ответ передаётся в `ReportJobListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>ReportJobList</code> | <code>object (ReportJobList)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ReportJobList`](../data-types/reports/ReportJobList.md)

### Пример

```python
result = await client.reports.get_report_jobs(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_report_jobs](../examples/reports/get_report_jobs.md).

## `client.reports.get_reports()`

Получить список доступных отчётов v2.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `reports` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportListResponse`

**Pydantic-модель:** [`ReportListResponse`](../data-types/reports/ReportListResponse.md)

Ответ передаётся в `ReportListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>ReportList</code> | <code>object (ReportList)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ReportList`](../data-types/reports/ReportList.md)

### Пример

```python
result = await client.reports.get_reports(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_reports](../examples/reports/get_reports.md).

## `client.reports.order_report()`

Создать задание на формирование отчета.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `reports` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `report_id` | <code>str</code> | Да | — | Идентификатор отчета. |
| `format` | <code>str</code> | Да | — | Формат отчёта; допустимые форматы приведены в поле `formats` метода получения списка доступных отчётов. |
| `params` | <code>dict[str, Any]</code> | Да | — | Параметры отчёта; набор параметров приведён в поле `parameters` метода получения списка доступных отчётов. |
| `emails` | <code>list[str] &#124; None</code> | Нет | `None` | Список email-адресов получателей отчёта. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportOrderResponse`

**Pydantic-модель:** [`ReportOrderResponse`](../data-types/reports/ReportOrderResponse.md)

Ответ передаётся в `ReportOrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>ReportOrderData</code> | <code>object (ReportOrderData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

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

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [order_report](../examples/reports/order_report.md).

## `client.reports.order_report_v1()`

Заказать транзакционный отчёт v1.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `reports` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `start` | <code>str</code> | Да | — | Дата начала отчётного периода. |
| `end` | <code>str</code> | Да | — | Дата окончания отчётного периода. |
| `report_format` | <code>Literal[xlsx, xml, pdf, csv]</code> | Да | — | Формат отчёта: `xlsx`, `xml`, `pdf` или `csv`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `email` | <code>str &#124; None</code> | Нет | `None` | Email-адреса для отправки отчёта. |
| `cards_list` | <code>list[str] &#124; None</code> | Нет | `None` | Список 16-значных номеров карт для формирования отчёта. Если список не передан, отчёт формируется по указанной группе карт либо по всем картам договора. |
| `group_id` | <code>list[str] &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `archive` | <code>bool</code> | Нет | `False` | Параметр публичного метода SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ReportV1OrderResponse`

**Pydantic-модель:** [`ReportV1OrderResponse`](../data-types/reports/ReportV1OrderResponse.md)

Ответ передаётся в `ReportV1OrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>list[str]</code> | <code>array[string]</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.reports.order_report_v1(
    start="start",
    end="end",
    report_format="report-format",
    archive=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [order_report_v1](../examples/reports/order_report_v1.md).
