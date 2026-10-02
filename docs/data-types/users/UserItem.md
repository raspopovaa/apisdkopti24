---
description: "Поля и правила Pydantic-валидации модели UserItem."
---
# `UserItem`

Модель данных SDK.

!!! info "Назначение Pydantic"
    Тип модели: **response/data**. Ответ API проверяется этой моделью напрямую или рекурсивно как часть родительской response-модели. При несовпадении типов или отсутствии обязательного поля Pydantic формирует `ValidationError`.

## Поведение модели

| Настройка | Значение | Фактическое поведение |
|---|---|---|
| Дополнительные поля (`extra`) | `allow` | Дополнительные поля разрешены и сохраняются в модели. |
| Проверка default | `True` | Значения по умолчанию также проходят валидацию. |
| Заполнение по имени поля | `True` | Разрешено использовать имя поля наряду с alias. |
| Число → строка | `False` | Для строковых полей числовые значения могут быть преобразованы в строку. |

## Поля и проверки

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Описание | Ограничения схемы | Что проверяет Pydantic |
|---|---|---|:---:|:---:|---|---|---|---|
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID пользователя в системе | — | Значение преобразуется и проверяется как str. |
| `login` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Логин пользователя (обычно номер телефона) | — | Значение преобразуется и проверяется как str. |
| `first_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Имя пользователя | — | Значение преобразуется и проверяется как str. |
| `last_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Фамилия пользователя | — | Значение преобразуется и проверяется как str. |
| `middle_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Отчество пользователя | — | Значение преобразуется и проверяется как str. |
| `date` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>—</code> | Дата рождения в формате MM/DD/YYYY; может быть null | — | Значение должно соответствовать одному из типов: str, None |
| `position` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Должность или UUID должности | — | Значение преобразуется и проверяется как str. |
| `role` | <code>UserRole</code> | <code>object (UserRole)</code> | Да | Нет | <code>—</code> | Роль пользователя | — | Вложенный объект рекурсивно проверяется моделью UserRole. |
| `active` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Активен ли пользователь | — | Значение должно соответствовать одному из типов: bool, None |
| `access` | <code>UserAccess</code> | <code>object (UserAccess)</code> | Да | Нет | <code>—</code> | Информация о доступах пользователя | — | Вложенный объект рекурсивно проверяется моделью UserAccess. |
| `mobile_phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Мобильный телефон пользователя | — | Значение должно соответствовать одному из типов: str, None |
| `email` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Email пользователя | — | Значение должно соответствовать одному из типов: str, None |
| `contracts` | <code>list[UserContractItem]</code> | <code>array[object (UserContractItem)]</code> | Нет | Нет | <code>фабрика: list()</code> | Список договоров пользователя | — | Проверяется как список; каждый элемент проверяется как UserContractItem. |
| `cards` | <code>list[UserCardItem]</code> | <code>array[object (UserCardItem)]</code> | Нет | Нет | <code>фабрика: list()</code> | Список карт пользователя | — | Проверяется как список; каждый элемент проверяется как UserCardItem. |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`UserRole`](UserRole.md)
- [`UserAccess`](UserAccess.md)
- [`UserContractItem`](UserContractItem.md)
- [`UserCardItem`](UserCardItem.md)
