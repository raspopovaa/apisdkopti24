---
description: "Выпуск виртуальных карт, управление МПК и формирование платёжных строк для QR-кодов."
---

# `client.virtual_cards`

Выпуск виртуальных карт, управление МПК и формирование платёжных строк для QR-кодов.

## `client.virtual_cards.confirm_mpc()`

Подтвердить выпуск МПК кодом из SMS.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/confirmMPC` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `code` | <code>str</code> | Да | — | Код подтверждения выпуска МПК из SMS. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `MPCActionResponse`

**Pydantic-модель:** [`MPCActionResponse`](../data-types/virtual_cards/MPCActionResponse.md)

Ответ передаётся в `MPCActionResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.virtual_cards.confirm_mpc(
    card_id="card-id",
    code="code",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [confirm_mpc](../examples/virtual_cards/confirm_mpc.md).

## `client.virtual_cards.create_virtual_card()`

Выпуск виртуальной карты (старый метод POST /vip/v2/cards)

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `user_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор пользователя. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `template_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор шаблона. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `VirtualCardResponse`

**Pydantic-модель:** [`VirtualCardResponse`](../data-types/virtual_cards/VirtualCardResponse.md)

Ответ передаётся в `VirtualCardResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>StatusModel</code> | <code>object (StatusModel)</code> | Да | Нет | Статус ответа от сервера |
| `data` | <code>VirtualCardData</code> | <code>object (VirtualCardData)</code> | Да | Нет | Информация о выпущенной виртуальной карте |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Время ответа сервера в формате Unix Timestamp |

**Вложенные модели:**
- [`StatusModel`](../data-types/virtual_cards/StatusModel.md)
- [`VirtualCardData`](../data-types/virtual_cards/VirtualCardData.md)

### Пример

```python
result = await client.virtual_cards.create_virtual_card(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [create_virtual_card](../examples/virtual_cards/create_virtual_card.md).

## `client.virtual_cards.delete_mpc()`

Удалить мобильный профиль карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/deleteMPC` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |

### Возвращаемое значение

**Тип после валидации:** `SimpleActionResponse`

**Pydantic-модель:** [`SimpleActionResponse`](../data-types/virtual_cards/SimpleActionResponse.md)

Ответ передаётся в `SimpleActionResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>StatusModel</code> | <code>object (StatusModel)</code> | Да | Нет | Статус выполнения операции |
| `data` | <code>bool</code> | <code>boolean</code> | Да | Нет | Результат операции (True — успешно) |
| `timestamp` | <code>int</code> | <code>integer</code> | Да | Нет | Время выполнения запроса (Unix Timestamp) |

**Вложенные модели:**
- [`StatusModel`](../data-types/virtual_cards/StatusModel.md)

### Пример

```python
result = await client.virtual_cards.delete_mpc(
    card_id="card-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [delete_mpc](../examples/virtual_cards/delete_mpc.md).

## `client.virtual_cards.generate_payment_qr()`

Сформировать одноразовую платёжную строку для QR-кода.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/pay` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `pin` | <code>str</code> | Да | — | PIN мобильного профиля карты из 4–8 цифр. Значение не должно попадать в логи. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `PaymentQRResponse`

**Pydantic-модель:** [`PaymentQRResponse`](../data-types/virtual_cards/PaymentQRResponse.md)

Ответ передаётся в `PaymentQRResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>PaymentQRData</code> | <code>object (PaymentQRData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`PaymentQRData`](../data-types/virtual_cards/PaymentQRData.md)

Возвращает BER-TLV строку, срок её действия и счётчики МПК.

### Пример

```python
result = await client.virtual_cards.generate_payment_qr(
    card_id="card-id",
    pin="pin",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [generate_payment_qr](../examples/virtual_cards/generate_payment_qr.md).

## `client.virtual_cards.get_mpc_qr_list()`

Получить список выпущенных мобильных профилей карт.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| GET | v2 | `MPC` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `MPCListResponse`

**Pydantic-модель:** [`MPCListResponse`](../data-types/virtual_cards/MPCListResponse.md)

Ответ передаётся в `MPCListResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>ResponseStatus</code> | <code>object (ResponseStatus)</code> | Да | Нет | Статус ответа API |
| `data` | <code>MPCListData</code> | <code>object (MPCListData)</code> | Да | Нет | Типизированные данные ответа API |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`MPCListData`](../data-types/virtual_cards/MPCListData.md)

### Пример

```python
result = await client.virtual_cards.get_mpc_qr_list(
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [get_mpc_qr_list](../examples/virtual_cards/get_mpc_qr_list.md).

## `client.virtual_cards.init_mpc()`

Начать выпуск мобильного профиля карты.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/initMPC` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `user_id` | <code>str</code> | Да | — | ID пользователя, к которому привязана карта. |
| `pin` | <code>str</code> | Да | — | Новый PIN мобильного профиля из 4–8 цифр. |
| `device_id` | <code>str</code> | Да | — | Идентификатор устройства длиной 1–255 символов. |
| `device_name` | <code>str</code> | Да | — | Название устройства длиной 11–17 символов. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `MPCActionResponse`

**Pydantic-модель:** [`MPCActionResponse`](../data-types/virtual_cards/MPCActionResponse.md)

Ответ передаётся в `MPCActionResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.virtual_cards.init_mpc(
    card_id="card-id",
    user_id="user-id",
    pin="pin",
    device_id="device-id",
    device_name="device-name",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [init_mpc](../examples/virtual_cards/init_mpc.md).

## `client.virtual_cards.release_virtual_card()`

Выпустить виртуальную карту по типу или шаблону.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/release` | Нет | Да |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `type_` | <code>str &#124; None</code> | Нет | `None` | Тип карты: `limit` — лимитная схема, `wallet` — электронный кошелёк. Обязателен, если не указан `template_id`; не передаётся, если указан `template_id`. |
| `template_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор шаблона. |
| `user_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор пользователя. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `VirtualCardResponse`

**Pydantic-модель:** [`VirtualCardResponse`](../data-types/virtual_cards/VirtualCardResponse.md)

Ответ передаётся в `VirtualCardResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>StatusModel</code> | <code>object (StatusModel)</code> | Да | Нет | Статус ответа от сервера |
| `data` | <code>VirtualCardData</code> | <code>object (VirtualCardData)</code> | Да | Нет | Информация о выпущенной виртуальной карте |
| `timestamp` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | Время ответа сервера в формате Unix Timestamp |

**Вложенные модели:**
- [`StatusModel`](../data-types/virtual_cards/StatusModel.md)
- [`VirtualCardData`](../data-types/virtual_cards/VirtualCardData.md)

### Пример

```python
result = await client.virtual_cards.release_virtual_card(
    template_id="template-id",
    user_id="user-id",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [release_virtual_card](../examples/virtual_cards/release_virtual_card.md).

## `client.virtual_cards.reset_mpc()`

Сбросить блокировку выпуска или оплаты по МПК.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/resetMPC` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `type_` | <code>str</code> | Нет | `'ResetCounterCode'` | `ResetCounterCode` сбрасывает блокировку оплаты, `ResetCounterMPC` — блокировку выпуска МПК. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |

### Возвращаемое значение

**Тип после валидации:** `ResetMPCResponse`

**Pydantic-модель:** [`ResetMPCResponse`](../data-types/virtual_cards/ResetMPCResponse.md)

Ответ передаётся в `ResetMPCResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | <code>StatusModel</code> | <code>object (StatusModel)</code> | Да | Нет | Статус выполнения операции сброса |
| `data` | <code>bool</code> | <code>boolean</code> | Да | Нет | Результат операции (True — успешно) |
| `timestamp` | <code>int</code> | <code>integer</code> | Да | Нет | Время выполнения запроса (Unix Timestamp) |

**Вложенные модели:**
- [`StatusModel`](../data-types/virtual_cards/StatusModel.md)

### Пример

```python
result = await client.virtual_cards.reset_mpc(
    card_id="card-id",
    type_='ResetCounterCode',
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [reset_mpc](../examples/virtual_cards/reset_mpc.md).

## `client.virtual_cards.update_mpc()`

Перевыпустить ключи МПК и при необходимости изменить PIN.

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/updateMPC` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | Идентификатор топливной карты. |
| `pin` | <code>str</code> | Да | — | Текущий PIN мобильного профиля из 4–8 цифр. |
| `new_pin` | <code>str &#124; None</code> | Нет | `None` | Новый PIN из 4–8 цифр. Если не передан, API перевыпускает ключи оплаты без смены PIN. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `MPCActionResponse`

**Pydantic-модель:** [`MPCActionResponse`](../data-types/virtual_cards/MPCActionResponse.md)

Ответ передаётся в `MPCActionResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.virtual_cards.update_mpc(
    card_id="card-id",
    pin="pin",
)
print(result)
```

Подробный учебный пример с HTTP-запросом, ответом и ошибками: [update_mpc](../examples/virtual_cards/update_mpc.md).
