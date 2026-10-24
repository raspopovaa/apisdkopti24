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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | ID торговой точки (АЗС) | не задано | Значение преобразуется и проверяется как str. |
| `siebelId` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | ID торговой точки в CRM | не задано | Значение преобразуется и проверяется как str. |
| `contractNumber` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Код торговой точки (договор) | не задано | Значение преобразуется и проверяется как str. |
| `contractName` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Название торговой точки | не задано | Значение преобразуется и проверяется как str. |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Статус точки (257 – работает, 258 – не работает) | не задано | Значение преобразуется и проверяется как str. |
| `countryCode` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Код страны | не задано | Значение преобразуется и проверяется как str. |
| `regionCode` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Код региона | не задано | Значение преобразуется и проверяется как str. |
| `secessionGPN` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Отделение ГПН по географии | не задано | Значение должно соответствовать одному из типов: str, None |
| `belongsTo` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Название владельца или оператора | не задано | Значение преобразуется и проверяется как str. |
| `partner` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | ID партнера | не задано | Значение преобразуется и проверяется как str. |
| `ownType` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Тип собственности (например, Own GPN, EXT, RENT) | не задано | Значение преобразуется и проверяется как str. |
| `locationType` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Тип расположения (ROAD и т.д.) | не задано | Значение должно соответствовать одному из типов: str, None |
| `brand` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Бренд торговой точки | не задано | Значение должно соответствовать одному из типов: str, None |
| `openDate` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Дата открытия точки (MM/DD/YYYY) | не задано | Значение преобразуется и проверяется как str. |
| `closeDate` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата закрытия (если закрыта) | не задано | Значение должно соответствовать одному из типов: str, None |
| `latitude` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Координата широты | не задано | Значение преобразуется и проверяется как str. |
| `longitude` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Координата долготы | не задано | Значение преобразуется и проверяется как str. |
| `type` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Тип торговой точки (АЗС, СТО и т.д.) | не задано | Значение преобразуется и проверяется как str. |
| `timeZone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Часовой пояс точки | не задано | Значение должно соответствовать одному из типов: str, None |
| `services` | <code>list[int] &#124; None</code> | <code>array[integer] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Массив ID услуг | не задано | Значение должно соответствовать одному из типов: list[int], None |
| `terminals` (в JSON также: <code>Terminals</code>) | <code>list[TerminalV1] &#124; None</code> | <code>array[object (TerminalV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Список терминалов торговой точки | не задано | Значение должно соответствовать одному из типов: list[TerminalV1], None |
| `address` (в JSON также: <code>Address</code>) | <code>AddressV1</code> | <code>object (AddressV1)</code> | Да | Нет | <code>не задано</code> | Адрес торговой точки | не задано | Вложенный объект рекурсивно проверяется моделью AddressV1. |
| `prices` (в JSON также: <code>Prices</code>) | <code>list[PriceItemV1] &#124; None</code> | <code>array[object (PriceItemV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Цены товаров на точке | не задано | Значение должно соответствовать одному из типов: list[PriceItemV1], None |
| `searchTxt` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Строка поиска | не задано | Значение преобразуется и проверяется как str. |
| `phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Контактный телефон | не задано | Значение должно соответствовать одному из типов: str, None |
| `height_post` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Высота поста (в метрах) | не задано | Значение должно соответствовать одному из типов: str, None |
| `working_time` | <code>list[WorkingTimeV1] &#124; None</code> | <code>array[object (WorkingTimeV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Режим работы | не задано | Значение должно соответствовать одному из типов: list[WorkingTimeV1], None |
| `only_virtual_card` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Принимаются ли только виртуальные карты | не задано | Значение должно соответствовать одному из типов: bool, None |
| `accept_cards` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Принимаются ли карты | не задано | Значение должно соответствовать одному из типов: bool, None |
| `hidden_on_map` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Скрыта ли точка на карте | не задано | Значение должно соответствовать одному из типов: bool, None |
| `active` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | Активна ли торговая точка | не задано | Значение должно соответствовать одному из типов: bool, None |
| `POIType` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Тип торговой точки (POI-код) | не задано | Значение должно соответствовать одному из типов: str, None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`TerminalV1`](TerminalV1.md)
- [`AddressV1`](AddressV1.md)
- [`PriceItemV1`](PriceItemV1.md)
- [`WorkingTimeV1`](WorkingTimeV1.md)
