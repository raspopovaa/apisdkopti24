# `client.auth`

Методы авторизации пользователя, завершения сессии и получения сведений об учетной записи.

## `client.auth.auth_user()`

Авторизовать пользователя и открыть сессию SDK.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `authUser` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `contract_number` | `str | None` | Нет | `None` | Параметр публичного метода SDK. |

### Возвращаемое значение

**Тип после валидации:** `AuthUserResponse`

**Pydantic-модель:** [`AuthUserResponse`](../data-types/auth/AuthUserResponse.md)

Ответ передаётся в `AuthUserResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `AuthUserData` | `object (AuthUserData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`AuthUserData`](../data-types/auth/AuthUserData.md)

Возвращает типизированные данные авторизации, включая идентификатор сессии и доступные договоры.

### Пример

```python
result = await client.auth.auth_user(
)
print(result)
```

## `client.auth.get_info()`

Получение статистических данных по вызовам всех методов.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `info` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `period` | `str | None` | Нет | `None` | Период: месяц в формате `YYYY-MM` или конкретный день в формате `YYYY-MM-DD`. |

### Возвращаемое значение

**Тип после валидации:** `GetInfoResponse`

**Pydantic-модель:** [`GetInfoResponse`](../data-types/auth/GetInfoResponse.md)

Ответ передаётся в `GetInfoResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `InfoData` | `object (InfoData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`InfoData`](../data-types/auth/InfoData.md)

### Пример

```python
result = await client.auth.get_info(
)
print(result)
```

## `client.auth.logoff()`

Завершить серверную сессию и очистить локальное состояние клиента.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `logoff` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `LogoffResponse`

**Pydantic-модель:** [`LogoffResponse`](../data-types/auth/LogoffResponse.md)

Ответ передаётся в `LogoffResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.auth.logoff(
)
print(result)
```
