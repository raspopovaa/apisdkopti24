---
description: "Управление пользователями договора и привязками пользователей к картам."
---

# `client.users`

Управление пользователями договора и привязками пользователей к картам.

## `client.users.attach_card()`

Привязать карту к пользователю.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `users/{user_id}/attachCard` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `user_id` | `str` | Да | — | Идентификатор пользователя. |
| `card_id` | `str` | Да | — | Идентификатор топливной карты. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `UserBoolResponse`

**Pydantic-модель:** [`UserBoolResponse`](../data-types/users/UserBoolResponse.md)

Ответ передаётся в `UserBoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.users.attach_card(
    user_id="user-id",
    card_id="card-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [attach_card](../examples/users/attach_card.md).

## `client.users.attach_contracts()`

Привязать договоры и права доступа к пользователю.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `users/{user_id}/attachContracts` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `user_id` | `str` | Да | — | Идентификатор пользователя. |
| `contracts` | `list[UserAttachContractRequest | Mapping[str, object]]` | Да | — | Список договоров для прикрепления к пользователю. Для каждого договора указываются `sid` — ID договора, `template_id` — ID шаблона ВК, `use_mpc` — разрешение выпуска МПК (`true`/`false`). |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `UserBoolResponse`

**Pydantic-модель:** [`UserBoolResponse`](../data-types/users/UserBoolResponse.md)

Ответ передаётся в `UserBoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.users.attach_contracts(
    user_id="user-id",
    contracts="contracts",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [attach_contracts](../examples/users/attach_contracts.md).

## `client.users.create_user()`

Создать пользователя по внешнему UUID и мобильному номеру.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `users` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `uuid` | `str` | Да | — | Внутренний ID водителя в системе клиента. |
| `mobile` | `str` | Да | — | Телефон водителя, используемый как логин. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `UserCreateResponse`

**Pydantic-модель:** [`UserCreateResponse`](../data-types/users/UserCreateResponse.md)

Ответ передаётся в `UserCreateResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.users.create_user(
    uuid="uuid",
    mobile="mobile",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [create_user](../examples/users/create_user.md).

## `client.users.delete_user()`

Удалить пользователя через DELETE или POST method override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `users/{user_id}` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `user_id` | `str` | Да | — | Идентификатор пользователя. |
| `use_post` | `bool` | Нет | `False` | Параметр публичного метода SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `UserBoolResponse`

**Pydantic-модель:** [`UserBoolResponse`](../data-types/users/UserBoolResponse.md)

Ответ передаётся в `UserBoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.users.delete_user(
    user_id="user-id",
    use_post=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [delete_user](../examples/users/delete_user.md).

## `client.users.detach_card()`

Отвязать карту от пользователя.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `users/{user_id}/detachCard` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `user_id` | `str` | Да | — | Идентификатор пользователя. |
| `card_id` | `str` | Да | — | Идентификатор топливной карты. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `UserBoolResponse`

**Pydantic-модель:** [`UserBoolResponse`](../data-types/users/UserBoolResponse.md)

Ответ передаётся в `UserBoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.users.detach_card(
    user_id="user-id",
    card_id="card-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [detach_card](../examples/users/detach_card.md).

## `client.users.detach_contracts()`

Отвязать договоры от пользователя.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `users/{user_id}/detachContracts` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `user_id` | `str` | Да | — | Идентификатор пользователя. |
| `contracts` | `list[str]` | Да | — | Список ID договоров, которые нужно открепить от пользователя. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `UserBoolResponse`

**Pydantic-модель:** [`UserBoolResponse`](../data-types/users/UserBoolResponse.md)

Ответ передаётся в `UserBoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.users.detach_contracts(
    user_id="user-id",
    contracts=["item-id"],
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [detach_contracts](../examples/users/detach_contracts.md).

## `client.users.get_users()`

Получить страницу пользователей корпоративного клиента.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `users` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `sort` | `str | None` | Нет | `None` | Выражение сортировки. Префикс «-» задает сортировку по убыванию. |
| `page` | `int | None` | Нет | `None` | Номер страницы результата. |
| `on_page` | `int | None` | Нет | `None` | Количество элементов на странице. |
| `q` | `str | None` | Нет | `None` | Строка полнотекстового поиска. |
| `filter` | `UserFilter | Mapping[str, object] | None` | Нет | `None` | Объект фильтрации пользователей, например `{"role": "Driver", "active": true}`. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `UserListResponse`

**Pydantic-модель:** [`UserListResponse`](../data-types/users/UserListResponse.md)

Ответ передаётся в `UserListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `UserList \| None` | `object (UserList) \| null` | Да | Да | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`UserList`](../data-types/users/UserList.md)

### Пример

```python
result = await client.users.get_users(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_users](../examples/users/get_users.md).
