from typing import Any

from ..modeling import APIEnvelope, BaseModel, Field, field_validator

# ==========================================================
# 🔹 Универсальные модели для общих справочников
# ==========================================================


class DictionaryItem(BaseModel):
    """Элемент справочника (универсальная модель)"""

    id: str = Field(..., description="Уникальный идентификатор элемента справочника")
    code: str | None = Field(None, description="Код элемента (например, код валюты)")
    value: str | None = Field(
        None, description="Значение элемента (используется в старых справочниках)"
    )
    name: str | None = Field(
        None, description="Название элемента (используется в новых справочниках)"
    )
    deleted: int | None = Field(0, description="Признак удаления элемента (0 — активен)")
    last_update: str | None = Field(None, description="Дата последнего обновления записи")


class DictionaryData(BaseModel):
    """Основные данные справочника"""

    total_count: int | None = Field(None, description="Количество элементов в справочнике")
    result: list[DictionaryItem] | None = Field(
        default_factory=list, description="Список элементов справочника"
    )


class DictionaryResponse(APIEnvelope[DictionaryData | None]):
    """Ответ метода GET /vip/v1/getDictionary"""


# ==========================================================
# 🔹 Фильтры торговых точек (GET /vip/v2/azs/filters)
# ==========================================================


class AzsFilterValue(BaseModel):
    """Отдельное значение фильтра"""

    name: str | None = Field(default=None, description="Название значения фильтра")
    code: str | None = Field(default=None, description="Код значения фильтра")


class AzsFilterItem(BaseModel):
    """Описание фильтра торговых точек"""

    filter: str | None = Field(
        default=None,
        description="Ключ фильтра (например: services_with_card, countries и т.д.)",
    )
    name: str | None = Field(default=None, description="Название фильтра (человекочитаемое)")
    values: dict[str, AzsFilterValue] | None = Field(
        default_factory=dict, description="Список значений для данного фильтра"
    )


class AzsFiltersResponse(APIEnvelope[list[AzsFilterItem] | None]):
    """Ответ метода /azs/filters"""


# ==========================================================
# 🔹 Модели для списка торговых точек (GET /vip/v1/AZS)
# ==========================================================


class PriceItemV1(BaseModel):
    """Цена товара на торговой точке"""

    ID: str | None = Field(None, description="Идентификатор записи цены")
    GasStationID: str | None = Field(None, description="ID торговой точки (АЗС)")
    GoodsCode: str | None = Field(None, description="Код товара (см. справочник GoodsCode)")
    Price: str | None = Field(None, description="Цена товара")
    Currency: str | None = Field(None, description="Валюта (код и наименование через ';')")
    DateTo: str | None = Field(None, description="Дата окончания действия цены")
    DateFrom: str | None = Field(None, description="Дата начала действия цены")


class TerminalV1(BaseModel):
    """Терминал торговой точки"""

    id: str | None = Field(None, description="Идентификатор терминала")
    active: bool | None = Field(
        None,
        description="Статус активности терминала (True — включен, False — выключен)",
    )
    name: str | None = Field(None, description="Наименование терминала")
    status: str | None = Field(None, description="Статус терминала")
    type: str | None = Field(None, description="Тип терминала")
    connectionType: str | None = Field(None, description="Тип подключения терминала")
    number: str | None = Field(None, description="Номер терминала")


class AddressV1(BaseModel):
    """Адрес торговой точки"""

    track_id: str | None = Field(None, description="Номер трассы, если применимо")
    kmRoad: str | None = Field(None, description="Километр трассы")
    roadSide: str | None = Field(None, description="Сторона дороги")
    city: str | None = Field(None, description="Город")
    street: str | None = Field(None, description="Улица")
    house: str | None = Field(None, description="Дом")
    building: str | None = Field(None, description="Строение")
    phone: str | None = Field(None, description="Телефон торговой точки")
    fax: str | None = Field(None, description="Факс")


class WorkingTimeV1(BaseModel):
    """Рабочее время торговой точки"""

    Weekday: str | None = Field(None, description="День недели или режим работы")
    StartWorkTime: str | None = Field(None, description="Время открытия")
    FinishWorkTime: str | None = Field(None, description="Время закрытия")


