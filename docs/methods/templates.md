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
| `type_` | `Literal[Limit, Wallet]` | Да | — | Тип карты: `Limit` — лимитная схема, `Wallet` — электронный кошелёк. |
| `name` | `str` | Да | — | Имя шаблона ВК, уникальное в рамках договора. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateCreateResponse`

**Pydantic-модель:** [`TemplateCreateResponse`](../data-types/templates/TemplateCreateResponse.md)

Ответ передаётся в `TemplateCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.create_template_georestriction()`

Создать геоограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/georestrictions` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `payload` | `TemplateGeoRestrictionCreateRequest | Mapping[str, Any]` | Да | — | Параметры геоограничителя: `contract_id`, `country`, `region`, `partner`, `service_center`, `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionCreateResponse`](../data-types/templates/TemplateGeoRestrictionCreateResponse.md)

Ответ передаётся в `TemplateGeoRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.create_template_limit()`

Создать лимит шаблона виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/limits` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `payload` | `TemplateLimitCreateRequest | Mapping[str, Any]` | Да | — | Параметры лимита шаблона ВК: `contract_id`, ограничение `amount` или `sum`, параметры `time`/`term`, `product_type`, `product_group`, а также `create_restriction`. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitCreateResponse`

**Pydantic-модель:** [`TemplateLimitCreateResponse`](../data-types/templates/TemplateLimitCreateResponse.md)

Ответ передаётся в `TemplateLimitCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.create_template_restriction()`

Создать ограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/restrictions` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `payload` | `TemplateRestrictionCreateRequest | Mapping[str, Any]` | Да | — | Параметры ограничителя: `contract_id`, `product_type`, `product_group`, `restriction_type` (`1` — разрешающий, `2` — запрещающий). |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateRestrictionCreateResponse`](../data-types/templates/TemplateRestrictionCreateResponse.md)

Ответ передаётся в `TemplateRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.delete_template()`

Удалить шаблон виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | `bool` | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateDeleteResponse`

**Pydantic-модель:** [`TemplateDeleteResponse`](../data-types/templates/TemplateDeleteResponse.md)

Ответ передаётся в `TemplateDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template(
    template_id="template-id",
    use_post=False,
)
print(result)
```

## `client.templates.delete_template_georestriction()`

Удалить геоограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `georestriction_id` | `str` | Да | — | ID геоограничителя шаблона ВК. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | `bool` | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionDeleteResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionDeleteResponse`](../data-types/templates/TemplateGeoRestrictionDeleteResponse.md)

Ответ передаётся в `TemplateGeoRestrictionDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template_georestriction(
    template_id="template-id",
    georestriction_id="georestriction-id",
    use_post=False,
)
print(result)
```

## `client.templates.delete_template_limit()`

Удалить лимит шаблона виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}/limits/{limit_id}` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `limit_id` | `str` | Да | — | ID лимита шаблона ВК. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | `bool` | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitDeleteResponse`

**Pydantic-модель:** [`TemplateLimitDeleteResponse`](../data-types/templates/TemplateLimitDeleteResponse.md)

Ответ передаётся в `TemplateLimitDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template_limit(
    template_id="template-id",
    limit_id="limit-id",
    use_post=False,
)
print(result)
```

## `client.templates.delete_template_restriction()`

Удалить ограничитель шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `restriction_id` | `str` | Да | — | ID ограничителя шаблона ВК. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | `bool` | Нет | `False` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionDeleteResponse`

**Pydantic-модель:** [`TemplateRestrictionDeleteResponse`](../data-types/templates/TemplateRestrictionDeleteResponse.md)

Ответ передаётся в `TemplateRestrictionDeleteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.templates.delete_template_restriction(
    template_id="template-id",
    restriction_id="restriction-id",
    use_post=False,
)
print(result)
```

## `client.templates.get_template_georestrictions()`

Получить список геоограничителей шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates/{template_id}/georestrictions` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionListResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionListResponse`](../data-types/templates/TemplateGeoRestrictionListResponse.md)

Ответ передаётся в `TemplateGeoRestrictionListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `TemplateGeoRestrictionListData` | `object (TemplateGeoRestrictionListData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.get_template_limits()`

