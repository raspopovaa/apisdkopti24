---
description: "Поля и правила Pydantic-валидации модели AzsV2Filter."
---
# `AzsV2Filter`

Модель данных SDK.

!!! info "Назначение Pydantic"
    Тип модели: **request**. Правила ниже применяются, когда вызывающий код явно создаёт `AzsV2Filter` или вызывает `AzsV2Filter.model_validate(payload)`. Наличие request-модели не означает, что каждый метод SDK автоматически создаёт её: фактический входной контракт определяется сигнатурой соответствующего сервисного метода.

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
| `services_with_card` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `services_without_card` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `own_types` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `payment_types` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `fuel` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `diesel` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `gaz` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `electric_charging_station` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `adblue` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `poi_types` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `countries` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |
| `regions` | <code>list[str] &#124; None</code> | <code>array[string] &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: list[str], None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.
