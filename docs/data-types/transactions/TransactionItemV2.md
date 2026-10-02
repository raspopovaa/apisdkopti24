---
description: "Позиция в транзакции (v2)."
---
# `TransactionItemV2`

Позиция в транзакции (v2).

Типы спорных полей выбраны по примерам ответов и реальным ответам
DEMO-стенда.

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
| `id` | <code>int &#124; str</code> | <code>integer &#124; string</code> | Да | Нет | <code>—</code> | ID транзакции | — | Значение должно соответствовать одному из типов: int, str |
| `timestamp` | <code>datetime</code> | <code>string</code> | Да | Нет | <code>—</code> | Местное время транзакции. Строка оканчивается на Z, но время не UTC: SDK разбирает его как UTC, поэтому не используйте tzinfo этого поля | формат: 'date-time' | Значение преобразуется и проверяется как datetime. |
| `utc_time` | <code>datetime</code> | <code>string</code> | Да | Нет | <code>—</code> | Время транзакции в UTC | формат: 'date-time' | Значение преобразуется и проверяется как datetime. |
| `card_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID карты | — | Значение преобразуется и проверяется как str. |
| `poi_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID точки продаж (АЗС) | — | Значение преобразуется и проверяется как str. |
| `terminal_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID терминала | — | Значение преобразуется и проверяется как str. |
| `type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип операции (P — покупка, R — возврат) | — | Значение преобразуется и проверяется как str. |
| `product_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID продукта | — | Значение преобразуется и проверяется как str. |
| `product_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Наименование продукта | — | Значение преобразуется и проверяется как str. |
| `product_category_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Категория продукта (например, НП) | — | Значение преобразуется и проверяется как str. |
| `currency` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Код валюты (например, RUR) | — | Значение преобразуется и проверяется как str. |
| `check_id` | <code>int &#124; str</code> | <code>integer &#124; string</code> | Да | Нет | <code>—</code> | Номер чека | — | Значение должно соответствовать одному из типов: int, str |
| `stor_transaction_id` | <code>int &#124; str &#124; None</code> | <code>integer &#124; string &#124; null</code> | Да | Да | <code>—</code> | ID сторнируемой транзакции | — | Значение должно соответствовать одному из типов: int, str, None |
| `is_storno` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | Признак сторно | — | Значение преобразуется и проверяется как bool. |
| `is_manual_correction` (в JSON также: <code>is_manual_corrention</code>) | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | Признак ручной корректировки | — | Значение преобразуется и проверяется как bool. |
| `qty` | <code>int &#124; float</code> | <code>integer &#124; number</code> | Да | Нет | <code>—</code> | Количество | — | Значение должно соответствовать одному из типов: int, float |
| `price` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | Цена за единицу | — | Значение должно соответствовать одному из типов: float, str |
| `price_no_discount` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | Цена без скидки | — | Значение должно соответствовать одному из типов: float, str |
| `sum` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | Сумма с учетом скидки | — | Значение должно соответствовать одному из типов: float, str |
| `sum_no_discount` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | Сумма без скидки | — | Значение должно соответствовать одному из типов: float, str |
| `discount` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | Размер скидки | — | Значение должно соответствовать одному из типов: float, str |
| `exchange_rate` | <code>float &#124; str</code> | <code>number &#124; string</code> | Да | Нет | <code>—</code> | Курс обмена | — | Значение должно соответствовать одному из типов: float, str |
| `card_number` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Номер карты | — | Значение преобразуется и проверяется как str. |
| `payment_type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип оплаты (например, Карта) | — | Значение преобразуется и проверяется как str. |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.
