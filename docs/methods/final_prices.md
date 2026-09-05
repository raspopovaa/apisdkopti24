# `client.final_prices`

Проверка возможности покупки и расчет итоговых цен по карте.

## `client.final_prices.check_purchase()`

Проверка возможности проведения транзакции по карте
(POST /vip/v2/cards/{card_id}/checkPurchase)

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/checkPurchase` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | `str` | Да | — | Идентификатор топливной карты. |
| `poi_id` | `str` | Да | — | ID точки обслуживания. |
| `goods` | `list[dict[str, Any]]` | Да | — | Массив данных о товарах; для каждого товара указываются `code`, `quantity` и `price`. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `CheckPurchaseResponse`

**Pydantic-модель:** [`CheckPurchaseResponse`](../data-types/final_prices/CheckPurchaseResponse.md)

Ответ передаётся в `CheckPurchaseResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

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
result = await client.final_prices.check_purchase(
    card_id="card-id",
    poi_id="poi-id",
    goods={},
)
print(result)
```

## `client.final_prices.get_final_prices()`

Получение финальных цен на АЗС по карте (POST /vip/v2/cards/{card_id}/calculatePrices)

### Маршрут

| HTTP | API | Route | DEMO | Тарифицируется |
|---:|---:|---|:---:|:---:|
| POST | v2 | `cards/{card_id}/calculatePrices` | Нет | Нет |

### Параметры

| Параметр | Python-тип | Обязательный | Значение по умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | `str` | Да | — | Идентификатор топливной карты. |
| `poi_id` | `str` | Да | — | ID точки обслуживания. |
| `goods` | `list[str]` | Да | — | Массив идентификаторов продуктов. |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Возвращаемое значение

**Тип после валидации:** `FinalPricesResponse`

**Pydantic-модель:** [`FinalPricesResponse`](../data-types/final_prices/FinalPricesResponse.md)

Ответ передаётся в `FinalPricesResponse.model_validate(payload)`. Pydantic проверяет обязательные поля, преобразует значения по аннотациям и рекурсивно валидирует вложенные модели.

#### Поля возвращаемой модели

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | Описание |
|---|---|---|:---:|:---:|---|
| `status` | `ResponseStatus` | `object (ResponseStatus)` | Да | Нет | Статус ответа API |
| `data` | `FinalPricesData` | `object (FinalPricesData)` | Да | Нет | Типизированные данные ответа API |
| `timestamp` | `int \| None` | `integer \| null` | Нет | Да | Метка времени ответа API |

**Вложенные модели:**
- [`ResponseStatus`](../data-types/modeling/ResponseStatus.md)
- [`FinalPricesData`](../data-types/final_prices/FinalPricesData.md)

### Пример

```python
result = await client.final_prices.get_final_prices(
    card_id="card-id",
    poi_id="poi-id",
    goods=["item-id"],
)
print(result)
```
