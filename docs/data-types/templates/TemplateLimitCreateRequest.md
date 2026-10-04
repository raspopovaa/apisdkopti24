---
description: "Поля и правила Pydantic-валидации модели TemplateLimitCreateRequest."
---
# `TemplateLimitCreateRequest`

Модель данных SDK.

!!! info "Назначение Pydantic"
    Тип модели: **request**. Правила ниже применяются, когда вызывающий код явно создаёт `TemplateLimitCreateRequest` или вызывает `TemplateLimitCreateRequest.model_validate(payload)`. Наличие request-модели не означает, что каждый метод SDK автоматически создаёт её: фактический входной контракт определяется сигнатурой соответствующего сервисного метода.

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
| `contract_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Идентификатор договора | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None |
| `product_type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип продукта (например, '1-276PF01') | — | Значение преобразуется и проверяется как str. |
| `product_group` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Группа продукта (например, '1-276PF0E') | — | Значение должно соответствовать одному из типов: str, None |
| `sum` | <code>LimitSumRequest &#124; None</code> | <code>object (LimitSumRequest) &#124; null</code> | Нет | Да | <code>None</code> | Суммовой лимит | — | Значение должно соответствовать одному из типов: LimitSumRequest, None |
| `amount` | <code>LimitAmountRequest &#124; None</code> | <code>object (LimitAmountRequest) &#124; null</code> | Нет | Да | <code>None</code> | Объемный лимит | — | Значение должно соответствовать одному из типов: LimitAmountRequest, None |
| `time` | <code>LimitTimeRequest</code> | <code>object (LimitTimeRequest)</code> | Да | Нет | <code>—</code> | Период лимита | — | Вложенный объект рекурсивно проверяется моделью LimitTimeRequest. |
| `term` | <code>LimitTermRequest &#124; None</code> | <code>object (LimitTermRequest) &#124; null</code> | Нет | Да | <code>None</code> | Дополнительные временные ограничения | — | Значение должно соответствовать одному из типов: LimitTermRequest, None |
| `create_restriction` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Создать ограничитель автоматически | — | Значение должно соответствовать одному из типов: bool, None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `model_validator` | `require_amount_or_sum` | <code>вся модель</code> | <code>after</code> | Пользовательская проверка `require_amount_or_sum`. |

## Вложенные модели

- [`LimitSumRequest`](../limits/LimitSumRequest.md)
- [`LimitAmountRequest`](../limits/LimitAmountRequest.md)
- [`LimitTimeRequest`](../limits/LimitTimeRequest.md)
- [`LimitTermRequest`](../limits/LimitTermRequest.md)
