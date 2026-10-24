---
description: "Поля и правила Pydantic-валидации модели CardDetail."
---
# `CardDetail`

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Идентификатор карты | не задано | Значение преобразуется и проверяется как str. |
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | ID договора | не задано | Значение преобразуется и проверяется как str. |
| `number` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Номер карты | не задано | Значение преобразуется и проверяется как str. |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Статус карты | не задано | Значение преобразуется и проверяется как str. |
| `can_work_offline` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>не задано</code> | Может работать офлайн | не задано | Значение преобразуется и проверяется как bool. |
| `card_auth_type` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>не задано</code> | Тип аутентификации карты | не задано | Значение должно соответствовать одному из типов: str, None |
| `comment` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Комментарий к карте | не задано | Значение должно соответствовать одному из типов: str, None |
| `date_last_usage` | <code>datetime &#124; str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата последнего использования (YYYY-MM-DD); пустую строку SDK заменяет на None | формат: 'date-time'; не задано | Значение должно соответствовать одному из типов: datetime, str, None Дополнительно: empty_str_to_none (before). |
| `date_released` | <code>datetime &#124; str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата выпуска карты (YYYY-MM-DD HH:MM:SS) | формат: 'date-time'; не задано | Значение должно соответствовать одному из типов: datetime, str, None Дополнительно: empty_str_to_none (before). |
| `servicecenter_last_usage_name` (в JSON также: <code>servicecenter_last_usage</code>) | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Название АЗС последнего использования | не задано | Значение должно соответствовать одному из типов: str, None |
| `transaction_timeout` | <code>TransactionTimeout &#124; None</code> | <code>object (TransactionTimeout) &#124; null</code> | Нет | Да | <code>None</code> | Таймаут транзакции | не задано | Значение должно соответствовать одному из типов: TransactionTimeout, None |
| `product` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Тип продукта (limit/wallet) | не задано | Значение преобразуется и проверяется как str. |
| `carrier` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Тип карты (Plastic/Virtual) | не задано | Значение преобразуется и проверяется как str. |
| `available` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Доступный лимит или баланс | не задано | Значение преобразуется и проверяется как str. |
| `currency` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Валюта | не задано | Значение преобразуется и проверяется как str. |
| `payment_of_tolls` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Признак оплаты дорожных сборов | не задано | Значение преобразуется и проверяется как str. |
| `mpc` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>не задано</code> | Признак доступности мобильного профиля карты | не задано | Значение преобразуется и проверяется как bool. |
| `pin_reset` | <code>int</code> | <code>integer</code> | Да | Нет | <code>не задано</code> | Количество доступных попыток сброса PIN | не задано | Значение преобразуется и проверяется как int. |
| `pin_counter` | <code>int</code> | <code>integer</code> | Да | Нет | <code>не задано</code> | Счётчик попыток ввода PIN | не задано | Значение преобразуется и проверяется как int. |
| `previous` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID предыдущей карты | не задано | Значение должно соответствовать одному из типов: str, None |
| `next` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID следующей карты | не задано | Значение должно соответствовать одному из типов: str, None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `field_validator` | `empty_str_to_none` | <code>date_last_usage, date_released</code> | <code>before</code> | Пользовательская проверка `empty_str_to_none`. |

## Вложенные модели

- [`TransactionTimeout`](TransactionTimeout.md)
