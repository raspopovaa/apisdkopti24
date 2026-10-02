---
description: "Получение, установка и удаление ограничений по регионам обслуживания."
---

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
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `card_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор топливной карты. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RegionLimitResponse`

**Pydantic-модель:** [`RegionLimitResponse`](../data-types/region_limits/RegionLimitResponse.md)

Ответ передаётся в `RegionLimitResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>RegionLimitList</code> | <code>object (RegionLimitList)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`RegionLimitList`](../data-types/region_limits/RegionLimitList.md)

### Пример

```python
result = await client.region_limits.get_region_limits(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_region_limits](../examples/region_limits/get_region_limits.md).

## `client.region_limits.remove_region_limit()`

Удалить региональный лимит карты или группы карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `removeRegionLimit` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `regionlimit_id` | <code>str</code> | Да | — | ID регионального лимита. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RemoveRegionLimit`

**Pydantic-модель:** [`RemoveRegionLimit`](../data-types/region_limits/RemoveRegionLimit.md)

Ответ передаётся в `RemoveRegionLimit.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>bool</code> | <code>boolean</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.region_limits.remove_region_limit(
    regionlimit_id="regionlimit-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [remove_region_limit](../examples/region_limits/remove_region_limit.md).

## `client.region_limits.set_region_limit()`

Создать или изменить региональные лимиты одного договора.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setRegionLimit` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `region_limits` | <code>list[RegionLimitRequestItem]</code> | Да | — | Массив параметров регионального лимита: ID лимита, карты, группы и договора, страна, регион, АЗС, партнёр и `limit_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RegionLimitSetResponse`

**Pydantic-модель:** [`RegionLimitSetResponse`](../data-types/region_limits/RegionLimitSetResponse.md)

Ответ передаётся в `RegionLimitSetResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | ID сохранённых региональных лимитов |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.region_limits.set_region_limit(
    region_limits="region-limits",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [set_region_limit](../examples/region_limits/set_region_limit.md).
