---
description: "Поля и правила Pydantic-валидации модели TemplateLimit."
---
# `TemplateLimit`

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Идентификатор лимита шаблона | — | Значение преобразуется и проверяется как str. |
| `template_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Идентификатор шаблона, которому принадлежит лимит | — | Значение преобразуется и проверяется как str. |
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Идентификатор договора, на который распространяется лимит | — | Значение преобразуется и проверяется как str. |
| `amount` | <code>LimitAmount &#124; None</code> | <code>object (LimitAmount) &#124; null</code> | Нет | Да | <code>None</code> | Объемный лимит (в литрах и т.д.) | — | Значение должно соответствовать одному из типов: LimitAmount, None |
| `sum` | <code>LimitSum &#124; None</code> | <code>object (LimitSum) &#124; null</code> | Нет | Да | <code>None</code> | Суммовой лимит (в рублях и т.д.) | — | Значение должно соответствовать одному из типов: LimitSum, None |
| `time` | <code>LimitTime</code> | <code>object (LimitTime)</code> | Да | Нет | <code>—</code> | Период действия лимита | — | Вложенный объект рекурсивно проверяется моделью LimitTime. |
| `term` | <code>LimitTerm</code> | <code>object (LimitTerm)</code> | Да | Нет | <code>—</code> | Дополнительные временные ограничения | — | Вложенный объект рекурсивно проверяется моделью LimitTerm. |
| `transactions` | <code>LimitTransactions</code> | <code>object (LimitTransactions)</code> | Да | Нет | <code>—</code> | Информация по транзакциям лимита | — | Вложенный объект рекурсивно проверяется моделью LimitTransactions. |
| `date` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Дата создания лимита (MM/DD/YYYY HH:MM:SS) | — | Значение преобразуется и проверяется как str. |
| `productType` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип продукта (топливо, услуга и т.д.) | — | Значение преобразуется и проверяется как str. |
| `productGroup` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Группа продукта (например, G-95) | — | Значение должно соответствовать одному из типов: str, None |
| `productTypeName` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Название типа продукта | — | Значение преобразуется и проверяется как str. |
| `productGroupName` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Название группы продукта | — | Значение должно соответствовать одному из типов: str, None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`LimitAmount`](LimitAmount.md)
- [`LimitSum`](LimitSum.md)
- [`LimitTime`](LimitTime.md)
- [`LimitTerm`](LimitTerm.md)
- [`LimitTransactions`](LimitTransactions.md)
