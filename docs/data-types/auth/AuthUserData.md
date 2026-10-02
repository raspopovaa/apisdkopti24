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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `client_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID клиента |
| `client_status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Статус пользователя (Active, Blocked, и т.п.) |
| `org_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Наименование организации |
| `session_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID текущей сессии пользователя |
| `user_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID пользователя |
| `contracts` | <code>list[ContractInfo]</code> | <code>array[object (ContractInfo)]</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Проверяется как список; каждый элемент проверяется как ContractInfo. | Список доступных договоров |
| `role_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID роли пользователя (например, Supervisor) |
| `role_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Название роли пользователя (например, Администратор) |
| `read_only` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как bool. | Флаг режима только чтение |
| `user_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Имя пользователя |
| `user_patronymic` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Отчество пользователя |
| `user_surname` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Фамилия пользователя |
| `last_contract` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | ID последнего использованного договора |
| `access` | <code>AccessRights</code> | <code>object (AccessRights)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью AccessRights. | Права доступа (ЛК/МП/API) |
| `email` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Электронная почта |
| `phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Телефон |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`ContractInfo`](ContractInfo.md)
- [`AccessRights`](AccessRights.md)
