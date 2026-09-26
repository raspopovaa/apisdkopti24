"""get_cards_v1 — Получить список топливных карт через API v1.

Что делает
    Получает список карт v1. Передаёт contract_id и cache, выводит список карт.
    Изменяет данные: нет. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.cards.get_cards_v1(...)
    Раздел спецификации 1.1.60: Список топливных карт (Процессинг)

HTTP-запрос
      GET /v1/cards
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта
      cache: bool, необязательный, по умолчанию True, тип в спецификации: bool — Кеш карт. false или не задан - данные берутся по прямому запросу из процессинга.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    CardsListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: CardsListData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    CardsListData:
      total_count: int, обязательное — Общее количество найденных карт
      result: list[CardInfo] | None, необязательное — Список найденных карт
    CardInfo:
      id: str, обязательное — Уникальный идентификатор карты
      contract_id: str, обязательное — Идентификатор договора
      number: str, обязательное — Номер топливной карты
      status: str, обязательное — Статус карты (например, Active, Locked(Client))
      can_work_offline: bool, обязательное — Может ли карта работать офлайн
      card_auth_type: str, обязательное — Тип авторизации карты (например, PIN)
      comment: str | None, необязательное — Комментарий к карте
      date_expired: datetime.datetime, обязательное — Дата истечения срока действия карты
      date_last_usage: datetime.datetime | None, необязательное — Дата последнего использования карты
      date_released: datetime.datetime | None, необязательное — Дата выпуска карты
      servicecenter_last_usage_name: str | None, необязательное — Название последней АЗС, где использовалась карта
      transaction_last_detail: str | None, необязательное — Информация о последней транзакции
      transaction_timeout: TransactionTimeout | None, необязательное — Таймаут последней транзакции
      product: str, обязательное — Тип продукта (limit/wallet)
      payment_of_tolls: str, обязательное — Оплата платных дорог ('Y' или 'N')
    TransactionTimeout:
      type: int | str | None, обязательное — Тип таймаута ('H', 'N' или числовое значение)
      value: int | str, обязательное — Значение таймаута

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
    'cache': True,
}

DESCRIPTION = 'Получает список карт v1. Передаёт contract_id и cache, выводит список карт.'

if __name__ == "__main__":
    run('get_cards_v1', PARAMS, mutating=False, description=DESCRIPTION)
