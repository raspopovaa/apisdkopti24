"""order_cards — Заказ топливных карт

Что делает
    Создаёт заявку на выпуск пластиковых карт. Передаёт contract_id, count и office_id,
    выводит envelope заявки.
    Изменяет данные: да. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.contracts.order_cards(...)
    Раздел спецификации 1.1.60: Заказ топливных карт

HTTP-запрос
      POST /v2/orderCards
    Параметры передаются: тело (form).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      count: int, обязательный, тип в спецификации: string — Количество заказываемых карт.
      office_id: str, обязательный, тип в спецификации: string — ID офиса продаж из справочника `Office`.
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта (Можно передать в заголовке запроса, а не только в URI - строке)

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    OrderCardsResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: bool, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

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
    Повтор при сетевой ошибке: never; идемпотентность: нет.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'count': method_value('order_cards', 'count'),
    'office_id': common('office_id'),
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Создаёт заявку на выпуск пластиковых карт. Передаёт contract_id, count и office_id, выводит envelope заявки.'

if __name__ == "__main__":
    run('order_cards', PARAMS, mutating=True, description=DESCRIPTION)
