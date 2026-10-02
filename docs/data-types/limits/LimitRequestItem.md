---
description: "Строгий элемент запроса установки продуктового лимита."
---
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
| `id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID изменяемого лимита |
| `contract_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID договора |
| `card_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID карты |
| `group_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID группы карт |
| `product_type` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>productType</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID типа продукта |
| `product_group` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>productGroup</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | ID группы продуктов |
| `amount` | <code>LimitAmountRequest &#124; None</code> | <code>object (LimitAmountRequest) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitAmountRequest, None | Объёмный лимит |
| `sum` | <code>LimitSumRequest &#124; None</code> | <code>object (LimitSumRequest) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitSumRequest, None | Денежный лимит |
| `term` | <code>LimitTermRequest &#124; None</code> | <code>object (LimitTermRequest) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitTermRequest, None | Условия действия лимита |
| `transactions` | <code>LimitTransactionsRequest &#124; None</code> | <code>object (LimitTransactionsRequest) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitTransactionsRequest, None | Лимит количества транзакций |
| `time` | <code>LimitTimeRequest</code> | <code>object (LimitTimeRequest)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью LimitTimeRequest. | Период действия лимита |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `model_validator` | `validate_target_and_value` | <code>вся модель</code> | <code>after</code> | Пользовательская проверка `validate_target_and_value`. |

## Вложенные модели

- [`LimitAmountRequest`](LimitAmountRequest.md)
- [`LimitSumRequest`](LimitSumRequest.md)
- [`LimitTermRequest`](LimitTermRequest.md)
- [`LimitTransactionsRequest`](LimitTransactionsRequest.md)
- [`LimitTimeRequest`](LimitTimeRequest.md)
