---
description: "Переводы между договором и картой, а также выбор продуктовой схемы карты."
---

# `client.ewallet`

Переводы между договором и картой, а также выбор продуктовой схемы карты.

## `client.ewallet.move_to_card()`

Перевести деньги со счёта договора на электронный кошелёк карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `moveToCard` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `amount` | <code>Decimal</code> | Да | — | Сумма перевода. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `MoveToCardResponse`

**Pydantic-модель:** [`MoveToCardResponse`](../data-types/ewallet/MoveToCardResponse.md)

Ответ передаётся в `MoveToCardResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.ewallet.move_to_card(
    card_id="card-id",
    amount="amount",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [move_to_card](../examples/ewallet/move_to_card.md).

## `client.ewallet.move_to_contract()`

Перевести деньги с электронного кошелька карты обратно на договор.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `moveToContract` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `amount` | <code>Decimal</code> | Да | — | Сумма перевода. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `MoveToContractResponse`

**Pydantic-модель:** [`MoveToContractResponse`](../data-types/ewallet/MoveToContractResponse.md)

Ответ передаётся в `MoveToContractResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.ewallet.move_to_contract(
    card_id="card-id",
    amount="amount",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [move_to_contract](../examples/ewallet/move_to_contract.md).

## `client.ewallet.set_card_product()`

Изменить тип карт: лимитная (``limit``) или электронный кошелёк (``wallet``).

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setCardProduct` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `card_ids` | <code>list[str]</code> | Да | — | Список идентификаторов топливных карт. |
| `product` | <code>Literal[wallet, limit]</code> | Да | — | Тип продукта: `wallet` или `limit`. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `SetCardProductResponse`

**Pydantic-модель:** [`SetCardProductResponse`](../data-types/ewallet/SetCardProductResponse.md)

Ответ передаётся в `SetCardProductResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | ID карт с изменённым типом продукта |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.ewallet.set_card_product(
    card_ids=["item-id"],
    product="product",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [set_card_product](../examples/ewallet/set_card_product.md).
