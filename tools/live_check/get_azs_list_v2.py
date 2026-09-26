"""get_azs_list_v2 — Список торговых точек (v.2)

Что делает
    Получает список АЗС v2. Передаёт filter/q, выводит список АЗС.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.dictionaries.get_azs_list_v2(...)
    Раздел спецификации 1.1.60: Список торговых точек (v.2)

HTTP-запрос
      GET /v2/azs
    Параметры передаются: строка запроса.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      filter: AzsV2Filter | Mapping[str, object] | None, необязательный, по умолчанию None, тип в спецификации: json — JSON-объект для фильтрации списка торговых точек.
      q: str | None, необязательный, по умолчанию None, тип в спецификации: string — Поисковая строка запроса (Ищет по наименованию АЗС и адресу)
      id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID точки АЗС
      page: int | None, необязательный, по умолчанию None, тип в спецификации: int — Номер страницы
      on_page: int | None, необязательный, по умолчанию None, тип в спецификации: int — Количество записей на странице

Модели проверки входящих данных (запрос)
    AzsV2Query:
      q: str | None, необязательное — описание не задано
      id: Optional[Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)]], необязательное — описание не задано
      page: Optional[Annotated[int, FieldInfo(annotation=NoneType, required=True, metadata=[Ge(ge=1)])]], необязательное — описание не задано
      on_page: Optional[Annotated[int, FieldInfo(annotation=NoneType, required=True, metadata=[Ge(ge=1)])]], необязательное — описание не задано
      filter: AzsV2Filter | None, необязательное — описание не задано
    AzsV2Filter:
      services_with_card: list[str] | None, необязательное — описание не задано
      services_without_card: list[str] | None, необязательное — описание не задано
      own_types: list[str] | None, необязательное — описание не задано
      payment_types: list[str] | None, необязательное — описание не задано
      fuel: list[str] | None, необязательное — описание не задано
      diesel: list[str] | None, необязательное — описание не задано
      gaz: list[str] | None, необязательное — описание не задано
      electric_charging_station: list[str] | None, необязательное — описание не задано
      adblue: list[str] | None, необязательное — описание не задано
      poi_types: list[str] | None, необязательное — описание не задано
      countries: list[str] | None, необязательное — описание не задано
      regions: list[str] | None, необязательное — описание не задано

Модели проверки исходящих данных (ответ API)
    AzsListV2Response:
      status: ResponseStatus, обязательное — Статус ответа API
      data: AzsListV2Data | None, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    AzsListV2Data:
      total_count: int, обязательное — Общее количество торговых точек
      result: list[AzsItemV2], обязательное — Список торговых точек (АЗС)
    AzsItemV2:
      id: str, обязательное — ID торговой точки
      siebel_id: str, обязательное — Идентификатор Siebel
      status: str, обязательное — Статус торговой точки (257 – работает, 258 – не работает)
      full_name: str | None, необязательное — Полное наименование торговой точки
      brand: str | None, необязательное — Бренд
      poi_type_name: str | None, необязательное — Именование типа
      poi_type_code: str | None, необязательное — Код типа
      own_type_name: str, обязательное — Тип собственности (наименование)
      own_type_code: str, обязательное — Код типа собственности (по отношению к ГПН)
      contract_name: str | None, необязательное — Название договора
      contract_number: str | None, необязательное — Номер договора
      phone: str | None, необязательное — Телефон контактный
      utc_timezone: str | None, обязательное — UTC часовой пояс АЗС (+5)
      time_zone: str | None, необязательное — Часовой пояс АЗС относительно Москвы
      open_date: str | None, необязательное — Дата открытия
      close_date: str | None, необязательное — Дата закрытия
      last_update: str | None, необязательное — Дата последнего обновления
      height_post: str | None, необязательное — Высота поста (в метрах)
      country_name: str | None, обязательное — Название страны
      country_code: str | None, обязательное — Код страны
      region_name: str | None, необязательное — Название региона
      region_code: str | None, необязательное — Код региона
      address_full: str | None, необязательное — Полный адрес торговой точки
      location: Coordinates | None, необязательное — Географические координаты
      latitude: str | None, необязательное — Широта
      longitude: str | None, необязательное — Долгота
      location_type: str | None, необязательное — Тип локации
      secession_gpn: str | None, необязательное — Отделение ГПН
      partner: str | None, необязательное — ID партнёра
      belongs_to: str | None, необязательное — Принадлежность
      info: str | None, необязательное — Дополнительная информация о точке
      search_txt: str | None, обязательное — Строка для запроса поиска
      accept_cards: bool | None, обязательное — Принимаются ли банковские карты
      adblue: ServiceGroup | None, необязательное — Услуги AdBlue
      electric_charging_station: ServiceGroup | None, необязательное — Электрозарядные станции
      services_with_card: ServiceGroup | None, необязательное — Услуги, доступные при оплате картой
      services_without_card: ServiceGroup | None, необязательное — Услуги, доступные без карты
      prices: list[PriceItemV2] | None, необязательное — Список товаров с указанием цен
      payment_type: list[PaymentType] | None, необязательное — Доступные способы оплаты
      terminals: list[TerminalV2] | None, необязательное — Список терминалов
      address: AddressV2 | None, необязательное — Адрес торговой точки
      working_time: list[WorkingTimeV2] | None, необязательное — Расписание работы торговой точки
    Coordinates:
      type: str | None, необязательное — Тип геоданных (обычно 'Point')
      coordinates: list[float], необязательное — Координаты в формате [долгота, широта]
    ServiceGroup:
      name: str, обязательное — Наименование группы услуг
      items: list[ServiceItem], обязательное — Список услуг, входящих в группу
    ServiceItem:
      name: str, обязательное — Наименование услуги
      code: int | str, обязательное — Код услуги (числовой или строковый)
      sort: int | None, необязательное — Порядок сортировки
    PriceItemV2:
      ID: str | None, необязательное — Идентификатор цены
      GasStationID: str | None, необязательное — ID торговой точки (АЗС)
      GoodsCode: str | None, необязательное — Код товара (из справочника GoodsCode)
      Price: str | None, необязательное — Цена товара
      Currency: str | None, необязательное — Код валюты, например '810;RUR'
      DateTo: str | None, необязательное — Дата действия цены до
      DateFrom: str | None, необязательное — Дата начала действия цены
      hex_color: str | None, необязательное — HEX-код цвета товара (если указан)
      name: str | None, необязательное — Название товара
      CurrencyName: str | None, необязательное — Наименование валюты
      sort: int | None, необязательное — Порядковый номер отображения
    PaymentType:
      code: str | None, необязательное — Код способа оплаты
      name: str | None, необязательное — Название способа оплаты
    TerminalV2:
      id: str | None, необязательное — Идентификатор терминала
      active: bool | None, необязательное — Активен ли терминал (true — включен)
      name: str | None, необязательное — Наименование терминала
      status: str | None, необязательное — Статус терминала
      type: str | None, необязательное — Тип терминала
      connectionType: str | None, необязательное — Тип подключения
      number: str | None, необязательное — Номер терминала
    AddressV2:
      track_id: str | None, необязательное — Номер трассы
      kmRoad: str | None, необязательное — Километр трассы
      roadSide: str | None, необязательное — Сторона дороги
      city: str | None, необязательное — Город
      street: str | None, необязательное — Улица
      house: str | None, необязательное — Дом
      building: str | None, необязательное — Строение
      phone: str | None, необязательное — Телефон
      fax: str | None, необязательное — Факс
    WorkingTimeV2:
      Weekday: str | None, необязательное — День недели или режим работы (Monday, Everyday, Round-The-Clock)
      StartWorkTime: str | None, необязательное — Время открытия, формат HH:MM
      FinishWorkTime: str | None, необязательное — Время закрытия, формат HH:MM
      Everyday: bool, обязательное — Признак работы ежедневно
      Round-The-Clock: bool, обязательное — Признак круглосуточного режима

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      специальных проверок нет
      pydantic.ValidationError / RequestValidationError — неверный тип или формат
      параметра по модели запроса.
    Ответ API (HTTP-код или status.code; текст сервера — в «Сообщение сервера: …»):
      400 ValidationError — неверные параметры или структура запроса;
      401 NotAuthenticatedError — сессия недействительна (SDK один раз авторизуется
          заново и повторяет запрос);
      403 AccessDeniedError — нет прав на объект, роль, IP, api_key или тариф;
      404 NotFoundError — объект или маршрут не найден;
      409 DuplicateConflictError — повтор однотипного запроса;
      429/509 RateLimitError — превышен лимит запросов;
      5xx ServerError — ошибка сервера API.
    Проверка ответа моделью SDK: pydantic.ValidationError — ответ с HTTP 200 не совпал
      с моделью (поле отсутствует, null вместо значения, другой тип); список полей
      выводится при запуске, известные расхождения — в docs/spec-compatibility.md.
    Сеть: APIConnectionError (сервер недоступен, в т. ч. IP вне разрешённых стран),
      OperationTimeoutError (исчерпан общий лимит времени), RetryBudgetExceededError.
    Повтор при сетевой ошибке: только безопасные читающие; идемпотентность: да.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'filter': None,
    'q': None,
    'id': None,
    'page': None,
    'on_page': None,
}

DESCRIPTION = 'Получает список АЗС v2. Передаёт filter/q, выводит список АЗС.'

if __name__ == "__main__":
    run('get_azs_list_v2', PARAMS, mutating=False, description=DESCRIPTION)
