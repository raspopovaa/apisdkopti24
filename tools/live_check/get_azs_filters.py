"""get_azs_filters — Запрос списка фильтров торговых точек

Что делает
    Получает фильтры АЗС. Передаёт только session/api context, выводит справочник фильтров.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.dictionaries.get_azs_filters(...)
    Раздел спецификации 1.1.60: Запрос списка фильтров торговых точек

HTTP-запрос
      GET /v2/azs/filters
    Параметры передаются: без параметров.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      нет параметров

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    AzsFiltersResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: list[AzsFilterItem] | None, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    AzsFilterItem:
      filter: str, обязательное — Ключ фильтра (например: services_with_card, countries и т.д.)
      name: str, обязательное — Название фильтра (человекочитаемое)
      items: list[AzsFilterValue], обязательное — Список значений для данного фильтра
    AzsFilterValue:
      name: str, обязательное — Название значения фильтра
      code: str | None, обязательное — Код значения фильтра; реальный API может вернуть null

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
PARAMS: dict = {}

DESCRIPTION = (
    'Получает фильтры АЗС. Передаёт только session/api context, выводит справочник фильтров.'
)

if __name__ == "__main__":
    run('get_azs_filters', PARAMS, mutating=False, description=DESCRIPTION)
