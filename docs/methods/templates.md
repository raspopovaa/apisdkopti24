---
description: "Управление шаблонами, лимитами, ограничителями и географическими ограничениями."
---

# `client.templates`

Управление шаблонами, лимитами, ограничителями и географическими ограничениями.

## `client.templates.create_template()`

Создать шаблон виртуальной карты для выбранного договора.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `type_` | <code>Literal[Limit, Wallet]</code> | Да | — | Тип карты: `Limit` — лимитная схема, `Wallet` — электронный кошелёк. |
| `name` | <code>str</code> | Да | — | Имя шаблона ВК, уникальное в рамках договора. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateCreateResponse`

**Pydantic-модель:** [`TemplateCreateResponse`](../data-types/templates/TemplateCreateResponse.md)

Ответ передаётся в `TemplateCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.create_template(
    type_="type-",
    name="name",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [create_template](../examples/templates/create_template.md).

## `client.templates.create_template_georestriction()`

Создать геоограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/georestrictions` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `payload` | <code>TemplateGeoRestrictionCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Параметры геоограничителя: `contract_id`, `country`, `region`, `partner`, `service_center`, `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionCreateResponse`](../data-types/templates/TemplateGeoRestrictionCreateResponse.md)

Ответ передаётся в `TemplateGeoRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.create_template_georestriction(
    template_id="template-id",
    payload="payload",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [create_template_georestriction](../examples/templates/create_template_georestriction.md).

## `client.templates.create_template_limit()`

Создать лимит шаблона виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/limits` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `payload` | <code>TemplateLimitCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Параметры лимита шаблона ВК: `contract_id`, ограничение `amount` или `sum`, параметры `time`/`term`, `product_type`, `product_group`, а также `create_restriction`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitCreateResponse`

**Pydantic-модель:** [`TemplateLimitCreateResponse`](../data-types/templates/TemplateLimitCreateResponse.md)

Ответ передаётся в `TemplateLimitCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.create_template_limit(
    template_id="template-id",
    payload="payload",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [create_template_limit](../examples/templates/create_template_limit.md).

## `client.templates.create_template_restriction()`

Создать ограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/restrictions` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `payload` | <code>TemplateRestrictionCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Параметры ограничителя: `contract_id`, `product_type`, `product_group`, `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateRestrictionCreateResponse`](../data-types/templates/TemplateRestrictionCreateResponse.md)

Ответ передаётся в `TemplateRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.create_template_restriction(
    template_id="template-id",
    payload="payload",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [create_template_restriction](../examples/templates/create_template_restriction.md).

## `client.templates.delete_template()`

Удалить шаблон виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateDeleteResponse`

**Pydantic-модель:** [`TemplateDeleteResponse`](../data-types/templates/TemplateDeleteResponse.md)

Ответ передаётся в `TemplateDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template(
    template_id="template-id",
    use_post=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [delete_template](../examples/templates/delete_template.md).

## `client.templates.delete_template_georestriction()`

Удалить геоограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `georestriction_id` | <code>str</code> | Да | — | ID геоограничителя шаблона ВК. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionDeleteResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionDeleteResponse`](../data-types/templates/TemplateGeoRestrictionDeleteResponse.md)

Ответ передаётся в `TemplateGeoRestrictionDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template_georestriction(
    template_id="template-id",
    georestriction_id="georestriction-id",
    use_post=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [delete_template_georestriction](../examples/templates/delete_template_georestriction.md).

## `client.templates.delete_template_limit()`

Удалить лимит шаблона виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}/limits/{limit_id}` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `limit_id` | <code>str</code> | Да | — | ID лимита шаблона ВК. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitDeleteResponse`

**Pydantic-модель:** [`TemplateLimitDeleteResponse`](../data-types/templates/TemplateLimitDeleteResponse.md)

Ответ передаётся в `TemplateLimitDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template_limit(
    template_id="template-id",
    limit_id="limit-id",
    use_post=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [delete_template_limit](../examples/templates/delete_template_limit.md).

## `client.templates.delete_template_restriction()`

Удалить ограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `restriction_id` | <code>str</code> | Да | — | ID ограничителя шаблона ВК. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionDeleteResponse`

**Pydantic-модель:** [`TemplateRestrictionDeleteResponse`](../data-types/templates/TemplateRestrictionDeleteResponse.md)

Ответ передаётся в `TemplateRestrictionDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template_restriction(
    template_id="template-id",
    restriction_id="restriction-id",
    use_post=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [delete_template_restriction](../examples/templates/delete_template_restriction.md).

## `client.templates.get_template_georestrictions()`

Получить список геоограничителей шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates/{template_id}/georestrictions` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionListResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionListResponse`](../data-types/templates/TemplateGeoRestrictionListResponse.md)

Ответ передаётся в `TemplateGeoRestrictionListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TemplateGeoRestrictionListData</code> | <code>object (TemplateGeoRestrictionListData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TemplateGeoRestrictionListData`](../data-types/templates/TemplateGeoRestrictionListData.md)

### Пример

