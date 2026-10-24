---
description: "Информация о торговой точке (АЗС)"
---
# `AzsItemV2`

Информация о торговой точке (АЗС)

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
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | ID торговой точки | не задано | Значение преобразуется и проверяется как str. |
| `siebel_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Идентификатор Siebel | не задано | Значение преобразуется и проверяется как str. |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Статус торговой точки (257 – работает, 258 – не работает) | не задано | Значение преобразуется и проверяется как str. |
| `full_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Полное наименование торговой точки | не задано | Значение должно соответствовать одному из типов: str, None |
| `brand` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Бренд | не задано | Значение должно соответствовать одному из типов: str, None |
| `poi_type_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Именование типа | не задано | Значение должно соответствовать одному из типов: str, None |
| `poi_type_code` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Код типа | не задано | Значение должно соответствовать одному из типов: str, None |
| `own_type_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Тип собственности (наименование) | не задано | Значение преобразуется и проверяется как str. |
| `own_type_code` | <code>str</code> | <code>string</code> | Да | Нет | <code>не задано</code> | Код типа собственности (по отношению к ГПН) | не задано | Значение преобразуется и проверяется как str. |
| `contract_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Название договора | не задано | Значение должно соответствовать одному из типов: str, None |
| `contract_number` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Номер договора | не задано | Значение должно соответствовать одному из типов: str, None |
| `phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Телефон контактный | не задано | Значение должно соответствовать одному из типов: str, None |
| `utc_timezone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>не задано</code> | UTC часовой пояс АЗС (+5) | не задано | Значение должно соответствовать одному из типов: str, None |
| `time_zone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Часовой пояс АЗС относительно Москвы | не задано | Значение должно соответствовать одному из типов: str, None |
| `open_date` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата открытия (MM/DD/YYYY) | не задано | Значение должно соответствовать одному из типов: str, None |
| `close_date` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата закрытия (MM/DD/YYYY) | не задано | Значение должно соответствовать одному из типов: str, None |
| `last_update` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дата последнего обновления | не задано | Значение должно соответствовать одному из типов: str, None |
| `height_post` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Высота поста (в метрах) | не задано | Значение должно соответствовать одному из типов: str, None |
| `country_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>не задано</code> | Название страны | не задано | Значение должно соответствовать одному из типов: str, None |
| `country_code` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>не задано</code> | Код страны | не задано | Значение должно соответствовать одному из типов: str, None |
| `region_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Название региона | не задано | Значение должно соответствовать одному из типов: str, None |
| `region_code` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Код региона | не задано | Значение должно соответствовать одному из типов: str, None |
| `address_full` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Полный адрес торговой точки | не задано | Значение должно соответствовать одному из типов: str, None |
| `location` | <code>Coordinates &#124; None</code> | <code>object (Coordinates) &#124; null</code> | Нет | Да | <code>None</code> | Географические координаты | не задано | Значение должно соответствовать одному из типов: Coordinates, None |
| `latitude` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Широта | не задано | Значение должно соответствовать одному из типов: str, None |
| `longitude` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Долгота | не задано | Значение должно соответствовать одному из типов: str, None |
| `location_type` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Тип локации | не задано | Значение должно соответствовать одному из типов: str, None |
| `secession_gpn` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Отделение ГПН | не задано | Значение должно соответствовать одному из типов: str, None |
| `partner` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID партнёра | не задано | Значение должно соответствовать одному из типов: str, None |
| `belongs_to` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Принадлежность | не задано | Значение должно соответствовать одному из типов: str, None |
| `info` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дополнительная информация о точке | не задано | Значение должно соответствовать одному из типов: str, None |
| `search_txt` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>не задано</code> | Строка для запроса поиска | не задано | Значение должно соответствовать одному из типов: str, None |
| `accept_cards` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Да | Да | <code>не задано</code> | Принимаются ли банковские карты | не задано | Значение должно соответствовать одному из типов: bool, None |
| `adblue` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | Услуги AdBlue | не задано | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). |
| `electric_charging_station` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | Электрозарядные станции | не задано | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). |
| `services_with_card` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | Услуги, доступные при оплате картой | не задано | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). |
| `services_without_card` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | Услуги, доступные без карты | не задано | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). |
| `prices` | <code>list[PriceItemV2] &#124; None</code> | <code>array[object (PriceItemV2)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Список товаров с указанием цен | не задано | Значение должно соответствовать одному из типов: list[PriceItemV2], None |
| `payment_type` | <code>list[PaymentType] &#124; None</code> | <code>array[object (PaymentType)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Доступные способы оплаты | не задано | Значение должно соответствовать одному из типов: list[PaymentType], None |
| `terminals` | <code>list[TerminalV2] &#124; None</code> | <code>array[object (TerminalV2)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Список терминалов | не задано | Значение должно соответствовать одному из типов: list[TerminalV2], None |
| `address` | <code>AddressV2 &#124; None</code> | <code>object (AddressV2) &#124; null</code> | Нет | Да | <code>None</code> | Адрес торговой точки | не задано | Значение должно соответствовать одному из типов: AddressV2, None |
| `working_time` | <code>list[WorkingTimeV2] &#124; None</code> | <code>array[object (WorkingTimeV2)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | Расписание работы торговой точки | не задано | Значение должно соответствовать одному из типов: list[WorkingTimeV2], None |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `field_validator` | `fix_empty_service_groups` | <code>adblue, electric_charging_station, services_with_card, services_without_card</code> | <code>before</code> | Исправляет ошибку, когда API возвращает [] вместо объекта. Конвертирует [] → None, чтобы избежать ValidationError. |

## Вложенные модели

- [`Coordinates`](Coordinates.md)
- [`ServiceGroup`](ServiceGroup.md)
- [`PriceItemV2`](PriceItemV2.md)
- [`PaymentType`](PaymentType.md)
- [`TerminalV2`](TerminalV2.md)
- [`AddressV2`](AddressV2.md)
- [`WorkingTimeV2`](WorkingTimeV2.md)
