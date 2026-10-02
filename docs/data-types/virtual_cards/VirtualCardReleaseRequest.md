---
description: "Поля и правила Pydantic-валидации модели VirtualCardReleaseRequest."
---
# `VirtualCardReleaseRequest`

Модель данных SDK.

!!! info "Назначение Pydantic"
    Тип модели: **request**. Правила ниже применяются, когда вызывающий код явно создаёт `VirtualCardReleaseRequest` или вызывает `VirtualCardReleaseRequest.model_validate(payload)`. Наличие request-модели не означает, что каждый метод SDK автоматически создаёт её: фактический входной контракт определяется сигнатурой соответствующего сервисного метода.

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
| `contract_id` | <code>Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)] &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)], None | — |
| `type` | <code>Literal[limit, wallet] &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | допустимые значения: 'limit', 'wallet'; — | Значение должно соответствовать одному из типов: Literal[limit, wallet], None | — |
| `template_id` | <code>Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)] &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)], None | — |
| `user_id` | <code>Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)] &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | минимальная длина: 1; — | Значение должно соответствовать одному из типов: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)], None | — |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `model_validator` | `exactly_one_card_source` | <code>вся модель</code> | <code>after</code> | Пользовательская проверка `exactly_one_card_source`. |
