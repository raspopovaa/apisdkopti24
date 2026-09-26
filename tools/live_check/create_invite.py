"""create_invite — Создание приглашения с отправкой

Что делает
    Создаёт приглашение пользователя. Передаёт invite JSON и with_send, выводит envelope
    созданного приглашения.
    Изменяет данные: да. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.invites.create_invite(...)
    Раздел спецификации 1.1.60: Создание приглашения с отправкой

HTTP-запрос
      POST /v2/invites
      POST /v2/invites_free (вариант without_send)
    Параметры передаются: тело (json).
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      data: InviteCreateRequest | Mapping[str, object], обязательный — Данные приглашения: роль, телефон или email, список карт и список договоров с возможным `template_id`.
      with_send: bool, необязательный, по умолчанию True — описание в спецификации не найдено

Модели проверки входящих данных (запрос)
    InviteCreateRequest:
      role: str, обязательное — ID роли
      mobile: str | None, необязательное — Номер телефона
      email: str | None, необязательное — Email
      cards: list[str], необязательное — ID прикрепляемых карт
      contracts: list[_InviteContractRequest], необязательное — Договоры, прикрепляемые после регистрации
    _InviteContractRequest:
      id: str, обязательное — ID договора
      template_id: str | None, необязательное — ID шаблона виртуальной карты

Модели проверки исходящих данных (ответ API)
    InviteResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: InviteActionResult, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    InviteActionResult:
      id: str, обязательное — ID приглашения
      url: str, обязательное — Ссылка на приглашение
      attempts: int, обязательное — Количество попыток отправки
      expired_at: int, обязательное — Дата истечения срока действия ссылки (timestamp)

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
    Повтор при сетевой ошибке: never; идемпотентность: нет.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'data': method_value('create_invite', 'data'),
    'with_send': True,
}

DESCRIPTION = 'Создаёт приглашение пользователя. Передаёт invite JSON и with_send, выводит envelope созданного приглашения.'

if __name__ == "__main__":
    run('create_invite', PARAMS, mutating=True, description=DESCRIPTION)