class AzsItemV1(BaseModel):
    """Информация о торговой точке (v1)"""

    id: str | None = Field(None, description="ID торговой точки (АЗС)")
    siebelId: str | None = Field(None, description="ID торговой точки в CRM")
    contractNumber: str | None = Field(None, description="Код торговой точки (договор)")
    contractName: str | None = Field(None, description="Название торговой точки")
    status: str | None = Field(None, description="Статус точки (257 – работает, 258 – не работает)")
    countryCode: str | None = Field(None, description="Код страны")
    regionCode: str | None = Field(None, description="Код региона")
    secessionGPN: str | None = Field(None, description="Отделение ГПН по географии")
    belongsTo: str | None = Field(None, description="Название владельца или оператора")
    partner: str | None = Field(None, description="ID партнера")
    ownType: str | None = Field(None, description="Тип собственности (Own / FRAN и др.)")
    locationType: str | None = Field(None, description="Тип расположения (ROAD и т.д.)")
    brand: str | None = Field(None, description="Бренд торговой точки")
    openDate: str | None = Field(None, description="Дата открытия точки")
    closeDate: str | None = Field(None, description="Дата закрытия (если закрыта)")
    latitude: str | None = Field(None, description="Координата широты")
    longitude: str | None = Field(None, description="Координата долготы")
    type: str | None = Field(None, description="Тип торговой точки (АЗС, СТО и т.д.)")
    timeZone: str | None = Field(None, description="Часовой пояс точки")
    services: list[int] | None = Field(default_factory=list, description="Массив ID услуг")
    terminals: list[TerminalV1] | None = Field(
        default_factory=list, description="Список терминалов торговой точки"
    )
    address: AddressV1 | None = Field(None, description="Адрес торговой точки")
    prices: list[PriceItemV1] | None = Field(
        default_factory=list, description="Цены товаров на точке"
    )
    searchTxt: str | None = Field(None, description="Строка поиска")
    phone: str | None = Field(None, description="Контактный телефон")
    height_post: str | None = Field(None, description="Высота поста (в метрах)")
    working_time: list[WorkingTimeV1] | None = Field(
        default_factory=list, description="Режим работы"
    )
    only_virtual_card: bool | None = Field(
        None, description="Принимаются ли только виртуальные карты"
    )
    accept_cards: bool | None = Field(None, description="Принимаются ли карты")
    hidden_on_map: bool | None = Field(None, description="Скрыта ли точка на карте")
    active: bool | None = Field(None, description="Активна ли торговая точка")
    POIType: str | None = Field(None, description="Тип торговой точки (POI-код)")


class AzsListV1Data(BaseModel):
    """Основные данные списка торговых точек (v1)"""

    total_count: int | None = Field(None, description="Количество найденных торговых точек")
    result: list[AzsItemV1] | None = Field(
        default_factory=list, description="Список торговых точек"
    )


class AzsListV1Response(APIEnvelope[AzsListV1Data | None]):
    """Ответ метода GET /vip/v1/AZS"""


# ==========================================================
# 🔹 Список торговых точек (GET /vip/v2/azs)
# ==========================================================
class Coordinates(BaseModel):
    """Географические координаты торговой точки"""

    type: str | None = Field(default=None, description="Тип геоданных (обычно 'Point')")
    coordinates: list[float] = Field(
        default_factory=list, description="Координаты в формате [долгота, широта]"
    )


class ServiceItem(BaseModel):
    """Описание отдельной услуги"""

    name: str | None = Field(default=None, description="Наименование услуги")
    code: int | str | None = Field(default=None, description="Код услуги (числовой или строковый)")
    sort: int | None = Field(default=None, description="Порядок сортировки")


class ServiceGroup(BaseModel):
    """Группа услуг, доступных на торговой точке"""

    name: str | None = Field(default=None, description="Наименование группы услуг")
    items: list[ServiceItem] | None = Field(None, description="Список услуг, входящих в группу")


class PriceItemV2(BaseModel):
    """Информация о цене товара на торговой точке"""

    ID: str | None = Field(default=None, description="Идентификатор цены")
    GasStationID: str | None = Field(default=None, description="ID торговой точки (АЗС)")
    GoodsCode: str | None = Field(default=None, description="Код товара (из справочника GoodsCode)")
    Price: str | None = Field(default=None, description="Цена товара")
    Currency: str | None = Field(default=None, description="Код валюты, например '810;RUR'")
    DateTo: str | None = Field(default=None, description="Дата действия цены до")
    DateFrom: str | None = Field(default=None, description="Дата начала действия цены")
    hex_color: str | None = Field(default=None, description="HEX-код цвета товара (если указан)")
    name: str | None = Field(default=None, description="Название товара")
    CurrencyName: str | None = Field(default=None, description="Наименование валюты")
    sort: int | None = Field(default=None, description="Порядковый номер отображения")


class WorkingTimeV2(BaseModel):
    """Расписание работы торговой точки"""

    Weekday: str | None = Field(
        default=None,
        description="День недели или режим работы (Monday, Everyday, Round-The-Clock)",
    )
    StartWorkTime: str | None = Field(default=None, description="Время открытия, формат HH:MM")
    FinishWorkTime: str | None = Field(default=None, description="Время закрытия, формат HH:MM")
    Everyday: bool | None = Field(default=False, description="Признак работы ежедневно")
    Round_The_Clock: bool | None = Field(
        default=False,
        alias="Round-The-Clock",
        description="Признак круглосуточного режима",
    )


class AddressV2(BaseModel):
    """Адрес торговой точки"""

    track_id: str | None = Field(default=None, description="Номер трассы")
    kmRoad: str | None = Field(default=None, description="Километр трассы")
    roadSide: str | None = Field(default=None, description="Сторона дороги")
    city: str | None = Field(default=None, description="Город")
    street: str | None = Field(default=None, description="Улица")
    house: str | None = Field(default=None, description="Дом")
    building: str | None = Field(default=None, description="Строение")
    phone: str | None = Field(default=None, description="Телефон")
    fax: str | None = Field(default=None, description="Факс")