Получить список лимитов шаблона виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates/{template_id}/limits` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitListResponse`

**Pydantic-модель:** [`TemplateLimitListResponse`](../data-types/templates/TemplateLimitListResponse.md)

Ответ передаётся в `TemplateLimitListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `TemplateLimitListData` | `object (TemplateLimitListData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.get_template_restrictions()`

Получить список ограничителей шаблона.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates/{template_id}/restrictions` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionListResponse`

**Pydantic-модель:** [`TemplateRestrictionListResponse`](../data-types/templates/TemplateRestrictionListResponse.md)

Ответ передаётся в `TemplateRestrictionListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `TemplateRestrictionListData` | `object (TemplateRestrictionListData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.get_templates()`

Получить список шаблонов виртуальных карт выбранного договора.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `vc/templates` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplatesListResponse`

**Pydantic-модель:** [`TemplatesListResponse`](../data-types/templates/TemplatesListResponse.md)

Ответ передаётся в `TemplatesListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `TemplatesListData` | `object (TemplatesListData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TemplatesListData`](../data-types/templates/TemplatesListData.md)

### Пример

```python
result = await client.templates.get_templates(
)
print(result)
```

## `client.templates.update_template()`

Изменить существующий шаблон виртуальной карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `type_` | `Literal[Limit, Wallet]` | Да | — | Тип карты: `Limit` — лимитная схема, `Wallet` — электронный кошелёк. |
| `name` | `str` | Да | — | Имя шаблона ВК, уникальное в рамках договора. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateCreateResponse`

**Pydantic-модель:** [`TemplateCreateResponse`](../data-types/templates/TemplateCreateResponse.md)

Ответ передаётся в `TemplateCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.update_template(
    template_id="template-id",
    type_="type-",
    name="name",
)
print(result)
```

## `client.templates.update_template_georestriction()`

Изменить геоограничитель шаблона через PUT или POST override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `georestriction_id` | `str` | Да | — | ID геоограничителя шаблона ВК. |
| `payload` | `TemplateGeoRestrictionCreateRequest | Mapping[str, Any]` | Да | — | Изменяемые параметры геоограничителя: `country`, `region`, `partner`, `service_center`, `restriction_type`; `contract_id` изменить нельзя. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | `bool` | Нет | `True` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateGeoRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateGeoRestrictionCreateResponse`](../data-types/templates/TemplateGeoRestrictionCreateResponse.md)

Ответ передаётся в `TemplateGeoRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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

## `client.templates.update_template_limit()`

Изменить лимит шаблона через PUT или POST method override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/limits/{limit_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `limit_id` | `str` | Да | — | ID лимита шаблона ВК. |
| `limits` | `list[TemplateLimitCreateRequest | Mapping[str, Any]]` | Да | — | Параметры изменения лимита: ограничение `amount` или `sum`, `time`/`term`, `product_type`, `product_group`; `contract_id` изменить нельзя. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `use_post` | `bool` | Нет | `True` | Параметр публичного метода SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `TemplateLimitCreateResponse`

**Pydantic-модель:** [`TemplateLimitCreateResponse`](../data-types/templates/TemplateLimitCreateResponse.md)

Ответ передаётся в `TemplateLimitCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.templates.update_template_limit(
    template_id="template-id",
    limit_id="limit-id",
    limits="limits",
    use_post=True,
)
print(result)
```

## `client.templates.update_template_restriction()`

Изменить ограничитель шаблона через PUT или POST override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `template_id` | `str` | Да | — | Идентификатор шаблона. |
| `restriction_id` | `str` | Да | — | ID ограничителя шаблона ВК. |
| `payload` | `TemplateRestrictionCreateRequest | Mapping[str, Any]` | Да | — | Изменяемые параметры ограничителя: `product_type`, `product_group`, `restriction_type`; `contract_id` изменить нельзя. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `use_post` | `bool` | Нет | `True` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `TemplateRestrictionCreateResponse`

**Pydantic-модель:** [`TemplateRestrictionCreateResponse`](../data-types/templates/TemplateRestrictionCreateResponse.md)

Ответ передаётся в `TemplateRestrictionCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `str` | `string` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

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
