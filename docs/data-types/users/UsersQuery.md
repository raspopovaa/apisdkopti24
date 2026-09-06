# `UsersQuery`

Модель данных SDK.

!!! info "Назначение Pydantic"
    Тип модели: **request**. Правила ниже применяются, когда вызывающий код явно создаёт `UsersQuery` или вызывает `UsersQuery.model_validate(payload)`. Наличие request-модели не означает, что каждый метод SDK автоматически создаёт её: фактический входной контракт определяется сигнатурой соответствующего сервисного метода.

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
| `sort` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: str, None | — |
| `filter` | `UserFilter \| None` | `object (UserFilter) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: UserFilter, None | — |
| `q` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | — |
| `page` | `Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]] \| None` | `integer \| null` | Нет | Да | `None` | `—` | минимум: 1; — | Значение должно соответствовать одному из типов: Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]], None | — |
| `on_page` | `Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]] \| None` | `integer \| null` | Нет | Да | `None` | `—` | минимум: 1; — | Значение должно соответствовать одному из типов: Annotated[int, annotation=NoneType required=True metadata=[Ge(ge=1)]], None | — |
| `contract_id` | `Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)] \| None` | `string \| null` | Нет | Да | `None` | `—` | минимальная длина: 1; — | Значение должно соответствовать одному из типов: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)], None | — |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`UserFilter`](UserFilter.md)
