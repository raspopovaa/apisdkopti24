---
description: "Получение, установка и удаление продуктовых лимитов топливной карты."
---

# `client.limits`

Получение, установка и удаление продуктовых лимитов топливной карты.

## `client.limits.get_limits()`

Получить продуктовые лимиты договора, карты или группы карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `limit` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `card_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор топливной карты. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `LimitsResponse`

**Pydantic-модель:** [`LimitsResponse`](../data-types/limits/LimitsResponse.md)

Ответ передаётся в `LimitsResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>LimitsData</code> | <code>object (LimitsData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`LimitsData`](../data-types/limits/LimitsData.md)

### Пример

```python
result = await client.limits.get_limits(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_limits](../examples/limits/get_limits.md).

## `client.limits.remove_limit()`

Удалить продуктовый лимит карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `removeLimit` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `limit_id` | <code>str</code> | Да | — | Параметр публичного метода SDK. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RemoveLimitResponse`

**Pydantic-модель:** [`RemoveLimitResponse`](../data-types/limits/RemoveLimitResponse.md)

Ответ передаётся в `RemoveLimitResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.limits.remove_limit(
    limit_id="limit-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [remove_limit](../examples/limits/remove_limit.md).

## `client.limits.set_limit()`

Установить или изменить продуктовый лимит карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setLimit` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `limits` | <code>list[LimitRequestItem &#124; Mapping[str, Any]]</code> | Да | — | Параметр публичного метода SDK. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `SetLimitResponse`

**Pydantic-модель:** [`SetLimitResponse`](../data-types/limits/SetLimitResponse.md)

Ответ передаётся в `SetLimitResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.limits.set_limit(
    limits="limits",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [set_limit](../examples/limits/set_limit.md).
