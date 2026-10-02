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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID торговой точки (АЗС) |
| `siebelId` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID торговой точки в CRM |
| `contractNumber` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Код торговой точки (договор) |
| `contractName` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Название торговой точки |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Статус точки (257 – работает, 258 – не работает) |
| `countryCode` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Код страны |
| `regionCode` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Код региона |
| `secessionGPN` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Отделение ГПН по географии |
| `belongsTo` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Название владельца или оператора |
| `partner` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID партнера |
| `ownType` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип собственности (например, Own GPN, EXT, RENT) |
| `locationType` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Тип расположения (ROAD и т.д.) |
| `brand` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Бренд торговой точки |
| `openDate` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Дата открытия точки (MM/DD/YYYY) |
| `closeDate` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дата закрытия (если закрыта) |
| `latitude` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Координата широты |
| `longitude` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Координата долготы |
| `type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип торговой точки (АЗС, СТО и т.д.) |
| `timeZone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Часовой пояс точки |
| `services` | <code>list[int] &#124; None</code> | <code>array[integer] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[int], None | Массив ID услуг |
| `terminals` | <code>list[TerminalV1] &#124; None</code> | <code>array[object (TerminalV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[TerminalV1], None | Список терминалов торговой точки |
| `address` | <code>AddressV1</code> | <code>object (AddressV1)</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Вложенный объект рекурсивно проверяется моделью AddressV1. | Адрес торговой точки |
| `prices` | <code>list[PriceItemV1] &#124; None</code> | <code>array[object (PriceItemV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[PriceItemV1], None | Цены товаров на точке |
| `searchTxt` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Строка поиска |
| `phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Контактный телефон |
| `height_post` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Высота поста (в метрах) |
| `working_time` | <code>list[WorkingTimeV1] &#124; None</code> | <code>array[object (WorkingTimeV1)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[WorkingTimeV1], None | Режим работы |
| `only_virtual_card` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: bool, None | Принимаются ли только виртуальные карты |
| `accept_cards` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: bool, None | Принимаются ли карты |
| `hidden_on_map` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: bool, None | Скрыта ли точка на карте |
| `active` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: bool, None | Активна ли торговая точка |
| `POIType` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Тип торговой точки (POI-код) |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`TerminalV1`](TerminalV1.md)
- [`AddressV1`](AddressV1.md)
- [`PriceItemV1`](PriceItemV1.md)
- [`WorkingTimeV1`](WorkingTimeV1.md)
