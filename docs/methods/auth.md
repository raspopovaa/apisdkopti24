---
description: "Методы авторизации пользователя, завершения сессии и получения сведений об учетной записи."
---

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
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Локально выбрать договор по ID после получения ответа. Параметр не отправляется в authUser. |
| `contract_number` | <code>str &#124; None</code> | Нет | `None` | Локально выбрать договор по номеру после получения ответа. Параметр не отправляется в authUser. |

### Возвращаемое значение

**Тип после валидации:** `AuthUserResponse`

**Pydantic-модель:** [`AuthUserResponse`](../data-types/auth/AuthUserResponse.md)

Ответ передаётся в `AuthUserResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>AuthUserData</code> | <code>object (AuthUserData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`AuthUserData`](../data-types/auth/AuthUserData.md)

Возвращает типизированные данные авторизации, включая идентификатор сессии и доступные договоры. Один договор SDK выбирает автоматически. Если договоров несколько и селектор не передан, метод вызывает ContractSelectionError; варианты доступны в exc.available_contracts. Одновременно передавать contract_id и contract_number нельзя.

### Пример

```python
auth = await client.auth.auth_user(contract_id="contract-id")
print("Авторизация выполнена")
print("Количество доступных договоров:", len(auth.data.contracts))
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [auth_user](../examples/auth/auth_user.md).

## `client.auth.get_info()`

Получение статистических данных по вызовам всех методов.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `info` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `period` | <code>str &#124; None</code> | Нет | `None` | Период: месяц в формате `YYYY-MM` или конкретный день в формате `YYYY-MM-DD`. |

### Возвращаемое значение

**Тип после валидации:** `GetInfoResponse`

**Pydantic-модель:** [`GetInfoResponse`](../data-types/auth/GetInfoResponse.md)

Ответ передаётся в `GetInfoResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>InfoData</code> | <code>object (InfoData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`InfoData`](../data-types/auth/InfoData.md)

### Пример

```python
result = await client.auth.get_info(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_info](../examples/auth/get_info.md).

## `client.auth.logoff()`

Завершить серверную сессию и очистить локальное состояние клиента.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `logoff` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `LogoffResponse | None`

**Pydantic-модель:** [`LogoffResponse`](../data-types/auth/LogoffResponse.md)

Ответ передаётся в `LogoffResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.auth.logoff(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [logoff](../examples/auth/logoff.md).
