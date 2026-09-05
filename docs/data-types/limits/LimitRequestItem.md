# `LimitRequestItem`

Строгий элемент запроса установки продуктового лимита.

!!! info "Назначение Pydantic"
    Тип модели: **request**. Правила ниже применяются, когда вызывающий код явно создаёт `LimitRequestItem` или вызывает `LimitRequestItem.model_validate(payload)`. Наличие request-модели не означает, что каждый метод SDK автоматически создаёт её: фактический входной контракт определяется сигнатурой соответствующего сервисного метода.

## Поведение модели

| Настройка | Значение | Фактическое поведение |
|---|---|---|
| Дополнительные поля (`extra`) | `forbid` | Дополнительные поля запрещены и вызывают ValidationError. |
| Проверка default | `True` | Значения по умолчанию также проходят валидацию. |
| Заполнение по имени поля | `True` | Разрешено использовать имя поля наряду с alias. |
| Число → строка | `False` | Для строковых полей числовые значения могут быть преобразованы в строку. |

## Поля и проверки

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `id` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID изменяемого лимита |
| `contract_id` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID договора |
| `card_id` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID карты |
| `group_id` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID группы карт |
| `product_type` | `str \| None` | `string \| null` | Нет | Да | `None` | `productType` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | — |
| `product_group` | `str \| None` | `string \| null` | Нет | Да | `None` | `productGroup` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | — |
| `amount` | `LimitAmountRequest \| None` | `object (LimitAmountRequest) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: LimitAmountRequest, None | — |
| `sum` | `LimitSumRequest \| None` | `object (LimitSumRequest) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: LimitSumRequest, None | — |
| `term` | `LimitTermRequest \| None` | `object (LimitTermRequest) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: LimitTermRequest, None | — |
| `transactions` | `LimitTransactionsRequest \| None` | `object (LimitTransactionsRequest) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: LimitTransactionsRequest, None | — |
| `time` | `LimitTimeRequest` | `object (LimitTimeRequest)` | Да | Нет | `—` | `—` | — | Вложенный объект рекурсивно проверяется моделью LimitTimeRequest. | Период действия лимита |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`LimitAmountRequest`](LimitAmountRequest.md)
- [`LimitSumRequest`](LimitSumRequest.md)
- [`LimitTermRequest`](LimitTermRequest.md)
- [`LimitTransactionsRequest`](LimitTransactionsRequest.md)
- [`LimitTimeRequest`](LimitTimeRequest.md)
