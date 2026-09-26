"""get_users — Список пользователей

Что делает
    Получает список пользователей. Передаёт фильтры и пагинацию, выводит страницу
    пользователей.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.users.get_users(...)
    Раздел спецификации 1.1.60: Список пользователей

HTTP-запрос
      GET /v2/users
    Параметры передаются: строка запроса.
    contract_id передаётся: query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      sort: str | None, необязательный, по умолчанию None, тип в спецификации: string — Сортировка. Сортировка осуществляется формированием строки вида: sort=title,name,-date Поля для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC)
      page: int | None, необязательный, по умолчанию None, тип в спецификации: string — Номер страницы (Пагинация)
      on_page: int | None, необязательный, по умолчанию None, тип в спецификации: string — Количество элементов на странице.
      q: str | None, необязательный, по умолчанию None, тип в спецификации: string — Поисковый запрос (Ищет по Фамилия, Имя, Отчество, Логин, Электронный ящик, Номер мобильного телефона)
      filter: UserFilter | Mapping[str, object] | None, необязательный, по умолчанию None, тип в спецификации: json — Объект фильтрации пользователей, например `{"role": "Driver", "active": true}`.
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — Вывести пользователей с этим привязанным договором

Модели проверки входящих данных (запрос)
    UsersQuery:
      sort: str | None, необязательное — описание не задано
      filter: UserFilter | None, необязательное — описание не задано
      q: str | None, необязательное — описание не задано
      page: Optional[Annotated[int, FieldInfo(annotation=NoneType, required=True, metadata=[Ge(ge=1)])]], необязательное — описание не задано
      on_page: Optional[Annotated[int, FieldInfo(annotation=NoneType, required=True, metadata=[Ge(ge=1)])]], необязательное — описание не задано
      contract_id: Optional[Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)]], необязательное — описание не задано
    UserFilter:
      role: str | None, необязательное — описание не задано
      active: bool | None, необязательное — описание не задано

Модели проверки исходящих данных (ответ API)
    UserListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: UserList | None, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    UserList:
      total_count: int, обязательное — Общее количество пользователей
      result: list[UserItem] | None, необязательное — Список пользователей
    UserItem:
      id: str, обязательное — ID пользователя в системе
      login: str, обязательное — Логин пользователя (обычно номер телефона)
      first_name: str, обязательное — Имя пользователя
      last_name: str, обязательное — Фамилия пользователя
      middle_name: str, обязательное — Отчество пользователя
      date: str | None, обязательное — Дата рождения; реальный API может вернуть null
      position: str, обязательное — Должность или UUID должности
      role: UserRole, обязательное — Роль пользователя
      active: bool | None, необязательное — Активен ли пользователь
      access: UserAccess, обязательное — Информация о доступах пользователя
      mobile_phone: str | None, необязательное — Мобильный телефон пользователя
      email: str | None, необязательное — Email пользователя
      contracts: list[UserContractItem], необязательное — Список договоров пользователя
      cards: list[UserCardItem], необязательное — Список карт пользователя
    UserRole:
      id: str, обязательное — ID роли пользователя (Driver, Manager и т.д.)
      name: str, обязательное — Название роли пользователя
    UserAccess:
      web: bool, обязательное — Доступ через веб-интерфейс
      api: bool, обязательное — Доступ через API
      mobile: bool, обязательное — Доступ через мобильное приложение
    UserContractItem:
      sid: str, обязательное — ID договора
      number: str, обязательное — Номер договора
      available: bool | str, обязательное — Доступен ли договор пользователю
      template_id: str | None, необязательное — ID шаблона договора, если есть
      cards_count: int, обязательное — Количество карт по договору
      status: UserStatus, обязательное — Статус договора
    UserStatus:
      id: str, обязательное — ID статуса договора, например Active
      name: str, обязательное — Название статуса договора, например Активен
    UserCardItem:
      sid: str, обязательное — SID карты
      number: str, обязательное — Номер карты
      mpc: bool, обязательное — Признак мультикарты
      product: str, обязательное — Тип продукта карты (wallet, limit и т.д.)
      comment: str | None, необязательное — Комментарий к карте
      status: str, обязательное — Статус карты (Active, Blocked и т.п.)
      contract_id: str, обязательное — ID договора, к которому привязана карта
      contract_name: str, обязательное — Название договора
      available: bool | str, обязательное — Доступна ли карта пользователю

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
    'sort': None,
    'page': None,
    'on_page': None,
    'q': None,
    'filter': None,
    'contract_id': common('contract_id'),
}

DESCRIPTION = (
    'Получает список пользователей. Передаёт фильтры и пагинацию, выводит страницу пользователей.'
)

if __name__ == "__main__":
    run('get_users', PARAMS, mutating=False, description=DESCRIPTION)
