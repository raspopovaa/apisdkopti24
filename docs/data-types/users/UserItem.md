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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID пользователя в системе |
| `login` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Логин пользователя (обычно номер телефона) |
| `first_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Имя пользователя |
| `last_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Фамилия пользователя |
| `middle_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Отчество пользователя |
| `date` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дата рождения в формате MM/DD/YYYY; может быть null |
| `position` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Должность или UUID должности |
| `role` | <code>UserRole</code> | <code>object (UserRole)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью UserRole. | Роль пользователя |
| `active` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: bool, None | Активен ли пользователь |
| `access` | <code>UserAccess</code> | <code>object (UserAccess)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью UserAccess. | Информация о доступах пользователя |
| `mobile_phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Мобильный телефон пользователя |
| `email` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Email пользователя |
| `contracts` | <code>list[UserContractItem]</code> | <code>array[object (UserContractItem)]</code> | Нет | Нет | <code>фабрика: list()</code> | <code>—</code> | — | Проверяется как список; каждый элемент проверяется как UserContractItem. | Список договоров пользователя |
| `cards` | <code>list[UserCardItem]</code> | <code>array[object (UserCardItem)]</code> | Нет | Нет | <code>фабрика: list()</code> | <code>—</code> | — | Проверяется как список; каждый элемент проверяется как UserCardItem. | Список карт пользователя |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`UserRole`](UserRole.md)
- [`UserAccess`](UserAccess.md)
- [`UserContractItem`](UserContractItem.md)
- [`UserCardItem`](UserCardItem.md)
