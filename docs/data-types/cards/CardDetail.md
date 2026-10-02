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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Идентификатор карты |
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID договора |
| `number` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Номер карты |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Статус карты |
| `can_work_offline` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как bool. | Может работать офлайн |
| `card_auth_type` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Тип аутентификации карты |
| `comment` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Комментарий к карте |
| `date_last_usage` | <code>datetime &#124; str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | формат: 'date-time'; — | Значение должно соответствовать одному из типов: datetime, str, None Дополнительно: empty_str_to_none (before). | Дата последнего использования (YYYY-MM-DD); пустую строку SDK заменяет на None |
| `date_released` | <code>datetime &#124; str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | формат: 'date-time'; — | Значение должно соответствовать одному из типов: datetime, str, None Дополнительно: empty_str_to_none (before). | Дата выпуска карты (YYYY-MM-DD HH:MM:SS) |
| `servicecenter_last_usage_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Название АЗС последнего использования |
| `transaction_timeout` | <code>TransactionTimeout &#124; None</code> | <code>object (TransactionTimeout) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: TransactionTimeout, None | Таймаут транзакции |
| `product` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип продукта (limit/wallet) |
| `carrier` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип карты (Plastic/Virtual) |
| `available` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Доступный лимит или баланс |
| `currency` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Валюта |
| `payment_of_tolls` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Признак оплаты дорожных сборов |
| `mpc` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как bool. | Признак доступности мобильного профиля карты |
| `pin_reset` | <code>int</code> | <code>integer</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как int. | Количество доступных попыток сброса PIN |
| `pin_counter` | <code>int</code> | <code>integer</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как int. | Счётчик попыток ввода PIN |
| `previous` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | ID предыдущей карты |
| `next` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | ID следующей карты |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `field_validator` | `empty_str_to_none` | <code>date_last_usage, date_released</code> | <code>before</code> | Пользовательская проверка `empty_str_to_none`. |

## Вложенные модели

- [`TransactionTimeout`](TransactionTimeout.md)
