---
description: "Данные договора, платежи, счета, документы и заказ топливных карт."
---

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
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `ContractDataResponse`

**Pydantic-модель:** [`ContractDataResponse`](../data-types/contracts/ContractDataResponse.md)

Ответ передаётся в `ContractDataResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>ContractResponse</code> | <code>object (ContractResponse)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`ContractResponse`](../data-types/contracts/ContractResponse.md)

### Пример

```python
result = await client.contracts.get_contract_data(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_contract_data](../examples/contracts/get_contract_data.md).

## `client.contracts.get_documents()`

Получение списка первичных документов (номер документа, дата, сумма, НДС, номер договора и пр.).

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `documents` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `date_start` | <code>str</code> | Да | — | Дата начала периода в формате `YYYY-MM-DD`. |
| `date_end` | <code>str</code> | Да | — | Дата окончания периода в формате `YYYY-MM-DD`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `page` | <code>int</code> | Нет | `1` | Номер страницы результата. |
| `on_page` | <code>int</code> | Нет | `10` | Количество элементов на странице. |

### Возвращаемое значение

**Тип после валидации:** `DocumentsResponse`

**Pydantic-модель:** [`DocumentsResponse`](../data-types/contracts/DocumentsResponse.md)

Ответ передаётся в `DocumentsResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>DocumentsData</code> | <code>object (DocumentsData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

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

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_documents](../examples/contracts/get_documents.md).

## `client.contracts.get_invoices()`

Получение списка счетов на оплату.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `invoices` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InvoicesResponse`

**Pydantic-модель:** [`InvoicesResponse`](../data-types/contracts/InvoicesResponse.md)

Ответ передаётся в `InvoicesResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>InvoicesData</code> | <code>object (InvoicesData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`InvoicesData`](../data-types/contracts/InvoicesData.md)

### Пример

```python
result = await client.contracts.get_invoices(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_invoices](../examples/contracts/get_invoices.md).

## `client.contracts.get_payments()`

Получение данных о платежах по контракту.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `getPayments` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `PaymentsResponse`

**Pydantic-модель:** [`PaymentsResponse`](../data-types/contracts/PaymentsResponse.md)

Ответ передаётся в `PaymentsResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>PaymentsData</code> | <code>object (PaymentsData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`PaymentsData`](../data-types/contracts/PaymentsData.md)

### Пример

```python
result = await client.contracts.get_payments(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_payments](../examples/contracts/get_payments.md).

## `client.contracts.order_cards()`

Заказ необходимого количества топливных карт в определенном офисе продаж.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `orderCards` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `count` | <code>int</code> | Да | — | Количество заказываемых карт. |
| `office_id` | <code>str</code> | Да | — | ID офиса продаж из справочника `Office`. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `OrderCardsResponse`

**Pydantic-модель:** [`OrderCardsResponse`](../data-types/contracts/OrderCardsResponse.md)

Ответ передаётся в `OrderCardsResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.contracts.order_cards(
    count=1,
    office_id="office-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [order_cards](../examples/contracts/order_cards.md).

## `client.contracts.order_documents_email()`

Заказ первичных документов по ID документа на указанные email – адреса (до 5 адресов).

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `documents` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `ids` | <code>list[str]</code> | Да | — | Список ID документов. В API параметр называется `id`. |
| `fmt` | <code>Literal[pdf, xlsx]</code> | Да | — | Формат документа: `pdf` или `xlsx`. В API параметр называется `format`. |
| `emails` | <code>list[str]</code> | Да | — | Список email-адресов для отправки документов, не более пяти. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `DocumentsOrderResponse`

**Pydantic-модель:** [`DocumentsOrderResponse`](../data-types/contracts/DocumentsOrderResponse.md)

Ответ передаётся в `DocumentsOrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.contracts.order_documents_email(
    ids=["item-id"],
    fmt="fmt",
    emails=["item-id"],
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [order_documents_email](../examples/contracts/order_documents_email.md).

## `client.contracts.order_invoice()`

Заказать счёт на оплату и отправить его на email.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `invoice` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `amount` | <code>Decimal</code> | Да | — | Сумма счёта в рублях. В API параметр называется `sum`. |
| `email` | <code>str</code> | Да | — | Email-адрес для отправки счёта. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `InvoiceOrderResponse`

**Pydantic-модель:** [`InvoiceOrderResponse`](../data-types/contracts/InvoiceOrderResponse.md)

Ответ передаётся в `InvoiceOrderResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.contracts.order_invoice(
    amount="amount",
    email="email",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [order_invoice](../examples/contracts/order_invoice.md).
