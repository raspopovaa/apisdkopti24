---
description: "Получение карт и их реквизитов, блокировка, комментарии, водители и операции с PIN."
---

# `client.cards`

Получение карт и их реквизитов, блокировка, комментарии, водители и операции с PIN.

## `client.cards.block_card()`

Заблокировать или разблокировать одну или несколько топливных карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `blockCard` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_ids` | <code>list[str]</code> | Да | — | Список идентификаторов топливных карт. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `block` | <code>bool</code> | Нет | `True` | `true` — заблокировать карту, `false` — разблокировать. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `IDListResponse`

**Pydantic-модель:** [`IDListResponse`](../data-types/cards/IDListResponse.md)

Ответ передаётся в `IDListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | Список идентификаторов обработанных карт |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)

### Пример

```python
result = await client.cards.block_card(
    card_ids=["item-id"],
    block=True,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [block_card](../examples/cards/block_card.md).

## `client.cards.get_card_detail()`

Получить детальную информацию о топливной карте.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `cards` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `CardDetailResponse`

**Pydantic-модель:** [`CardDetailResponse`](../data-types/cards/CardDetailResponse.md)

Ответ передаётся в `CardDetailResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>CardDetailData</code> | <code>object (CardDetailData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`CardDetailData`](../data-types/cards/CardDetailData.md)

### Пример

```python
result = await client.cards.get_card_detail(
    card_id="card-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_card_detail](../examples/cards/get_card_detail.md).

## `client.cards.get_card_drivers()`

Получить пользователей, привязанных к карте.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `cards/{card_id}/drivers` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `CardDriversResponse`

**Pydantic-модель:** [`CardDriversResponse`](../data-types/cards/CardDriversResponse.md)

Ответ передаётся в `CardDriversResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>CardDriversData</code> | <code>object (CardDriversData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`CardDriversData`](../data-types/cards/CardDriversData.md)

### Пример

```python
result = await client.cards.get_card_drivers(
    card_id="card-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_card_drivers](../examples/cards/get_card_drivers.md).

## `client.cards.get_cards_by_group()`

Получить карты выбранной группы.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `cards` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `group_id` | <code>str</code> | Да | — | Идентификатор группы топливных карт. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `CardGroupResponse`

**Pydantic-модель:** [`CardGroupResponse`](../data-types/cards/CardGroupResponse.md)

Ответ передаётся в `CardGroupResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>CardGroupData</code> | <code>object (CardGroupData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`CardGroupData`](../data-types/cards/CardGroupData.md)

### Пример

```python
result = await client.cards.get_cards_by_group(
    group_id="group-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_cards_by_group](../examples/cards/get_cards_by_group.md).

## `client.cards.get_cards_v1()`

Получить список топливных карт через API v1.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `cards` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `cache` | <code>bool</code> | Нет | `True` | Параметр публичного метода SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `CardsListResponse`

**Pydantic-модель:** [`CardsListResponse`](../data-types/cards/CardsListResponse.md)

Ответ передаётся в `CardsListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>CardsListData</code> | <code>object (CardsListData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`CardsListData`](../data-types/cards/CardsListData.md)

### Пример

```python
result = await client.cards.get_cards_v1(
    cache=True,
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_cards_v1](../examples/cards/get_cards_v1.md).

## `client.cards.get_cards_v2()`

Получить постраничный список топливных карт договора через API v2.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `cards` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `sort` | <code>str</code> | Нет | `'-id'` | Выражение сортировки. Префикс «-» задает сортировку по убыванию. |
| `q` | <code>str &#124; None</code> | Нет | `None` | Строка полнотекстового поиска. |
| `status` | <code>str &#124; None</code> | Нет | `None` | Параметр публичного метода SDK. |
| `carrier` | <code>str &#124; None</code> | Нет | `None` | Параметр публичного метода SDK. |
| `platon` | <code>bool &#124; None</code> | Нет | `None` | Параметр публичного метода SDK. |
| `avtodor` | <code>bool &#124; None</code> | Нет | `None` | Параметр публичного метода SDK. |
| `users` | <code>bool &#124; None</code> | Нет | `None` | Параметр публичного метода SDK. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `page` | <code>int &#124; None</code> | Нет | `None` | Номер страницы результата. |
| `onpage` | <code>int &#124; None</code> | Нет | `None` | Количество элементов на странице. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `CardsV2Response`

**Pydantic-модель:** [`CardsV2Response`](../data-types/cards/CardsV2Response.md)

Ответ передаётся в `CardsV2Response.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>CardsV2Data</code> | <code>object (CardsV2Data)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`CardsV2Data`](../data-types/cards/CardsV2Data.md)

### Пример

```python
result = await client.cards.get_cards_v2(
    sort='-id',
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_cards_v2](../examples/cards/get_cards_v2.md).

## `client.cards.reset_pin()`

Сбросить PIN карты по проверочному коду.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/resetPIN` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `code` | <code>str</code> | Да | — | Код подтверждения, полученный по email. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `BoolResponse`

**Pydantic-модель:** [`BoolResponse`](../data-types/cards/BoolResponse.md)

Ответ передаётся в `BoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.cards.reset_pin(
    card_id="card-id",
    code="code",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [reset_pin](../examples/cards/reset_pin.md).

## `client.cards.set_card_comment()`

Установить комментарий для карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setCardComment` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `comment` | <code>str</code> | Да | — | Комментарий к топливной карте. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `BoolResponse`

**Pydantic-модель:** [`BoolResponse`](../data-types/cards/BoolResponse.md)

Ответ передаётся в `BoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.cards.set_card_comment(
    card_id="card-id",
    comment="comment",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [set_card_comment](../examples/cards/set_card_comment.md).

## `client.cards.verify_pin()`

Запросить проверочный код для сброса PIN карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/verifyPIN` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `BoolResponse`

**Pydantic-модель:** [`BoolResponse`](../data-types/cards/BoolResponse.md)

Ответ передаётся в `BoolResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.cards.verify_pin(
    card_id="card-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [verify_pin](../examples/cards/verify_pin.md).
