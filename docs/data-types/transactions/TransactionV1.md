---
description: "Транзакция для версии v1."
---
# `TransactionV1`

Транзакция для версии v1.

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID транзакции |
| `time` | <code>datetime</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | формат: 'date-time' | Значение преобразуется и проверяется как datetime. | Дата и время транзакции |
| `host_date` | <code>datetime</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | формат: 'date-time' | Значение преобразуется и проверяется как datetime. | Дата и время на хосте |
| `currency` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Код валюты (например, 810) |
| `card_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID карты |
| `service_center` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | ID сервисного центра (АЗС) |
| `card_number` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Номер карты |
| `base_cost` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Базовая стоимость транзакции |
| `cost` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Фактическая стоимость с учётом скидок |
| `discount` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Размер скидки |
| `discount_cost` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Стоимость после применения скидки |
| `incoming` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как bool. | Признак входящей транзакции |
| `request` | <code>RequestInfo</code> | <code>object (RequestInfo)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью RequestInfo. | Информация о типе операции |
| `transaction_items` | <code>list[TransactionItem] &#124; None</code> | <code>array[object (TransactionItem)] &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[TransactionItem], None | Список товаров в транзакции |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`RequestInfo`](RequestInfo.md)
- [`TransactionItem`](TransactionItem.md)
