---
description: "Поля и правила Pydantic-валидации модели AzsV1Query."
---
# `AzsV1Query`

Модель данных SDK.

!!! info "Назначение Pydantic"
    Тип модели: **request**. Правила ниже применяются, когда вызывающий код явно создаёт `AzsV1Query` или вызывает `AzsV1Query.model_validate(payload)`. Наличие request-модели не означает, что каждый метод SDK автоматически создаёт её: фактический входной контракт определяется сигнатурой соответствующего сервисного метода.

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
| `page` | <code>int</code> | <code>integer</code> | Нет | Нет | <code>1</code> | — | минимум: 1 | Значение преобразуется и проверяется как int. |
| `onpage` | <code>int</code> | <code>integer</code> | Нет | Нет | <code>10</code> | — | минимум: 0 | Значение преобразуется и проверяется как int. |
| `filter` | <code>AzsV1Filter &#124; None</code> | <code>object (AzsV1Filter) &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: AzsV1Filter, None |
| `q` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | — | — | Значение должно соответствовать одному из типов: str, None |
| `id` | <code>Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)] &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | — | минимальная длина: 1; — | Значение должно соответствовать одному из типов: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)], None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`AzsV1Filter`](AzsV1Filter.md)
