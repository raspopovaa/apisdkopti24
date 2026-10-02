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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID торговой точки |
| `siebel_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Идентификатор Siebel |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Статус торговой точки (257 – работает, 258 – не работает) |
| `full_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Полное наименование торговой точки |
| `brand` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Бренд |
| `poi_type_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Именование типа |
| `poi_type_code` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Код типа |
| `own_type_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип собственности (наименование) |
| `own_type_code` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Код типа собственности (по отношению к ГПН) |
| `contract_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Название договора |
| `contract_number` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Номер договора |
| `phone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Телефон контактный |
| `utc_timezone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | UTC часовой пояс АЗС (+5) |
| `time_zone` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Часовой пояс АЗС относительно Москвы |
| `open_date` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дата открытия (MM/DD/YYYY) |
| `close_date` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дата закрытия (MM/DD/YYYY) |
| `last_update` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дата последнего обновления |
| `height_post` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Высота поста (в метрах) |
| `country_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Название страны |
| `country_code` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Код страны |
| `region_name` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Название региона |
| `region_code` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Код региона |
| `address_full` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Полный адрес торговой точки |
| `location` | <code>Coordinates &#124; None</code> | <code>object (Coordinates) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: Coordinates, None | Географические координаты |
| `latitude` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Широта |
| `longitude` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Долгота |
| `location_type` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Тип локации |
| `secession_gpn` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Отделение ГПН |
| `partner` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | ID партнёра |
| `belongs_to` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Принадлежность |
| `info` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дополнительная информация о точке |
| `search_txt` | <code>str &#124; None</code> | <code>string &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Строка для запроса поиска |
| `accept_cards` | <code>bool &#124; None</code> | <code>boolean &#124; null</code> | Да | Да | <code>—</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: bool, None | Принимаются ли банковские карты |
| `adblue` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Услуги AdBlue |
| `electric_charging_station` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Электрозарядные станции |
| `services_with_card` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Услуги, доступные при оплате картой |
| `services_without_card` | <code>ServiceGroup &#124; None</code> | <code>object (ServiceGroup) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Услуги, доступные без карты |
| `prices` | <code>list[PriceItemV2] &#124; None</code> | <code>array[object (PriceItemV2)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[PriceItemV2], None | Список товаров с указанием цен |
| `payment_type` | <code>list[PaymentType] &#124; None</code> | <code>array[object (PaymentType)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[PaymentType], None | Доступные способы оплаты |
| `terminals` | <code>list[TerminalV2] &#124; None</code> | <code>array[object (TerminalV2)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[TerminalV2], None | Список терминалов |
| `address` | <code>AddressV2 &#124; None</code> | <code>object (AddressV2) &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: AddressV2, None | Адрес торговой точки |
| `working_time` | <code>list[WorkingTimeV2] &#124; None</code> | <code>array[object (WorkingTimeV2)] &#124; null</code> | Нет | Да | <code>фабрика: list()</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: list[WorkingTimeV2], None | Расписание работы торговой точки |

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
