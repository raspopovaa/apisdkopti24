---
description: "Информация о торговой точке (v1)"
---
# `AzsItemV1`

Информация о торговой точке (v1)

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID торговой точки (АЗС) | — | Значение преобразуется и проверяется как str. |
| `siebelId` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID торговой точки в CRM | — | Значение преобразуется и проверяется как str. |
| `contractNumber` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Код торговой точки (договор) | — | Значение преобразуется и проверяется как str. |
| `contractName` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Название торговой точки | — | Значение преобразуется и проверяется как str. |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Статус точки (257 – работает, 258 – не работает) | — | Значение преобразуется и проверяется как str. |
| `countryCode` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Код страны | — | Значение преобразуется и проверяется как str. |
| `regionCode` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Код региона | — | Значение преобразуется и проверяется как str. |
| `secessionGPN` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Отделение ГПН по географии | — | Значение должно соответствовать одному из типов: str, None |
| `belongsTo` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Название владельца или оператора | — | Значение преобразуется и проверяется как str. |
| `partner` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID партнера | — | Значение преобразуется и проверяется как str. |
| `ownType` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип собственности (например, Own GPN, EXT, RENT) | — | Значение преобразуется и проверяется как str. |
| `locationType` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Тип расположения (ROAD и т.д.) | — | Значение должно соответствовать одному из типов: str, None |
| `brand` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Бренд торговой точки | — | Значение должно соответствовать одному из типов: str, None |
| `openDate` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Дата открытия точки (MM/DD/YYYY) | — | Значение преобразуется и проверяется как str. |
| `closeDate` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата закрытия (если закрыта) | — | Значение должно соответствовать одному из типов: str, None |
| `latitude` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Координата широты | — | Значение преобразуется и проверяется как str. |
| `longitude` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Координата долготы | — | Значение преобразуется и проверяется как str. |
| `type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип торговой точки (АЗС, СТО и т.д.) | — | Значение преобразуется и проверяется как str. |
| `timeZone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Часовой пояс точки | — | Значение должно соответствовать одному из типов: str, None |
| `services` | <code>list[int] &#124; None</code> | <code>array[integer] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Массив ID услуг | — | Значение должно соответствовать одному из типов: list[int], None |
| `terminals` (в JSON также: <code>Terminals</code>) | <code>list[TerminalV1] &#124; None</code> | <code>array[object (TerminalV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Список терминалов торговой точки | — | Значение должно соответствовать одному из типов: list[TerminalV1], None |
| `address` (в JSON также: <code>Address</code>) | <code>AddressV1</code> | <code>object (AddressV1)</code> | Да | Нет | <code>—</code> | Адрес торговой точки | — | Вложенный объект рекурсивно проверяется моделью AddressV1. |
| `prices` (в JSON также: <code>Prices</code>) | <code>list[PriceItemV1] &#124; None</code> | <code>array[object (PriceItemV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Цены товаров на точке | — | Значение должно соответствовать одному из типов: list[PriceItemV1], None |
| `searchTxt` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Строка поиска | — | Значение преобразуется и проверяется как str. |
| `phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Контактный телефон | — | Значение должно соответствовать одному из типов: str, None |
| `height_post` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Высота поста (в метрах) | — | Значение должно соответствовать одному из типов: str, None |
| `working_time` | <code>list[WorkingTimeV1] &#124; None</code> | <code>array[object (WorkingTimeV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Режим работы | — | Значение должно соответствовать одному из типов: list[WorkingTimeV1], None |
| `only_virtual_card` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Принимаются ли только виртуальные карты | — | Значение должно соответствовать одному из типов: bool, None |
| `accept_cards` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Принимаются ли карты | — | Значение должно соответствовать одному из типов: bool, None |
| `hidden_on_map` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Скрыта ли точка на карте | — | Значение должно соответствовать одному из типов: bool, None |
| `active` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Активна ли торговая точка | — | Значение должно соответствовать одному из типов: bool, None |
| `POIType` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Тип торговой точки (POI-код) | — | Значение должно соответствовать одному из типов: str, None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`TerminalV1`](TerminalV1.md)
- [`AddressV1`](AddressV1.md)
- [`PriceItemV1`](PriceItemV1.md)
- [`WorkingTimeV1`](WorkingTimeV1.md)
