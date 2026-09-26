"""get_cards_by_group — Список топливных карт по группе карт

Что делает
    Получает карты группы. Передаёт group_id и contract_id, выводит список карт группы.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.cards.get_cards_by_group(...)
    Раздел спецификации 1.1.60: Список топливных карт по группе карт

HTTP-запрос
      GET /v1/cards
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      group_id: str, обязательный, тип в спецификации: string — ID группы карт
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    CardGroupResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: CardGroupData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    CardGroupData:
      total_count: int, обязательное — Количество карт в группе
      result: list[CardGroupInfo] | None, необязательное — Список карт в группе
    CardGroupInfo:
      id: str, обязательное — ID карты
      group: str | None, необязательное — ID группы карт
      contract_id: str, обязательное — ID договора
      number: str, обязательное — Номер карты
      status: str, обязательное — Статус карты
      comment: str | None, необязательное — Комментарий
      product: str, обязательное — Тип продукта
      payment_of_tolls: str, обязательное — Оплата платных дорог ('Y' или 'N')
      sync_group_state: str | None, необязательное — Статус синхронизации группы

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
    'group_id': common('group_id'),
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Получает карты группы. Передаёт group_id и contract_id, выводит список карт группы.'

if __name__ == "__main__":
    run('get_cards_by_group', PARAMS, mutating=False, description=DESCRIPTION)
