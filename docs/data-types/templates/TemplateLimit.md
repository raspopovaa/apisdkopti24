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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Идентификатор лимита шаблона |
| `template_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Идентификатор шаблона, которому принадлежит лимит |
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Идентификатор договора, на который распространяется лимит |
| `amount` | <code>LimitAmount &#124; None</code> | <code>object (LimitAmount) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitAmount, None | Объемный лимит (в литрах и т.д.) |
| `sum` | <code>LimitSum &#124; None</code> | <code>object (LimitSum) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: LimitSum, None | Суммовой лимит (в рублях и т.д.) |
| `time` | <code>LimitTime</code> | <code>object (LimitTime)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью LimitTime. | Период действия лимита |
| `term` | <code>LimitTerm</code> | <code>object (LimitTerm)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью LimitTerm. | Дополнительные временные ограничения |
| `transactions` | <code>LimitTransactions</code> | <code>object (LimitTransactions)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью LimitTransactions. | Информация по транзакциям лимита |
| `date` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Дата создания лимита (MM/DD/YYYY HH:MM:SS) |
| `productType` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип продукта (топливо, услуга и т.д.) |
| `productGroup` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Группа продукта (например, G-95) |
| `productTypeName` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Название типа продукта |
| `productGroupName` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Название группы продукта |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`LimitAmount`](LimitAmount.md)
- [`LimitSum`](LimitSum.md)
- [`LimitTime`](LimitTime.md)
- [`LimitTerm`](LimitTerm.md)
- [`LimitTransactions`](LimitTransactions.md)
