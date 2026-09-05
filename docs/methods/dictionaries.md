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
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `AzsFiltersResponse`

**Pydantic-модель:** [`AzsFiltersResponse`](../data-types/dictionaries/AzsFiltersResponse.md)

Ответ передаётся в `AzsFiltersResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `list[AzsFilterItem] \| None` | `array[object (AzsFilterItem)] \| null` | Да | Да | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`AzsFilterItem`](../data-types/dictionaries/AzsFilterItem.md)

### Пример

```python
result = await client.dictionaries.get_azs_filters(
)
print(result)
```

## `client.dictionaries.get_azs_list_v1()`

Получение списка торговых точек (АЗС, версия 1)

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `AZS` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `page` | `int` | Нет | `1` | Номер страницы результата. |
| `onpage` | `int` | Нет | `10` | Количество элементов на странице. |
| `filter` | `dict[str, Any] | None` | Нет | `None` | JSON-объект для фильтрации списка торговых точек. |
| `id` | `str | None` | Нет | `None` | ID торговой точки для получения одной детальной записи. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `AzsListV1Response`

**Pydantic-модель:** [`AzsListV1Response`](../data-types/dictionaries/AzsListV1Response.md)

Ответ передаётся в `AzsListV1Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `AzsListV1Data \| None` | `object (AzsListV1Data) \| null` | Да | Да | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.dictionaries.get_azs_list_v2()`

Получение списка торговых точек (АЗС, версия 2)

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `azs` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `filter` | `dict[str, Any] | None` | Нет | `None` | JSON-объект для фильтрации списка торговых точек. |
| `q` | `str | None` | Нет | `None` | Строка полнотекстового поиска. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `AzsListV2Response`

**Pydantic-модель:** [`AzsListV2Response`](../data-types/dictionaries/AzsListV2Response.md)

Ответ передаётся в `AzsListV2Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `AzsListV2Data \| None` | `object (AzsListV2Data) \| null` | Да | Да | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`AzsListV2Data`](../data-types/dictionaries/AzsListV2Data.md)

### Пример

```python
result = await client.dictionaries.get_azs_list_v2(
)
print(result)
```

## `client.dictionaries.get_dictionary()`

Получить общий справочник по имени.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getDictionary` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `name` | `str` | Да | — | Наименование справочника: `CardStatus`, `ContractStatus`, `Country`, `Currency`, `Goods`, `PaymentScheme`, `PaymentTerm`, `ProductGroup`, `ProductType`, `POIType`, `Region`, `Services`, `Unit`, `Office`, `POIPartner` или `DiscountScheme`. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `DictionaryResponse`

**Pydantic-модель:** [`DictionaryResponse`](../data-types/dictionaries/DictionaryResponse.md)

Ответ передаётся в `DictionaryResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `DictionaryData \| None` | `object (DictionaryData) \| null` | Да | Да | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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
