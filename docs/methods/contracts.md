# `client.contracts`

Данные договора, платежи, счета, документы и заказ топливных карт.

## `client.contracts.get_contract_data()`

Получение информации о контракте.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getPartContractData` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ContractDataResponse`

**Pydantic-модель:** [`ContractDataResponse`](../data-types/contracts/ContractDataResponse.md)

Ответ передаётся в `ContractDataResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `ContractResponse` | `object (ContractResponse)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ContractResponse`](../data-types/contracts/ContractResponse.md)

### Пример

```python
result = await client.contracts.get_contract_data(
)
print(result)
```

## `client.contracts.get_documents()`

Получение списка первичных документов (номер документа, дата, сумма, НДС, номер договора и пр.).

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `documents` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `date_start` | `str` | Да | — | Дата начала периода в формате `YYYY-MM-DD`. |
| `date_end` | `str` | Да | — | Дата окончания периода в формате `YYYY-MM-DD`. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `page` | `int` | Нет | `1` | Номер страницы результата. |
| `on_page` | `int` | Нет | `10` | Количество элементов на странице. |

### Возвращаемое значение

**Тип после валидации:** `DocumentsResponse`

**Pydantic-модель:** [`DocumentsResponse`](../data-types/contracts/DocumentsResponse.md)

Ответ передаётся в `DocumentsResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `DocumentsData` | `object (DocumentsData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`DocumentsData`](../data-types/contracts/DocumentsData.md)

### Пример

```python
result = await client.contracts.get_documents(
    date_start="date-start",
    date_end="date-end",
    page=1,
    on_page=10,
)
print(result)
```

## `client.contracts.get_invoices()`

Получение списка счетов на оплату.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `invoices` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InvoicesResponse`

**Pydantic-модель:** [`InvoicesResponse`](../data-types/contracts/InvoicesResponse.md)

Ответ передаётся в `InvoicesResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `InvoicesData` | `object (InvoicesData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`InvoicesData`](../data-types/contracts/InvoicesData.md)

### Пример

```python
result = await client.contracts.get_invoices(
)
print(result)
```

## `client.contracts.get_payments()`

Получение данных о платежах по контракту.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getPayments` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `PaymentsResponse`

**Pydantic-модель:** [`PaymentsResponse`](../data-types/contracts/PaymentsResponse.md)

Ответ передаётся в `PaymentsResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `PaymentsData` | `object (PaymentsData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`PaymentsData`](../data-types/contracts/PaymentsData.md)

### Пример

```python
result = await client.contracts.get_payments(
)
print(result)
```

## `client.contracts.order_cards()`

Заказ необходимого количества топливных карт в определенном офисе продаж.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `orderCards` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `count` | `int` | Да | — | Количество заказываемых карт. |
| `office_id` | `str` | Да | — | ID офиса продаж из справочника `Office`. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `OrderCardsResponse`

**Pydantic-модель:** [`OrderCardsResponse`](../data-types/contracts/OrderCardsResponse.md)

Ответ передаётся в `OrderCardsResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.contracts.order_cards(
    count=1,
    office_id="office-id",
)
print(result)
```

## `client.contracts.order_documents_email()`

Заказ первичных документов по ID документа на указанные email – адреса (до 5 адресов).

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `documents` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `ids` | `list[str]` | Да | — | Список ID документов. В API параметр называется `id`. |
| `fmt` | `Literal[pdf, xlsx]` | Да | — | Формат документа: `pdf` или `xlsx`. В API параметр называется `format`. |
| `emails` | `list[str]` | Да | — | Список email-адресов для отправки документов, не более пяти. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `DocumentsOrderResponse`

**Pydantic-модель:** [`DocumentsOrderResponse`](../data-types/contracts/DocumentsOrderResponse.md)

Ответ передаётся в `DocumentsOrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.contracts.order_documents_email(
    ids=["item-id"],
    fmt="fmt",
    emails=["item-id"],
)
print(result)
```

## `client.contracts.order_invoice()`

Заказать счёт на оплату и отправить его на email.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `invoice` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `amount` | `Decimal` | Да | — | Сумма счёта в рублях. В API параметр называется `sum`. |
| `email` | `str` | Да | — | Email-адрес для отправки счёта. |
| `contract_id` | `str | None` | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InvoiceOrderResponse`

**Pydantic-модель:** [`InvoiceOrderResponse`](../data-types/contracts/InvoiceOrderResponse.md)

Ответ передаётся в `InvoiceOrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.contracts.order_invoice(
    amount="amount",
    email="email",
)
print(result)
```
