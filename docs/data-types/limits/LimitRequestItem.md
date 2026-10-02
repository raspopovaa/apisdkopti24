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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Описание | Ограничения схемы | Что проверяет Pydantic |
|---|---|---|:---:|:---:|---|---|---|---|
| `id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID изменяемого лимита | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None |
| `contract_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID договора | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None |
| `card_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID карты | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None |
| `group_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID группы карт | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None |
| `product_type` (в JSON: <code>productType</code>) | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID типа продукта | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None |
| `product_group` (в JSON: <code>productGroup</code>) | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID группы продуктов | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None |
| `amount` | <code>LimitAmountRequest &#124; None</code> | <code>object (LimitAmountRequest) &#124; null</code> | Нет | Да | <code>None</code> | Объёмный лимит | — | Значение должно соответствовать одному из типов: LimitAmountRequest, None |
| `sum` | <code>LimitSumRequest &#124; None</code> | <code>object (LimitSumRequest) &#124; null</code> | Нет | Да | <code>None</code> | Денежный лимит | — | Значение должно соответствовать одному из типов: LimitSumRequest, None |
| `term` | <code>LimitTermRequest &#124; None</code> | <code>object (LimitTermRequest) &#124; null</code> | Нет | Да | <code>None</code> | Условия действия лимита | — | Значение должно соответствовать одному из типов: LimitTermRequest, None |
| `transactions` | <code>LimitTransactionsRequest &#124; None</code> | <code>object (LimitTransactionsRequest) &#124; null</code> | Нет | Да | <code>None</code> | Лимит количества транзакций | — | Значение должно соответствовать одному из типов: LimitTransactionsRequest, None |
| `time` | <code>LimitTimeRequest</code> | <code>object (LimitTimeRequest)</code> | Да | Нет | <code>—</code> | Период действия лимита | — | Вложенный объект рекурсивно проверяется моделью LimitTimeRequest. |

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
