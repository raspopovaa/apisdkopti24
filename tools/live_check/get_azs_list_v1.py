"""get_azs_list_v1 — Список торговых точек

Что делает
    Получает список АЗС v1. Передаёт пагинацию и опциональный filter/id, выводит список АЗС.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.dictionaries.get_azs_list_v1(...)
    Раздел спецификации 1.1.60: Список торговых точек

HTTP-запрос
      GET /v1/AZS
    Параметры передаются: строка запроса.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      page: int, необязательный, по умолчанию 1, тип в спецификации: uint — Номер страницы начиная с 1
      onpage: int, необязательный, по умолчанию 10, тип в спецификации: uint — Количество элементов на странице (0 – если нужно вывести все элементы)
      filter: AzsV1Filter | Mapping[str, object] | None, необязательный, по умолчанию None, тип в спецификации: json — JSON-объект для фильтрации списка торговых точек.
      id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID торговой точки для получения одной детальной записи.
      q: str | None, необязательный, по умолчанию None, тип в спецификации: string — Поисковая строка запроса (Ищет по наименованию ТТ, адресу и номеру терминала)

Модели проверки входящих данных (запрос)
    AzsV1Query:
      page: int, необязательное — описание не задано
      onpage: int, необязательное — описание не задано
      filter: AzsV1Filter | None, необязательное — описание не задано
      q: str | None, необязательное — описание не задано
      id: Optional[Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)]], необязательное — описание не задано
    AzsV1Filter:
      region: list[str] | None, необязательное — описание не задано
      country: list[str] | None, необязательное — описание не задано
      owntype: list[str] | None, необязательное — описание не задано
      type: list[str] | None, необязательное — описание не задано
      status: list[str] | None, необязательное — описание не задано
      services: list[int] | None, необязательное — описание не задано
      goods: list[str] | None, необязательное — описание не задано

Модели проверки исходящих данных (ответ API)
    AzsListV1Response:
      status: ResponseStatus, обязательное — Статус ответа API
      data: AzsListV1Data | None, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    AzsListV1Data:
      total_count: int, обязательное — Количество найденных торговых точек
      result: list[AzsItemV1] | None, необязательное — Список торговых точек
    AzsItemV1:
      id: str, обязательное — ID торговой точки (АЗС)
      siebelId: str, обязательное — ID торговой точки в CRM
      contractNumber: str, обязательное — Код торговой точки (договор)
      contractName: str, обязательное — Название торговой точки
      status: str, обязательное — Статус точки (257 – работает, 258 – не работает)
      countryCode: str, обязательное — Код страны
      regionCode: str, обязательное — Код региона
      secessionGPN: str | None, необязательное — Отделение ГПН по географии
      belongsTo: str, обязательное — Название владельца или оператора
      partner: str, обязательное — ID партнера
      ownType: str, обязательное — Тип собственности (Own / FRAN и др.)
      locationType: str | None, необязательное — Тип расположения (ROAD и т.д.)
      brand: str | None, необязательное — Бренд торговой точки
      openDate: str, обязательное — Дата открытия точки
      closeDate: str | None, необязательное — Дата закрытия (если закрыта)
      latitude: str, обязательное — Координата широты
      longitude: str, обязательное — Координата долготы
      type: str, обязательное — Тип торговой точки (АЗС, СТО и т.д.)
      timeZone: str | None, необязательное — Часовой пояс точки
      services: list[int] | None, необязательное — Массив ID услуг
      terminals: list[TerminalV1] | None, необязательное — Список терминалов торговой точки
      address: AddressV1, обязательное — Адрес торговой точки
      prices: list[PriceItemV1] | None, необязательное — Цены товаров на точке
      searchTxt: str, обязательное — Строка поиска
      phone: str | None, необязательное — Контактный телефон
      height_post: str | None, необязательное — Высота поста (в метрах)
      working_time: list[WorkingTimeV1] | None, необязательное — Режим работы
      only_virtual_card: bool | None, необязательное — Принимаются ли только виртуальные карты
      accept_cards: bool | None, необязательное — Принимаются ли карты
      hidden_on_map: bool | None, необязательное — Скрыта ли точка на карте
      active: bool | None, необязательное — Активна ли торговая точка
      POIType: str | None, необязательное — Тип торговой точки (POI-код)
    TerminalV1:
      id: str, обязательное — Идентификатор терминала
      active: bool, обязательное — Статус активности терминала (True — включен, False — выключен)
      name: str, обязательное — Наименование терминала
      status: str, обязательное — Статус терминала
      type: str, обязательное — Тип терминала
      connectionType: str, обязательное — Тип подключения терминала
      number: str, обязательное — Номер терминала
    AddressV1:
      track_id: str | None, необязательное — Номер трассы, если применимо
      kmRoad: str | None, необязательное — Километр трассы
      roadSide: str | None, необязательное — Сторона дороги
      city: str, обязательное — Город
      street: str | None, необязательное — Улица
      house: str | None, необязательное — Дом
      building: str | None, необязательное — Строение
      phone: str | None, необязательное — Телефон торговой точки
      fax: str | None, необязательное — Факс
    PriceItemV1:
      ID: str, обязательное — Идентификатор записи цены
      GasStationID: str, обязательное — ID торговой точки (АЗС)
      GoodsCode: str, обязательное — Код товара (см. справочник GoodsCode)
      Price: str, обязательное — Цена товара
      Currency: str, обязательное — Валюта (код и наименование через ';')
      DateTo: str, обязательное — Дата окончания действия цены
      DateFrom: str, обязательное — Дата начала действия цены
    WorkingTimeV1:
      Weekday: str, обязательное — День недели или режим работы
      StartWorkTime: str | None, необязательное — Время открытия
      FinishWorkTime: str | None, необязательное — Время закрытия

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
    'page': 1,
    'onpage': 10,
    'filter': None,
    'id': None,
    'q': None,
}

DESCRIPTION = (
    'Получает список АЗС v1. Передаёт пагинацию и опциональный filter/id, выводит список АЗС.'
)

if __name__ == "__main__":
    run('get_azs_list_v1', PARAMS, mutating=False, description=DESCRIPTION)
