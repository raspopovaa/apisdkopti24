---
description: "Элемент списка приглашений"
---
# `InviteItem`

Элемент списка приглашений

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID приглашения |
| `user_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | ID пользователя, если уже создан |
| `url` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Ссылка на регистрацию (уникальная, активна 3 дня) |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Технический статус приглашения (Active, Finished и т.п.) |
| `status_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Отображаемое название статуса |
| `role` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Роль пользователя ('Driver', 'Admin' и т.п.) |
| `role_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Название роли |
| `attempts` | <code>int</code> | <code>integer</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как int. | Количество отправок приглашения |
| `cards` | <code>list[InviteCard]</code> | <code>array[object (InviteCard)]</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Проверяется как список; каждый элемент проверяется как InviteCard. | Список карт, связанных с приглашением |
| `initiator` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Пользователь, создавший приглашение |
| `contracts` | <code>list[InviteContract]</code> | <code>array[object (InviteContract)]</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Проверяется как список; каждый элемент проверяется как InviteContract. | Список договоров, привязанных к приглашению |
| `mobile` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Номер телефона приглашенного |
| `email` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Email приглашенного |
| `communication_type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип отправки ('sms', 'email' и т.п.) |
| `sended_at` | <code>int &#124; None</code> | <code>integer &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: int, None | Время отправки (timestamp) |
| `expired_at` | <code>int</code> | <code>integer</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как int. | Время истечения срока действия ссылки (timestamp) |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`InviteCard`](InviteCard.md)
- [`InviteContract`](InviteContract.md)
