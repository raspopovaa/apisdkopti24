"""remove_limit — Удалить продуктовый лимит карты.

Что делает
    Удаляет продуктовый лимит. Передаёт limit_id, contract_id и опциональный group_id,
    выводит bool-envelope результата.
    Изменяет данные: да. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.limits.remove_limit(...)
    Раздел спецификации 1.1.60: Удаление продуктового лимита по карте и группе карт

HTTP-запрос
      POST /v1/removeLimit
    Параметры передаются: тело (form).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID договора.
      limit_id: str, обязательный, тип в спецификации: string — ID продуктового лимита.
      group_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID группы карт. Если ID группы карты не передано, то будет удален лимит по карте. Если передан ID группы карт, то будет удален лимит по группе карт

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    RemoveLimitResponse:
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
    'contract_id': common('contract_id'),
    'limit_id': common('limit_id'),
    'group_id': None,
}

DESCRIPTION = 'Удаляет продуктовый лимит. Передаёт limit_id, contract_id и опциональный group_id, выводит bool-envelope результата.'

if __name__ == "__main__":
    run('remove_limit', PARAMS, mutating=True, description=DESCRIPTION)
