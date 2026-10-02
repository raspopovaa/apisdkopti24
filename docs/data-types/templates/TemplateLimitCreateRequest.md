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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `contract_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | Идентификатор договора |
| `product_type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип продукта (например, '1-276PF01') |
| `product_group` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Группа продукта (например, '1-276PF0E') |
| `sum` | <code>LimitSum &#124; None</code> | <code>object (LimitSum) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitSum, None | Суммовой лимит |
| `amount` | <code>LimitAmount &#124; None</code> | <code>object (LimitAmount) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitAmount, None | Объемный лимит |
| `time` | <code>LimitTime</code> | <code>object (LimitTime)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью LimitTime. | Период лимита |
| `term` | <code>LimitTerm &#124; None</code> | <code>object (LimitTerm) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitTerm, None | Дополнительные временные ограничения |
| `create_restriction` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: bool, None | Создать ограничитель автоматически |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `model_validator` | `require_amount_or_sum` | <code>вся модель</code> | <code>after</code> | Пользовательская проверка `require_amount_or_sum`. |

## Вложенные модели

- [`LimitSum`](LimitSum.md)
- [`LimitAmount`](LimitAmount.md)
- [`LimitTime`](LimitTime.md)
- [`LimitTerm`](LimitTerm.md)
