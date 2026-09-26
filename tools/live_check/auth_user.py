"""auth_user — Авторизовать пользователя и открыть сессию SDK.

Что делает
    Авторизует пользователя, получает session_id и список доступных договоров. Выводит
    полный envelope авторизации и сохраняет выбранный contract_id для следующих методов.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.auth.auth_user(...)
    Раздел спецификации 1.1.60: Авторизация пользователя

HTTP-запрос
      POST /v1/authUser
    Параметры передаются: тело (form).
    Заголовки: api_key, date_time.

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None — Локально выбрать договор по ID после получения ответа. Параметр не отправляется в authUser.
      contract_number: str | None, необязательный, по умолчанию None — Локально выбрать договор по номеру после получения ответа. Параметр не отправляется в authUser.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    AuthUserResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: AuthUserData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    AuthUserData:
      client_id: str, обязательное — ID клиента
      client_status: str, обязательное — Статус пользователя (Active, Blocked, и т.п.)
      org_name: str, обязательное — Наименование организации
      session_id: str, обязательное — ID текущей сессии пользователя
      user_id: str, обязательное — ID пользователя
      contracts: list[ContractInfo], обязательное — Список доступных договоров
      role_id: str, обязательное — ID роли пользователя (например, Supervisor)
      role_name: str, обязательное — Название роли пользователя (например, Администратор)
      read_only: bool, обязательное — Флаг режима только чтение
      user_name: str | None, необязательное — Имя пользователя
      user_patronymic: str | None, необязательное — Отчество пользователя
      user_surname: str | None, необязательное — Фамилия пользователя
      last_contract: str | None, необязательное — ID последнего использованного договора
      access: AccessRights, обязательное — Права доступа (ЛК/МП/API)
      email: str, обязательное — Электронная почта
      phone: str | None, необязательное — Телефон
    ContractInfo:
      id: str, обязательное — ID договора
      number: str, обязательное — Номер договора
      mpc: bool, обязательное — Возможность выпуска МПК
      template_id: str | None, необязательное — ID шаблона ВК
      cards_count: int, обязательное — Количество карт на договоре
      one_price: bool, обязательное — Признак единой цены
    AccessRights:
      web: bool, обязательное — Доступ к ЛК
      api: bool, обязательное — Доступ к API
      mobile: bool, обязательное — Доступ к МП

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      специальных проверок нет
      pydantic.ValidationError / RequestValidationError — неверный тип или формат
      параметра по модели запроса.
      ContractSelectionError — несколько договоров, а contract_id не указан.
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
    Повтор при сетевой ошибке: network_only; идемпотентность: нет.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'contract_id': common('contract_id'),
    'contract_number': None,
}

DESCRIPTION = 'Авторизует пользователя, получает session_id и список доступных договоров. Выводит полный envelope авторизации и сохраняет выбранный contract_id для следующих методов.'

if __name__ == "__main__":
    run('auth_user', PARAMS, mutating=False, description=DESCRIPTION)
