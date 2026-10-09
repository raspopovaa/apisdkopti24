---
description: "Создание, изменение и удаление групп карт, а также управление составом группы."
---

# `client.card_groups`

Создание, изменение и удаление групп карт, а также управление составом группы.

## `client.card_groups.get_card_groups()`

Получить группы карт выбранного договора.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v1 | `cardGroups` | Да | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `CardGroupListResponse`

**Pydantic-модель:** [`CardGroupListResponse`](../data-types/card_group/CardGroupListResponse.md)

Ответ передаётся в `CardGroupListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>CardGroupListData</code> | <code>object (CardGroupListData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`CardGroupListData`](../data-types/card_group/CardGroupListData.md)

### Пример

```python
result = await client.card_groups.get_card_groups(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_card_groups](../examples/card_groups/get_card_groups.md).

## `client.card_groups.remove_card_group()`

Удалить группу карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `removeCardGroup` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `group_id` | <code>str</code> | Да | — | Идентификатор группы топливных карт. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `RemoveCardGroupResponse`

**Pydantic-модель:** [`RemoveCardGroupResponse`](../data-types/card_group/RemoveCardGroupResponse.md)

Ответ передаётся в `RemoveCardGroupResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.card_groups.remove_card_group(
    group_id="group-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [remove_card_group](../examples/card_groups/remove_card_group.md).

## `client.card_groups.set_card_group()`

Создать группу карт или изменить существующую.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setCardGroup` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `name` | <code>str</code> | Да | — | Имя группы карт. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `group_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор группы топливных карт. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `SetCardGroupResponse`

**Pydantic-модель:** [`SetCardGroupResponse`](../data-types/card_group/SetCardGroupResponse.md)

Ответ передаётся в `SetCardGroupResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>SetCardGroupData</code> | <code>object (SetCardGroupData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`SetCardGroupData`](../data-types/card_group/SetCardGroupData.md)

### Пример

```python
result = await client.card_groups.set_card_group(
    name="name",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [set_card_group](../examples/card_groups/set_card_group.md).

## `client.card_groups.set_cards_to_group()`

Добавить карты в группу или удалить их из группы.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v1 | `setCardsToGroup` | Да | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `group_id` | <code>str</code> | Да | — | Идентификатор группы топливных карт. |
| `cards_list` | <code>Sequence[CardGroupAssignmentRequest &#124; Mapping[str, object]]</code> | Да | — | Список карт договора, добавляемых в группу или удаляемых из неё. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `SetCardsToGroupResponse`

**Pydantic-модель:** [`SetCardsToGroupResponse`](../data-types/card_group/SetCardsToGroupResponse.md)

Ответ передаётся в `SetCardsToGroupResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.card_groups.set_cards_to_group(
    group_id="group-id",
    cards_list="cards-list",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [set_cards_to_group](../examples/card_groups/set_cards_to_group.md).
