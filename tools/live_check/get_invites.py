"""get_invites — Список приглашений

Что делает
    Получает список приглашений. Передаёт фильтры и пагинацию, выводит страницу приглашений.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.invites.get_invites(...)
    Раздел спецификации 1.1.60: Список приглашений

HTTP-запрос
      GET /v2/invites
    Параметры передаются: строка запроса.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      role: str | None, необязательный, по умолчанию None, тип в спецификации: string — Фильтр по ID роли: `Supervisor`, `Regulatory`, `Driver` или `Readonly`.
      user_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — Отобразить инвайты по которым произошла регистрация пользователя (true)
      sort: str | None, необязательный, по умолчанию None, тип в спецификации: string — Сортировка. Сортировка осуществляется формированием строки вида: sort=title,name,-date Поля для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC)
      status: str | None, необязательный, по умолчанию None, тип в спецификации: string — Фильтр по статусу приглашения: `Active`, `Expired` или `Finished`.
      q: str | None, необязательный, по умолчанию None, тип в спецификации: string — Поисковый запрос (Ищет email и mobile)
      page: int | None, необязательный, по умолчанию None, тип в спецификации: string — Номер страницы (Пагинация)
      on_page: int | None, необязательный, по умолчанию None, тип в спецификации: string — Количество элементов на странице.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    InviteListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: InviteList, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    InviteList:
      total_count: int, обязательное — Общее количество приглашений
      result: list[InviteItem] | None, необязательное — Список приглашений
    InviteItem:
      id: str, обязательное — ID приглашения
      user_id: str | None, необязательное — ID пользователя, если уже создан
      url: str, обязательное — Ссылка на регистрацию (уникальная, активна 3 дня)
      status: str, обязательное — Технический статус приглашения (Active, Finished и т.п.)
      status_name: str, обязательное — Отображаемое название статуса
      role: str, обязательное — Роль пользователя ('Driver', 'Admin' и т.п.)
      role_name: str, обязательное — Название роли
      attempts: int, обязательное — Количество отправок приглашения
      cards: list[InviteCard], обязательное — Список карт, связанных с приглашением
      initiator: str, обязательное — Пользователь, создавший приглашение
      contracts: list[InviteContract], обязательное — Список договоров, привязанных к приглашению
      mobile: str | None, необязательное — Номер телефона приглашенного
      email: str | None, необязательное — Email приглашенного
      communication_type: str, обязательное — Тип отправки ('sms', 'email' и т.п.)
      sended_at: int | None, необязательное — Время отправки (timestamp)
      expired_at: int, обязательное — Время истечения срока действия ссылки (timestamp)
    InviteCard:
      sid: str, обязательное — ID карты (SID)
      number: str, обязательное — Номер карты
      product: str, обязательное — Тип продукта ('wallet' и т.п.)
      comment: str | None, необязательное — Комментарий к карте (например, имя водителя)
      status: str, обязательное — Технический статус карты
      status_name: str, обязательное — Отображаемое название статуса
      contract_id: str, обязательное — ID договора, к которому относится карта
      contract_name: str, обязательное — Номер договора
    InviteContract:
      sid: str, обязательное — ID договора
      number: str, обязательное — Номер договора
      status: str, обязательное — Технический статус договора
      status_name: str, обязательное — Название статуса
      template_id: str | None, необязательное — ID шаблона виртуальной карты, если есть
      cards_count: int, обязательное — Количество карт по договору

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      require_identifier() — RequestValidationError при недопустимом значении
      validate_positive_count() — RequestValidationError при недопустимом значении
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
    'role': None,
    'user_id': None,
    'sort': None,
    'status': None,
    'q': None,
    'page': None,
    'on_page': None,
}

DESCRIPTION = (
    'Получает список приглашений. Передаёт фильтры и пагинацию, выводит страницу приглашений.'
)

if __name__ == "__main__":
    run('get_invites', PARAMS, mutating=False, description=DESCRIPTION)
