---
description: "Управление временными, количественными и иными ограничителями топливных карт."
---

# `client.restrictions`

Управление временными, количественными и иными ограничителями топливных карт.

## `client.restrictions.get_restrictions()`

Получить товарные ограничители договора, карты или группы карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `restriction` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `card_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор топливной карты. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RestrictionGetResponse`

**Pydantic-модель:** [`RestrictionGetResponse`](../data-types/restrictions/RestrictionGetResponse.md)

Ответ передаётся в `RestrictionGetResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>RestrictionList</code> | <code>object (RestrictionList)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`RestrictionList`](../data-types/restrictions/RestrictionList.md)

### Пример

```python
result = await client.restrictions.get_restrictions(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_restrictions](../examples/restrictions/get_restrictions.md).

## `client.restrictions.remove_restriction()`

Удалить товарный ограничитель карты или группы карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `removeRestriction` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `restriction_id` | <code>str</code> | Да | — | ID товарного ограничителя. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RestrictionRemoveResponse`

**Pydantic-модель:** [`RestrictionRemoveResponse`](../data-types/restrictions/RestrictionRemoveResponse.md)

Ответ передаётся в `RestrictionRemoveResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.restrictions.remove_restriction(
    restriction_id="restriction-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [remove_restriction](../examples/restrictions/remove_restriction.md).

## `client.restrictions.set_restriction()`

Создать или изменить товарные ограничители одного договора.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setRestriction` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `restrictions` | <code>list[RestrictionRequestItem]</code> | Да | — | Массив параметров товарного ограничителя: ID ограничителя, карты, группы и договора, группа и тип продукта, а также `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RestrictionSetResponse`

**Pydantic-модель:** [`RestrictionSetResponse`](../data-types/restrictions/RestrictionSetResponse.md)

Ответ передаётся в `RestrictionSetResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.restrictions.set_restriction(
    restrictions="restrictions",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [set_restriction](../examples/restrictions/set_restriction.md).
