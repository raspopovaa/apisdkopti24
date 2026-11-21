---
description: "Получение списка транзакций и детальной информации по отдельной операции."
---

# `client.transactions`

Получение списка транзакций и детальной информации по отдельной операции.

## `client.transactions.get_card_transactions_v2()`

Получить страницу транзакций карты за период не более месяца (v2).

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `cards/{card_id}/transactions` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | не задано | Идентификатор топливной карты. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора. Если не передан, берётся договор сессии. |
| `date_from` | <code>str</code> | Да | не задано | Начало периода, ``YYYY-MM-DD``. |
| `date_to` | <code>str</code> | Да | не задано | Конец периода, ``YYYY-MM-DD``; период не длиннее числа дней в месяце ``date_from``. |
| `page_limit` | <code>int</code> | Нет | `100` | Количество транзакций на странице. |
| `page_offset` | <code>int</code> | Нет | `0` | Количество транзакций, которые нужно пропустить. |
| `filter_fn` | <code>Callable[[&lt;class 'apisdkopti24.models.transactions.TransactionItemV2'&gt;], bool] &#124; None</code> | Нет | `None` | Устарел: фильтр уже полученной страницы на стороне SDK, выдаёт ``DeprecationWarning``. |
| `sort_by` | <code>str &#124; None</code> | Нет | `None` | Устарел: поле для сортировки уже полученной страницы на стороне SDK, выдаёт ``DeprecationWarning``. |
| `reverse` | <code>bool</code> | Нет | `False` | Устарел: обратный порядок для ``sort_by``, выдаёт ``DeprecationWarning``. |

### Возвращаемое значение

**Тип после валидации:** `TransactionsV2Response`

**Pydantic-модель:** [`TransactionsV2Response`](../data-types/transactions/TransactionsV2Response.md)

Ответ передаётся в `TransactionsV2Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TransactionsV2Data</code> | <code>object (TransactionsV2Data)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TransactionsV2Data`](../data-types/transactions/TransactionsV2Data.md)

### Пример

```python
result = await client.transactions.get_card_transactions_v2(
    card_id="card-id",
    date_from="date-from",
    date_to="date-to",
    page_limit=100,
    page_offset=0,
    reverse=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_card_transactions_v2](../examples/transactions/get_card_transactions_v2.md).

## `client.transactions.get_transaction_detail()`

Получить детальную информацию об одной транзакции.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `transactions/{transaction_id}` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `transaction_id` | <code>str</code> | Да | не задано | Идентификатор транзакции. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора. Если не передан, берётся договор сессии. |

### Возвращаемое значение

**Тип после валидации:** `TransactionDetailResponse`

**Pydantic-модель:** [`TransactionDetailResponse`](../data-types/transactions/TransactionDetailResponse.md)

Ответ передаётся в `TransactionDetailResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TransactionDetailData</code> | <code>object (TransactionDetailData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TransactionDetailData`](../data-types/transactions/TransactionDetailData.md)

Для несуществующего transaction_id сервер отвечает 200 с data.total_count = 0 и пустым data.result, а не 404: SDK не выбрасывает NotFoundError. Проверяйте total_count перед чтением result.

### Пример

```python
result = await client.transactions.get_transaction_detail(
    transaction_id="transaction-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_transaction_detail](../examples/transactions/get_transaction_detail.md).

## `client.transactions.get_transactions_v1()`

Получить последние транзакции договора, при необходимости: одной карты (v1).

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `transactions` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора. Если не передан, берётся договор сессии. |
| `card_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор топливной карты. |
| `count` | <code>int</code> | Нет | `20` | Сколько последних транзакций вернуть, больше 0. |
| `filter_fn` | <code>Callable[[&lt;class 'apisdkopti24.models.transactions.TransactionV1'&gt;], bool] &#124; None</code> | Нет | `None` | Устарел: фильтр уже полученной страницы на стороне SDK, выдаёт ``DeprecationWarning``. |
| `sort_by` | <code>str &#124; None</code> | Нет | `None` | Устарел: поле для сортировки уже полученной страницы на стороне SDK, выдаёт ``DeprecationWarning``. |
| `reverse` | <code>bool</code> | Нет | `False` | Устарел: обратный порядок для ``sort_by``, выдаёт ``DeprecationWarning``. |

### Возвращаемое значение

**Тип после валидации:** `TransactionsV1Response`

**Pydantic-модель:** [`TransactionsV1Response`](../data-types/transactions/TransactionsV1Response.md)

Ответ передаётся в `TransactionsV1Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TransactionsV1Data</code> | <code>object (TransactionsV1Data)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TransactionsV1Data`](../data-types/transactions/TransactionsV1Data.md)

### Пример

```python
result = await client.transactions.get_transactions_v1(
    count=20,
    reverse=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_transactions_v1](../examples/transactions/get_transactions_v1.md).

## `client.transactions.get_transactions_v2()`

Получить транзакции договора за заданный период.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `transactions` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | ID договора. Если не передан, берётся договор сессии. |
| `date_from` | <code>str</code> | Да | не задано | Начало периода, ``YYYY-MM-DD``. |
| `date_to` | <code>str</code> | Да | не задано | Конец периода, ``YYYY-MM-DD``; период не длиннее числа дней в месяце ``date_from``. |
| `page_limit` | <code>int</code> | Нет | `100` | Транзакций на странице, больше 0. |
| `page_offset` | <code>int</code> | Нет | `0` | Сколько транзакций пропустить от начала выборки, не меньше 0. |
| `filter_fn` | <code>Callable[[&lt;class 'apisdkopti24.models.transactions.TransactionItemV2'&gt;], bool] &#124; None</code> | Нет | `None` | Устарел: фильтр уже полученной страницы на стороне SDK, выдаёт ``DeprecationWarning``. |
| `sort_by` | <code>str &#124; None</code> | Нет | `None` | Устарел: поле для сортировки уже полученной страницы на стороне SDK, выдаёт ``DeprecationWarning``. |
| `reverse` | <code>bool</code> | Нет | `False` | Устарел: обратный порядок для ``sort_by``, выдаёт ``DeprecationWarning``. |

### Возвращаемое значение

**Тип после валидации:** `TransactionsV2Response`

**Pydantic-модель:** [`TransactionsV2Response`](../data-types/transactions/TransactionsV2Response.md)

Ответ передаётся в `TransactionsV2Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>TransactionsV2Data</code> | <code>object (TransactionsV2Data)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`TransactionsV2Data`](../data-types/transactions/TransactionsV2Data.md)

### Пример

```python
result = await client.transactions.get_transactions_v2(
    date_from="date-from",
    date_to="date-to",
    page_limit=100,
    page_offset=0,
    reverse=False,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_transactions_v2](../examples/transactions/get_transactions_v2.md).
