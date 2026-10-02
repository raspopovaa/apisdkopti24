---
description: "Поля и правила Pydantic-валидации модели AzsV2Query."
---
# `AzsV2Query`

Модель данных SDK.

!!! info "Назначение Pydantic"
    Тип модели: **request**. Правила ниже применяются, когда вызывающий код явно создаёт `AzsV2Query` или вызывает `AzsV2Query.model_validate(payload)`. Наличие request-модели не означает, что каждый метод SDK автоматически создаёт её: фактический входной контракт определяется сигнатурой соответствующего сервисного метода.

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
| `q` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: str, None |
| `id` | <code>Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)] &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | — | минимальная длина: 1; — | Значение должно соответствовать одному из типов: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)], None |
| `page` | <code>Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]] &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | <code>None</code> | — | минимум: 1; — | Значение должно соответствовать одному из типов: Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]], None |
| `on_page` | <code>Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]] &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | <code>None</code> | — | минимум: 1; — | Значение должно соответствовать одному из типов: Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]], None |
| `filter` | <code>AzsV2Filter &#124; None</code> | <code>object (AzsV2Filter) &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: AzsV2Filter, None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`AzsV2Filter`](AzsV2Filter.md)
