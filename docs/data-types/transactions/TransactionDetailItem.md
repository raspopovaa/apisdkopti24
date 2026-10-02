---
description: "Поля и правила Pydantic-валидации модели TransactionDetailItem."
---
# `TransactionDetailItem`

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
| `id` | <code>int &#124; str</code> | <code>integer &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: int, str | ID транзакции |
| `timestamp` | <code>datetime</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | формат: 'date-time' | Значение преобразуется и проверяется как datetime. | Местное время транзакции. Строка оканчивается на Z, но время не UTC: SDK разбирает его как UTC, поэтому не используйте tzinfo этого поля |
| `utc_time` | <code>datetime</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | формат: 'date-time' | Значение преобразуется и проверяется как datetime. | Время транзакции в UTC |
| `card_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID карты |
| `poi_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID точки продаж (АЗС) |
| `terminal_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID терминала |
| `type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип операции (P — покупка, R — возврат) |
| `product_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID продукта |
| `product_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Наименование продукта |
| `product_category_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Категория продукта (например, НП) |
| `currency` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Код валюты (например, RUR) |
| `check_id` | <code>int &#124; str</code> | <code>integer &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: int, str | Номер чека |
| `stor_transaction_id` | <code>int &#124; str &#124; None</code> | <code>integer &#124; string &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: int, str, None | ID сторнируемой транзакции |
| `is_storno` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как bool. | Признак сторно |
| `is_manual_correction` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как bool. | Признак ручной корректировки |
| `qty` | <code>int &#124; float</code> | <code>integer &#124; number</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: int, float | Количество |
| `price` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: float, str | Цена за единицу |
| `price_no_discount` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: float, str | Цена без скидки |
| `sum` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: float, str | Сумма с учетом скидки |
| `sum_no_discount` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: float, str | Сумма без скидки |
| `discount` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: float, str | Размер скидки |
| `exchange_rate` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: float, str | Курс обмена |
| `card_number` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Номер карты |
| `payment_type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип оплаты (например, Карта) |
| `date` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дата транзакции |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.
