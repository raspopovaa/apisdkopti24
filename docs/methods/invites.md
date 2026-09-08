---
description: "Создание, просмотр, повторная отправка, продление и удаление приглашений."
---

# `client.invites`

Создание, просмотр, повторная отправка, продление и удаление приглашений.

## `client.invites.create_invite()`

Создать приглашение с отправкой или без отправки сообщения.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `invites` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `data` | `InviteCreateRequest | Mapping[str, object]` | Да | — | Данные приглашения: роль, телефон или email, список карт и список договоров с возможным `template_id`. |
| `with_send` | `bool` | Нет | `True` | Параметр публичного метода SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InviteResponse`

**Pydantic-модель:** [`InviteResponse`](../data-types/invites/InviteResponse.md)

Ответ передаётся в `InviteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `InviteActionResult` | `object (InviteActionResult)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`InviteActionResult`](../data-types/invites/InviteActionResult.md)

### Пример

```python
result = await client.invites.create_invite(
    data="data",
    with_send=True,
)
print(result)
```

## `client.invites.delete_invite()`

Удалить приглашение через DELETE или POST method override.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| DELETE | v2 | `invites/{invite_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `invite_id` | `str` | Да | — | Идентификатор приглашения. |
| `use_post` | `bool` | Нет | `False` | Параметр публичного метода SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InviteBoolResponse`

**Pydantic-модель:** [`InviteBoolResponse`](../data-types/invites/InviteBoolResponse.md)

Ответ передаётся в `InviteBoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.invites.delete_invite(
    invite_id="invite-id",
    use_post=False,
)
print(result)
```

## `client.invites.get_invites()`

Получить страницу приглашений пользователей.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `invites` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `role` | `str | None` | Нет | `None` | Фильтр по ID роли: `Supervisor`, `Regulatory`, `Driver` или `Readonly`. |
| `user_id` | `str | None` | Нет | `None` | Идентификатор пользователя. |
| `sort` | `str | None` | Нет | `None` | Выражение сортировки. Префикс «-» задает сортировку по убыванию. |
| `status` | `str | None` | Нет | `None` | Фильтр по статусу приглашения: `Active`, `Expired` или `Finished`. |
| `q` | `str | None` | Нет | `None` | Строка полнотекстового поиска. |
| `page` | `int | None` | Нет | `None` | Номер страницы результата. |
| `on_page` | `int | None` | Нет | `None` | Количество элементов на странице. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InviteListResponse`

**Pydantic-модель:** [`InviteListResponse`](../data-types/invites/InviteListResponse.md)

Ответ передаётся в `InviteListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `InviteList` | `object (InviteList)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`InviteList`](../data-types/invites/InviteList.md)

### Пример

```python
result = await client.invites.get_invites(
)
print(result)
```

## `client.invites.prolong_invite()`

Продлить срок действия приглашения.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `invites/{invite_id}/prolong` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `invite_id` | `str` | Да | — | Идентификатор приглашения. |
| `with_send` | `bool` | Нет | `True` | Параметр публичного метода SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InviteBoolResponse`

**Pydantic-модель:** [`InviteBoolResponse`](../data-types/invites/InviteBoolResponse.md)

Ответ передаётся в `InviteBoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.invites.prolong_invite(
    invite_id="invite-id",
    with_send=True,
)
print(result)
```

## `client.invites.resend_invite()`

Повторно отправить приглашение.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `invites/{invite_id}/send` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `invite_id` | `str` | Да | — | Идентификатор приглашения. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InviteResponse`

**Pydantic-модель:** [`InviteResponse`](../data-types/invites/InviteResponse.md)

Ответ передаётся в `InviteResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `InviteActionResult` | `object (InviteActionResult)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`InviteActionResult`](../data-types/invites/InviteActionResult.md)

### Пример

```python
result = await client.invites.resend_invite(
    invite_id="invite-id",
)
print(result)
```
