"""get_card_groups — Список групп карт

Что делает
    Получает группы карт договора. Передаёт contract_id, выводит список групп карт.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.card_groups.get_card_groups(...)
    Раздел спецификации 1.1.60: Список групп карт

HTTP-запрос
      GET /v1/cardGroups
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID договора

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    CardGroupListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: CardGroupListData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    CardGroupListData:
      total_count: int, обязательное — Общее количество групп
      result: list[CardGroupItem] | None, необязательное — Список групп карт
    CardGroupItem:
      id: str, обязательное — Идентификатор группы карт
      name: str, обязательное — Название группы карт
      cards_count: int | str, обязательное — Количество карт в группе
      status: str, обязательное — Статус группы (например, Synchronize)
      contract_id: str, обязательное — Идентификатор договора

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
}

DESCRIPTION = 'Получает группы карт договора. Передаёт contract_id, выводит список групп карт.'

if __name__ == "__main__":
    run('get_card_groups', PARAMS, mutating=False, description=DESCRIPTION)