```python
result = await client.templates.get_template_georestrictions(
    template_id="template-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_template_georestrictions](../examples/templates/get_template_georestrictions.md).

## `client.templates.get_template_limits()`

Получить список лимитов шаблона виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates/{template_id}/limits` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitListResponse`

**Pydantic-модель:** [`TemplateLimitListResponse`](../data-types/templates/TemplateLimitListResponse.md)

Ответ передаётся в `TemplateLimitListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TemplateLimitListData</code> | <code>object (TemplateLimitListData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TemplateLimitListData`](../data-types/templates/TemplateLimitListData.md)

### Пример

```python
result = await client.templates.get_template_limits(
    template_id="template-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_template_limits](../examples/templates/get_template_limits.md).

## `client.templates.get_template_restrictions()`

Получить список ограничителей шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates/{template_id}/restrictions` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionListResponse`

**Pydantic-модель:** [`TemplateRestrictionListResponse`](../data-types/templates/TemplateRestrictionListResponse.md)

Ответ передаётся в `TemplateRestrictionListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TemplateRestrictionListData</code> | <code>object (TemplateRestrictionListData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TemplateRestrictionListData`](../data-types/templates/TemplateRestrictionListData.md)

### Пример

```python
result = await client.templates.get_template_restrictions(
    template_id="template-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_template_restrictions](../examples/templates/get_template_restrictions.md).

## `client.templates.get_templates()`

Получить список шаблонов виртуальных карт выбранного договора.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplatesListResponse`

**Pydantic-модель:** [`TemplatesListResponse`](../data-types/templates/TemplatesListResponse.md)

Ответ передаётся в `TemplatesListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TemplatesListData</code> | <code>object (TemplatesListData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TemplatesListData`](../data-types/templates/TemplatesListData.md)

### Пример

```python
result = await client.templates.get_templates(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_templates](../examples/templates/get_templates.md).

## `client.templates.update_template()`

Изменить существующий шаблон виртуальной карты через PUT или POST override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `type_` | <code>Literal[Limit, Wallet]</code> | Да | — | Тип карты: `Limit` — лимитная схема, `Wallet` — электронный кошелёк. |
| `name` | <code>str</code> | Да | — | Имя шаблона ВК, уникальное в рамках договора. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `True` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateCreateResponse`

**Pydantic-модель:** [`TemplateCreateResponse`](../data-types/templates/TemplateCreateResponse.md)

Ответ передаётся в `TemplateCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.update_template(
    template_id="template-id",
    type_="type-",
    name="name",
    use_post=True,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [update_template](../examples/templates/update_template.md).

## `client.templates.update_template_georestriction()`

Изменить геоограничитель шаблона через PUT или POST override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `georestriction_id` | <code>str</code> | Да | — | ID геоограничителя шаблона ВК. |
| `payload` | <code>TemplateGeoRestrictionCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Изменяемые параметры геоограничителя: `country`, `region`, `partner`, `service_center`, `restriction_type`; `contract_id` изменить нельзя. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `True` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionCreateResponse`](../data-types/templates/TemplateGeoRestrictionCreateResponse.md)

Ответ передаётся в `TemplateGeoRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.update_template_georestriction(
    template_id="template-id",
    georestriction_id="georestriction-id",
    payload="payload",
    use_post=True,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [update_template_georestriction](../examples/templates/update_template_georestriction.md).

## `client.templates.update_template_limit()`

Изменить лимит шаблона через PUT или POST method override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/limits/{limit_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `limit_id` | <code>str</code> | Да | — | ID лимита шаблона ВК. |
| `limit` | <code>TemplateLimitCreateRequest &#124; Mapping[str, Any] &#124; None</code> | Нет | `None` | Параметр публичного метода SDK. |
| `limits` | <code>list[TemplateLimitCreateRequest &#124; Mapping[str, Any]] &#124; None</code> | Нет | `None` | Параметры изменения лимита: ограничение `amount` или `sum`, `time`/`term`, `product_type`, `product_group`; `contract_id` изменить нельзя. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `use_post` | <code>bool</code> | Нет | `True` | Параметр публичного метода SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitCreateResponse`

**Pydantic-модель:** [`TemplateLimitCreateResponse`](../data-types/templates/TemplateLimitCreateResponse.md)

Ответ передаётся в `TemplateLimitCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.update_template_limit(
    template_id="template-id",
    limit_id="limit-id",
    use_post=True,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [update_template_limit](../examples/templates/update_template_limit.md).

## `client.templates.update_template_restriction()`

Изменить ограничитель шаблона через PUT или POST override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | <code>str</code> | Да | — | Идентификатор шаблона. |
| `restriction_id` | <code>str</code> | Да | — | ID ограничителя шаблона ВК. |
| `payload` | <code>TemplateRestrictionCreateRequest &#124; Mapping[str, Any]</code> | Да | — | Изменяемые параметры ограничителя: `product_type`, `product_group`, `restriction_type`; `contract_id` изменить нельзя. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | <code>bool</code> | Нет | `True` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateRestrictionCreateResponse`](../data-types/templates/TemplateRestrictionCreateResponse.md)

Ответ передаётся в `TemplateRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>str</code> | <code>string</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.update_template_restriction(
    template_id="template-id",
    restriction_id="restriction-id",
    payload="payload",
    use_post=True,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [update_template_restriction](../examples/templates/update_template_restriction.md).
