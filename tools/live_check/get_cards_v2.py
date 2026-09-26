"""get_cards_v2 — Получить постраничный список топливных карт договора через API v2.

Что делает
    Получает список карт v2. Передаёт contract_id, фильтры и пагинацию, выводит страницу
    карт.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.cards.get_cards_v2(...)
    Раздел спецификации 1.1.60: Список карт договора (v.2)

HTTP-запрос
      GET /v2/cards
    Параметры передаются: строка запроса.
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID договора (Можно передать в заголовке запроса, а не только в URI - строке). Если не передать, то подставим 1й договор из списка.
      sort: str, необязательный, по умолчанию '-id', тип в спецификации: string — Сортировка (sort=-id). Поле для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC).
      q: str | None, необязательный, по умолчанию None, тип в спецификации: string — Поисковый запрос (Ищет по комментарию на карте, по номерам карт).
      status: str | None, необязательный, по умолчанию None, тип в спецификации: string — Фильтрует по статусам карт (Справочник CardStatus)
      carrier: str | None, необязательный, по умолчанию None, тип в спецификации: string — Фильтрует по типу карты (Plastic – физическая карта, Virtual Card – виртуальная карта).
      platon: bool | None, необязательный, по умолчанию None, тип в спецификации: bool — Отобразит карты с подключенной услугой Платон.
      avtodor: bool | None, необязательный, по умолчанию None, тип в спецификации: bool — Отобразит карты с подключенной услугой Автодор.
      users: bool | None, необязательный, по умолчанию None, тип в спецификации: bool — С помощью данного параметра подгружаются пользователи и в списке карт заполняются поля users и mpc. Время ответа зависит от количества карт и количества пользователей.
      group_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID группы карт. При передаче параметра отобразит только карты этой группы.
      page: int | None, необязательный, по умолчанию None, тип в спецификации: string — Номер страницы (Пагинация).
      onpage: int | None, необязательный, по умолчанию None, тип в спецификации: string — Элементов на странице (Пагинация).

Модели проверки входящих данных (запрос)
    CardsV2Query:
      contract_id: Optional[Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)]], необязательное — описание не задано
      group_id: Optional[Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)]], необязательное — описание не задано
      sort: str, необязательное — описание не задано
      q: str | None, необязательное — описание не задано
      status: str | None, необязательное — описание не задано
      carrier: str | None, необязательное — описание не задано
      platon: bool | None, необязательное — описание не задано
      avtodor: bool | None, необязательное — описание не задано
      users: bool | None, необязательное — описание не задано
      page: Optional[Annotated[int, FieldInfo(annotation=NoneType, required=True, metadata=[Ge(ge=1)])]], необязательное — описание не задано
      onpage: Optional[Annotated[int, FieldInfo(annotation=NoneType, required=True, metadata=[Ge(ge=1)])]], необязательное — описание не задано

Модели проверки исходящих данных (ответ API)
    CardsV2Response:
      status: ResponseStatus, обязательное — Статус ответа API
      data: CardsV2Data, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    CardsV2Data:
      total_count: int, обязательное — Общее количество найденных карт
      result: list[CardV2Item] | None, необязательное — Список карт договора
    CardV2Item:
      id: str, обязательное — Уникальный идентификатор карты
      group_id: str | None, необязательное — ID группы карт, если назначена
      group_name: str | None, необязательное — Название группы карт
      contract_id: str, обязательное — ID договора, к которому принадлежит карта
      contract_name: str, обязательное — Название договора
      number: str, обязательное — Номер топливной карты
      status: str, обязательное — Системное значение статуса карты
      status_name: str | None, необязательное — Отображаемое имя статуса (например 'Активна')
      comment: str | None, необязательное — Комментарий, установленный пользователем
      product: str, обязательное — Тип продукта, например 'limit' или 'wallet'
      product_name: str | None, необязательное — Отображаемое имя продукта
      carrier: str, обязательное — Тип носителя карты ('Plastic' или 'Virtual Card')
      carrier_name: str | None, необязательное — Название типа носителя карты
      platon: bool, обязательное — Признак наличия поддержки Platon (оплата проезда)
      avtodor: bool, обязательное — Признак наличия поддержки Автодора
      sync_group_state: str | None, необязательное — Состояние синхронизации группы карт
      users: list[str] | None, необязательное — Список ID пользователей, привязанных к карте
      mpc: bool | None, необязательное — Признак наличия мультипроцессингового центра (mpc)

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
    'contract_id': common('contract_id'),
    'sort': '-id',
    'q': None,
    'status': None,
    'carrier': None,
    'platon': None,
    'avtodor': None,
    'users': None,
    'group_id': None,
    'page': None,
    'onpage': None,
}

DESCRIPTION = (
    'Получает список карт v2. Передаёт contract_id, фильтры и пагинацию, выводит страницу карт.'
)

if __name__ == "__main__":
    run('get_cards_v2', PARAMS, mutating=False, description=DESCRIPTION)
