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
| `id` | `str` | `string` | Да | Нет | `—` | `—` | — | Значение преобразуется и проверяется как str. | ID торговой точки |
| `siebel_id` | `str` | `string` | Да | Нет | `—` | `—` | — | Значение преобразуется и проверяется как str. | Идентификатор Siebel |
| `status` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Статус торговой точки (257 – работает, 258 – не работает) |
| `full_name` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Полное наименование торговой точки |
| `brand` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Бренд |
| `poi_type_name` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Именование типа |
| `poi_type_code` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Код типа |
| `own_type_name` | `str` | `string` | Да | Нет | `—` | `—` | — | Значение преобразуется и проверяется как str. | Тип собственности (наименование) |
| `own_type_code` | `str` | `string` | Да | Нет | `—` | `—` | — | Значение преобразуется и проверяется как str. | Код типа собственности (по отношению к ГПН) |
| `contract_name` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Название договора |
| `contract_number` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Номер договора |
| `phone` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Телефон контактный |
| `utc_timezone` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | UTC часовой пояс АЗС (+5) |
| `time_zone` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Часовой пояс АЗС относительно Москвы |
| `open_date` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Дата открытия |
| `close_date` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Дата закрытия |
| `last_update` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Дата последнего обновления |
| `height_post` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Высота поста (в метрах) |
| `country_name` | `str \| None` | `string \| null` | Да | Да | `—` | `—` | — | Значение должно соответствовать одному из типов: str, None | Название страны |
| `country_code` | `str \| None` | `string \| null` | Да | Да | `—` | `—` | — | Значение должно соответствовать одному из типов: str, None | Код страны |
| `region_name` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Название региона |
| `region_code` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Код региона |
| `address_full` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Полный адрес торговой точки |
| `location` | `Coordinates \| None` | `object (Coordinates) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: Coordinates, None | Географические координаты |
| `latitude` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Широта |
| `longitude` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Долгота |
| `location_type` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Тип локации |
| `secession_gpn` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Отделение ГПН |
| `partner` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | ID партнёра |
| `belongs_to` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Принадлежность |
| `info` | `str \| None` | `string \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: str, None | Дополнительная информация о точке |
| `search_txt` | `str \| None` | `string \| null` | Да | Да | `—` | `—` | — | Значение должно соответствовать одному из типов: str, None | Строка для запроса поиска |
| `accept_cards` | `bool \| None` | `boolean \| null` | Да | Да | `—` | `—` | — | Значение должно соответствовать одному из типов: bool, None | Принимаются ли банковские карты |
| `adblue` | `ServiceGroup \| None` | `object (ServiceGroup) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Услуги AdBlue |
| `electric_charging_station` | `ServiceGroup \| None` | `object (ServiceGroup) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Электрозарядные станции |
| `services_with_card` | `ServiceGroup \| None` | `object (ServiceGroup) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Услуги, доступные при оплате картой |
| `services_without_card` | `ServiceGroup \| None` | `object (ServiceGroup) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: ServiceGroup, None Дополнительно: fix_empty_service_groups (before). | Услуги, доступные без карты |
| `prices` | `list[PriceItemV2] \| None` | `array[object (PriceItemV2)] \| null` | Нет | Да | `factory: list()` | `—` | — | Значение должно соответствовать одному из типов: list[PriceItemV2], None | Список товаров с указанием цен |
| `payment_type` | `list[dict[str, Any]] \| None` | `array[object] \| null` | Нет | Да | `factory: list()` | `—` | — | Значение должно соответствовать одному из типов: list[dict[str, Any]], None | Доступные способы оплаты |
| `terminals` | `list[TerminalV2] \| None` | `array[object (TerminalV2)] \| null` | Нет | Да | `factory: list()` | `—` | — | Значение должно соответствовать одному из типов: list[TerminalV2], None | Список терминалов |
| `address` | `AddressV2 \| None` | `object (AddressV2) \| null` | Нет | Да | `None` | `—` | — | Значение должно соответствовать одному из типов: AddressV2, None | Адрес торговой точки |
| `working_time` | `list[WorkingTimeV2] \| None` | `array[object (WorkingTimeV2)] \| null` | Нет | Да | `factory: list()` | `—` | — | Значение должно соответствовать одному из типов: list[WorkingTimeV2], None | Расписание работы торговой точки |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Пользовательские валидаторы

| Тип | Имя | Поля/область | Режим | Описание |
|---|---|---|---|---|
| `field_validator` | `fix_empty_service_groups` | `adblue, electric_charging_station, services_with_card, services_without_card` | `before` | Исправляет ошибку, когда API возвращает [] вместо объекта. Конвертирует [] → None, чтобы избежать ValidationError. |

## Вложенные модели

- [`Coordinates`](Coordinates.md)
- [`ServiceGroup`](ServiceGroup.md)
- [`PriceItemV2`](PriceItemV2.md)
- [`TerminalV2`](TerminalV2.md)
- [`AddressV2`](AddressV2.md)
- [`WorkingTimeV2`](WorkingTimeV2.md)
