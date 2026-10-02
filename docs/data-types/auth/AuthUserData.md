---
description: "Поля и правила Pydantic-валидации модели AuthUserData."
---
# `AuthUserData`

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
| `client_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID клиента | — | Значение преобразуется и проверяется как str. |
| `client_status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Статус пользователя (Active, Blocked, и т.п.) | — | Значение преобразуется и проверяется как str. |
| `org_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Наименование организации | — | Значение преобразуется и проверяется как str. |
| `session_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID текущей сессии пользователя | — | Значение преобразуется и проверяется как str. |
| `user_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID пользователя | — | Значение преобразуется и проверяется как str. |
| `contracts` | <code>list[ContractInfo]</code> | <code>array[object (ContractInfo)]</code> | Да | Нет | <code>—</code> | Список доступных договоров | — | Проверяется как список; каждый элемент проверяется как ContractInfo. |
| `role_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID роли пользователя (например, Supervisor) | — | Значение преобразуется и проверяется как str. |
| `role_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Название роли пользователя (например, Администратор) | — | Значение преобразуется и проверяется как str. |
| `read_only` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | Флаг режима только чтение | — | Значение преобразуется и проверяется как bool. |
| `user_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Имя пользователя | — | Значение должно соответствовать одному из типов: str, None |
| `user_patronymic` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Отчество пользователя | — | Значение должно соответствовать одному из типов: str, None |
| `user_surname` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Фамилия пользователя | — | Значение должно соответствовать одному из типов: str, None |
| `last_contract` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID последнего использованного договора | — | Значение должно соответствовать одному из типов: str, None |
| `access` | <code>AccessRights</code> | <code>object (AccessRights)</code> | Да | Нет | <code>—</code> | Права доступа (ЛК/МП/API) | — | Вложенный объект рекурсивно проверяется моделью AccessRights. |
| `email` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Электронная почта | — | Значение преобразуется и проверяется как str. |
| `phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Телефон | — | Значение должно соответствовать одному из типов: str, None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`ContractInfo`](ContractInfo.md)
- [`AccessRights`](AccessRights.md)
