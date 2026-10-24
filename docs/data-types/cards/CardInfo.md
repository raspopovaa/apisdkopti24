---
description: "Поля и правила Pydantic-валидации модели CardInfo."
---
# `CardInfo`

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Уникальный идентификатор карты | не задано | Значение преобразуется и проверяется как str. |
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Идентификатор договора | не задано | Значение преобразуется и проверяется как str. |
| `number` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Номер топливной карты | не задано | Значение преобразуется и проверяется как str. |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Статус карты (например, Active, Locked(Client)) | не задано | Значение преобразуется и проверяется как str. |
| `can_work_offline` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Может ли карта работать офлайн | не задано | Значение должно соответствовать одному из типов: bool, None |
| `card_auth_type` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Тип авторизации карты (например, PIN) | не задано | Значение должно соответствовать одному из типов: str, None |
| `comment` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Комментарий к карте | не задано | Значение должно соответствовать одному из типов: str, None |
| `date_expired` | <code>datetime &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата истечения срока действия карты | формат: 'date-time'; не задано | Значение должно соответствовать одному из типов: datetime, None |
| `date_last_usage` | <code>datetime &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата последнего использования карты | формат: 'date-time'; не задано | Значение должно соответствовать одному из типов: datetime, None |
| `date_released` | <code>datetime &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата выпуска карты | формат: 'date-time'; не задано | Значение должно соответствовать одному из типов: datetime, None |
| `servicecenter_last_usage_name` (в JSON также: <code>servicecenter_last_usage</code>) | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Название последней АЗС, где использовалась карта | не задано | Значение должно соответствовать одному из типов: str, None |
| `transaction_last_detail` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Информация о последней транзакции | не задано | Значение должно соответствовать одному из типов: str, None |
| `transaction_timeout` | <code>TransactionTimeout &#124; None</code> | <code>object (TransactionTimeout) &#124; null</code> | Нет | Да | <code>None</code> | Таймаут последней транзакции | не задано | Значение должно соответствовать одному из типов: TransactionTimeout, None |
| `product` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Тип продукта (limit/wallet) | не задано | Значение преобразуется и проверяется как str. |
| `payment_of_tolls` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Оплата платных дорог ('Y' или 'N') | не задано | Значение преобразуется и проверяется как str. |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`TransactionTimeout`](TransactionTimeout.md)
