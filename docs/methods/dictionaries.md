---
description: "Справочные значения, список АЗС и фильтры торговых точек."
---

# `client.dictionaries`

Справочные значения, список АЗС и фильтры торговых точек.

## `client.dictionaries.get_azs_filters()`

Получить список доступных фильтров для поиска торговых точек (АЗС)

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `azs/filters` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `AzsFiltersResponse`

**Pydantic-модель:** [`AzsFiltersResponse`](../data-types/dictionaries/AzsFiltersResponse.md)

Ответ передаётся в `AzsFiltersResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>list[AzsFilterItem] &#124; None</code> | <code>array[object (AzsFilterItem)] &#124; null</code> | Да | Да | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`AzsFilterItem`](../data-types/dictionaries/AzsFilterItem.md)

### Пример

```python
result = await client.dictionaries.get_azs_filters(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_azs_filters](../examples/dictionaries/get_azs_filters.md).

## `client.dictionaries.get_azs_list_v1()`

Получить список торговых точек через API v1.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `AZS` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `page` | <code>int</code> | Нет | `1` | Номер страницы результата. |
| `onpage` | <code>int</code> | Нет | `10` | Количество точек на странице. 0 возвращает все точки одним ответом, который может превысить max_json_response_bytes (ResponseTooLargeError). |
| `filter` | <code>AzsV1Filter &#124; Mapping[str, object] &#124; None</code> | Нет | `None` | JSON-объект для фильтрации списка торговых точек. |
| `id` | <code>str &#124; None</code> | Нет | `None` | ID торговой точки для получения одной детальной записи. |
| `q` | <code>str &#124; None</code> | Нет | `None` | Строка полнотекстового поиска. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `AzsListV1Response`

**Pydantic-модель:** [`AzsListV1Response`](../data-types/dictionaries/AzsListV1Response.md)

Ответ передаётся в `AzsListV1Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>AzsListV1Data &#124; None</code> | <code>object (AzsListV1Data) &#124; null</code> | Да | Да | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`AzsListV1Data`](../data-types/dictionaries/AzsListV1Data.md)

### Пример

```python
result = await client.dictionaries.get_azs_list_v1(
    page=1,
    onpage=10,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_azs_list_v1](../examples/dictionaries/get_azs_list_v1.md).

## `client.dictionaries.get_azs_list_v2()`

Найти торговые точки по фильтрам и строке поиска через API v2.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `azs` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `filter` | <code>AzsV2Filter &#124; Mapping[str, object] &#124; None</code> | Нет | `None` | JSON-объект для фильтрации списка торговых точек. |
| `q` | <code>str &#124; None</code> | Нет | `None` | Строка полнотекстового поиска. |
| `id` | <code>str &#124; None</code> | Нет | `None` | ID торговой точки. |
| `page` | <code>int &#124; None</code> | Нет | `None` | Номер страницы, начиная с 1. Задаётся вместе с on_page: сервер делит ответ на страницы только при обоих, поэтому один из них SDK отклоняет (RequestValidationError). Без обоих API возвращает всю сеть АЗС одним ответом. |
| `on_page` | <code>int &#124; None</code> | Нет | `None` | Количество точек на странице. Задаётся вместе с page. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `AzsListV2Response`

**Pydantic-модель:** [`AzsListV2Response`](../data-types/dictionaries/AzsListV2Response.md)

Ответ передаётся в `AzsListV2Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>AzsListV2Data &#124; None</code> | <code>object (AzsListV2Data) &#124; null</code> | Да | Да | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`AzsListV2Data`](../data-types/dictionaries/AzsListV2Data.md)

### Пример

```python
result = await client.dictionaries.get_azs_list_v2(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_azs_list_v2](../examples/dictionaries/get_azs_list_v2.md).

## `client.dictionaries.get_dictionary()`

Получить общий справочник по имени.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getDictionary` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `name` | <code>str</code> | Да | — | Наименование справочника: `CardStatus`, `ContractStatus`, `Country`, `Currency`, `Goods`, `PaymentScheme`, `PaymentTerm`, `ProductGroup`, `ProductType`, `POIType`, `Region`, `Services`, `Unit`, `Office`, `POIPartner` или `DiscountScheme`. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `DictionaryResponse`

**Pydantic-модель:** [`DictionaryResponse`](../data-types/dictionaries/DictionaryResponse.md)

Ответ передаётся в `DictionaryResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>DictionaryData &#124; None</code> | <code>object (DictionaryData) &#124; null</code> | Да | Да | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`DictionaryData`](../data-types/dictionaries/DictionaryData.md)

### Пример

```python
result = await client.dictionaries.get_dictionary(
    name="name",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_dictionary](../examples/dictionaries/get_dictionary.md).
