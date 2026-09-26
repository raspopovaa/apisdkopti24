"""get_card_drivers — Список водителей по карте

Что делает
    Получает водителей карты. Передаёт card_id и contract_id, выводит список водителей.
    Изменяет данные: нет. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.cards.get_card_drivers(...)
    Раздел спецификации 1.1.60: Список водителей по карте

HTTP-запрос
      GET /v2/cards/{card_id}/drivers
    Параметры передаются: путь URL, строка запроса.
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      card_id: str, обязательный — Идентификатор топливной карты.
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    CardDriversResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: CardDriversData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    CardDriversData:
      total_count: int, обязательное — Количество водителей, связанных с картой
      result: list[CardDriverInfo] | None, необязательное — Список водителей
    CardDriverInfo:
      id: str, обязательное — ID пользователя/водителя
      login: str, обязательное — Логин (обычно телефон)
      first_name: str, обязательное — Имя водителя
      last_name: str, обязательное — Фамилия водителя
      middle_name: str | None, необязательное — Отчество водителя
      date: str | None, необязательное — Дата рождения или дата регистрации
      position: str | None, необязательное — Должность водителя
      role: str, обязательное — Роль пользователя
      mobile_phone: str, обязательное — Номер телефона
      email: str | None, необязательное — Email водителя

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      require_identifier() — RequestValidationError при недопустимом значении
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
    'card_id': common('card_id'),
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Получает водителей карты. Передаёт card_id и contract_id, выводит список водителей.'

if __name__ == "__main__":
    run('get_card_drivers', PARAMS, mutating=False, description=DESCRIPTION)
