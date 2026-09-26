"""get_dictionary — Общие справочники

Что делает
    Получает справочник по имени. Передаёт name, выводит данные справочника.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.dictionaries.get_dictionary(...)
    Раздел спецификации 1.1.60: Общие справочники

HTTP-запрос
      GET /v1/getDictionary
    Параметры передаются: строка запроса.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      name: str, обязательный, тип в спецификации: string — Наименование справочника: `CardStatus`, `ContractStatus`, `Country`, `Currency`, `Goods`, `PaymentScheme`, `PaymentTerm`, `ProductGroup`, `ProductType`, `POIType`, `Region`, `Services`, `Unit`, `Office`, `POIPartner` или `DiscountScheme`.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    DictionaryResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: DictionaryData | None, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    DictionaryData:
      total_count: int, обязательное — Количество элементов в справочнике
      result: list[DictionaryItem] | None, необязательное — Список элементов справочника
    DictionaryItem:
      id: str, обязательное — Уникальный идентификатор элемента справочника
      code: str | None, необязательное — Код элемента (например, код валюты)
      value: str | None, необязательное — Значение элемента (используется в старых справочниках)
      name: str | None, необязательное — Название элемента (используется в новых справочниках)
      deleted: int | None, необязательное — Признак удаления элемента (0 — активен)
      last_update: str | None, необязательное — Дата последнего обновления записи

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
    'name': method_value('get_dictionary', 'name'),
}

DESCRIPTION = 'Получает справочник по имени. Передаёт name, выводит данные справочника.'

if __name__ == "__main__":
    run('get_dictionary', PARAMS, mutating=False, description=DESCRIPTION)