class TerminalV2(BaseModel):
    """Информация о терминале, установленном на торговой точке"""

    id: str | None = Field(default=None, description="Идентификатор терминала")
    active: bool | None = Field(default=None, description="Активен ли терминал (true — включен)")
    name: str | None = Field(default=None, description="Наименование терминала")
    status: str | None = Field(default=None, description="Статус терминала")
    type: str | None = Field(default=None, description="Тип терминала")
    connectionType: str | None = Field(default=None, description="Тип подключения")
    number: str | None = Field(default=None, description="Номер терминала")


class AzsItemV2(BaseModel):
    """Информация о торговой точке (АЗС)"""

    id: str = Field(..., description="ID торговой точки")
    siebel_id: str = Field(..., description="Идентификатор Siebel")
    status: str | None = Field(
        None, description="Статус торговой точки (257 – работает, 258 – не работает)"
    )
    full_name: str | None = Field(default=None, description="Полное наименование торговой точки")
    brand: str | None = Field(default=None, description="Бренд")
    poi_type_name: str | None = Field(default=None, description="Именование типа")
    poi_type_code: str | None = Field(default=None, description="Код типа")
    own_type_name: str = Field(..., description="Тип собственности (наименование)")
    own_type_code: str = Field(..., description="Код типа собственности (по отношению к ГПН)")
    contract_name: str | None = Field(default=None, description="Название договора")
    contract_number: str | None = Field(default=None, description="Номер договора")
    phone: str | None = Field(default=None, description="Телефон контактный")
    utc_timezone: str | None = Field(default=None, description="UTC часовой пояс АЗС (+5)")
    time_zone: str | None = Field(default=None, description="Часовой пояс АЗС относительно Москвы")
    open_date: str | None = Field(default=None, description="Дата открытия")
    close_date: str | None = Field(default=None, description="Дата закрытия")
    last_update: str | None = Field(default=None, description="Дата последнего обновления")
    height_post: str | None = Field(default=None, description="Высота поста (в метрах)")
    country_name: str | None = Field(..., description="Название страны")
    country_code: str | None = Field(..., description="Код страны")
    region_name: str | None = Field(default=None, description="Название региона")
    region_code: str | None = Field(default=None, description="Код региона")
    address_full: str | None = Field(default=None, description="Полный адрес торговой точки")
    location: Coordinates | None = Field(default=None, description="Географические координаты")
    latitude: str | None = Field(default=None, description="Широта")
    longitude: str | None = Field(default=None, description="Долгота")
    location_type: str | None = Field(default=None, description="Тип локации")
    secession_gpn: str | None = Field(default=None, description="Отделение ГПН")
    partner: str | None = Field(default=None, description="ID партнёра")
    belongs_to: str | None = Field(default=None, description="Принадлежность")
    info: str | None = Field(default=None, description="Дополнительная информация о точке")
    search_txt: str | None = Field(..., description="Строка для запроса поиска")
    accept_cards: bool | None = Field(..., description="Принимаются ли банковские карты")
    adblue: ServiceGroup | None | None = Field(default=None, description="Услуги AdBlue")
    electric_charging_station: ServiceGroup | None = Field(
        default=None, description="Электрозарядные станции"
    )
    services_with_card: ServiceGroup | None = Field(
        default=None, description="Услуги, доступные при оплате картой"
    )
    services_without_card: ServiceGroup | None = Field(
        default=None, description="Услуги, доступные без карты"
    )
    prices: list[PriceItemV2] | None = Field(
        default_factory=list, description="Список товаров с указанием цен"
    )
    payment_type: list[dict[str, Any]] | None = Field(
        default_factory=list, description="Доступные способы оплаты"
    )
    terminals: list[TerminalV2] | None = Field(
        default_factory=list, description="Список терминалов"
    )
    address: AddressV2 | None = Field(default=None, description="Адрес торговой точки")
    working_time: list[WorkingTimeV2] | None = Field(
        default_factory=list, description="Расписание работы торговой точки"
    )

    @field_validator(
        "adblue",
        "electric_charging_station",
        "services_with_card",
        "services_without_card",
        mode="before",
        check_fields=False,
    )
    def fix_empty_service_groups(cls, v: Any) -> Any:
        """
        Исправляет ошибку, когда API возвращает [] вместо объекта.
        Конвертирует [] → None, чтобы избежать ValidationError.
        """
        if v == [] or v is None:
            return None
        return v


class AzsListV2Data(BaseModel):
    """Данные списка торговых точек (v2)"""

    pass
    total_count: int = Field(..., description="Общее количество торговых точек")
    result: list[AzsItemV2] = Field(..., description="Список торговых точек (АЗС)")


class AzsListV2Response(APIEnvelope[AzsListV2Data | None]):
    """Ответ метода получения списка торговых точек (v2)"""


# ==========================================================
