"""block_card — Заблокировать или разблокировать одну или несколько топливных карт.

Что делает
    Блокирует или разблокирует карты. Передаёт список card_ids и флаг block, выводит
    envelope со списком ID.
    Изменяет данные: да. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.cards.block_card(...)
    Раздел спецификации 1.1.60: Блокировка и разблокировка карты

HTTP-запрос
      POST /v1/blockCard
    Параметры передаются: тело (form).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      card_ids: list[str], обязательный — Список идентификаторов топливных карт.
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта
      block: bool, необязательный, по умолчанию True, тип в спецификации: bool — `true` — заблокировать карту, `false` — разблокировать.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    IDListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: list[str] | None, необязательное — Список идентификаторов обработанных карт
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

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
    'card_ids': [common("card_id")],
    'contract_id': common('contract_id'),
    'block': True,
}

DESCRIPTION = 'Блокирует или разблокирует карты. Передаёт список card_ids и флаг block, выводит envelope со списком ID.'

if __name__ == "__main__":
    run('block_card', PARAMS, mutating=True, description=DESCRIPTION)
