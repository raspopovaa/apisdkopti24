# `client.region_limits`

Получение, установка и удаление ограничений по регионам обслуживания.

## `client.region_limits.get_region_limits()`

Получить региональные лимиты договора, карты или группы карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `regionLimit` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `card_id` | `str | None` | Нет | `None` | Идентификатор топливной карты. |
| `group_id` | `str | None` | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RegionLimitResponse`

**Pydantic-модель:** [`RegionLimitResponse`](../data-types/region_limits/RegionLimitResponse.md)

Ответ передаётся в `RegionLimitResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `RegionLimitList` | `object (RegionLimitList)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`RegionLimitList`](../data-types/region_limits/RegionLimitList.md)

### Пример

```python
result = await client.region_limits.get_region_limits(
)
print(result)
```

## `client.region_limits.remove_region_limit()`

Удалить региональный лимит карты или группы карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `removeRegionLimit` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `regionlimit_id` | `str` | Да | — | ID регионального лимита. |
| `group_id` | `str | None` | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RemoveRegionLimit`

**Pydantic-модель:** [`RemoveRegionLimit`](../data-types/region_limits/RemoveRegionLimit.md)

Ответ передаётся в `RemoveRegionLimit.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `bool` | `boolean` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.region_limits.remove_region_limit(
    regionlimit_id="regionlimit-id",
)
print(result)
```

## `client.region_limits.set_region_limit()`

Создать или изменить региональные лимиты одного договора.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setRegionLimit` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `region_limits` | `list[RegionLimitRequestItem]` | Да | — | Массив параметров регионального лимита: ID лимита, карты, группы и договора, страна, регион, АЗС, партнёр и `limit_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RegionLimitSetResponse`

**Pydantic-модель:** [`RegionLimitSetResponse`](../data-types/region_limits/RegionLimitSetResponse.md)

Ответ передаётся в `RegionLimitSetResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.region_limits.set_region_limit(
    region_limits="region-limits",
)
print(result)
```
