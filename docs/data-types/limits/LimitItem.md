---
description: "Продуктовый лимит (карта, группа или договор)."
---
# `LimitItem`

Продуктовый лимит (карта, группа или договор).

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID лимита | — | Значение преобразуется и проверяется как str. |
| `card_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID карты, если лимит задан для карты | — | Значение должно соответствовать одному из типов: str, None |
| `group_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID группы карт, если лимит задан для группы | — | Значение должно соответствовать одному из типов: str, None |
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID договора, к которому относится лимит | — | Значение преобразуется и проверяется как str. |
| `productGroup` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID группы продуктов | — | Значение должно соответствовать одному из типов: str, None |
| `productType` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID типа продукта | — | Значение преобразуется и проверяется как str. |
| `amount` | <code>LimitAmount &#124; None</code> | <code>object (LimitAmount) &#124; null</code> | Нет | Да | <code>None</code> | Ограничение по объёму (литры и т.д.) | — | Значение должно соответствовать одному из типов: LimitAmount, None |
| `sum` | <code>LimitSum &#124; None</code> | <code>object (LimitSum) &#124; null</code> | Нет | Да | <code>None</code> | Ограничение по сумме в валюте договора | — | Значение должно соответствовать одному из типов: LimitSum, None |
| `term` | <code>LimitTerm &#124; None</code> | <code>object (LimitTerm) &#124; null</code> | Нет | Да | <code>None</code> | Периодичность и временные ограничения | — | Значение должно соответствовать одному из типов: LimitTerm, None |
| `transactions` | <code>LimitTransactions &#124; None</code> | <code>object (LimitTransactions) &#124; null</code> | Нет | Да | <code>None</code> | Ограничения по количеству транзакций | — | Значение должно соответствовать одному из типов: LimitTransactions, None |
| `time` | <code>LimitTime</code> | <code>object (LimitTime)</code> | Да | Нет | <code>—</code> | Периодичность сброса лимита | — | Вложенный объект рекурсивно проверяется моделью LimitTime. |
| `date` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Дата создания лимита (MM/DD/YYYY HH:MM:SS) | — | Значение преобразуется и проверяется как str. |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`LimitAmount`](LimitAmount.md)
- [`LimitSum`](LimitSum.md)
- [`LimitTerm`](LimitTerm.md)
- [`LimitTransactions`](LimitTransactions.md)
- [`LimitTime`](LimitTime.md)
