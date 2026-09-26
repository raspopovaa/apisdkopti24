"""get_transactions_v1 — Список последних транзакций по договору и карте

Что делает
    Получает последние транзакции v1. Передаёт contract_id, count и опциональный card_id,
    выводит список транзакций.
    Изменяет данные: нет. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.transactions.get_transactions_v1(...)
    Раздел спецификации 1.1.60: Список последних транзакций по договору и карте

HTTP-запрос
      GET /v1/transactions
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID договора
      card_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID карты
      count: int, необязательный, по умолчанию 20, тип в спецификации: uint (1..30) — Количество транзакций (если не указывать, то вернется 10 последних транзакций)

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TransactionsV1Response:
      status: ResponseStatus, обязательное — Статус ответа API
      data: TransactionsV1Data, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    TransactionsV1Data:
      total_count: int, обязательное — Общее количество транзакций
      result: list[TransactionV1] | None, необязательное — Список транзакций
    TransactionV1:
      id: str, обязательное — ID транзакции
      time: datetime.datetime, обязательное — Дата и время транзакции
      host_date: datetime.datetime, обязательное — Дата и время на хосте
      currency: str, обязательное — Код валюты (например, 810)
      card_id: str, обязательное — ID карты
      service_center: str | None, необязательное — ID сервисного центра (АЗС)
      card_number: str, обязательное — Номер карты
      base_cost: str, обязательное — Базовая стоимость транзакции
      cost: str, обязательное — Фактическая стоимость с учётом скидок
      discount: str, обязательное — Размер скидки
      discount_cost: str, обязательное — Стоимость после применения скидки
      incoming: bool, обязательное — Признак входящей транзакции
      request: RequestInfo, обязательное — Информация о типе операции
      transaction_items: list[TransactionItem] | None, необязательное — Список товаров в транзакции
    RequestInfo:
      type: str, обязательное — Тип операции (например, Advice)
      name: str, обязательное — Название операции (например, Покупка)
    TransactionItem:
      id: str, обязательное — ID позиции транзакции
      rrn: str, обязательное — Уникальный номер RRN
      product: str, обязательное — Наименование продукта (топлива)
      amount: str, обязательное — Количество продукта
      price: str, обязательное — Цена за единицу
      base_cost: str, обязательное — Базовая стоимость
      cost: str, обязательное — Итоговая стоимость с учетом скидки
      discount: str, обязательное — Скидка по позиции
      discount_cost: str, обязательное — Стоимость с учётом скидки
      transaction: str, обязательное — ID транзакции
      currency: str, обязательное — Валюта
      unit: str, обязательное — Единица измерения

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
    Повтор при сетевой ошибке: только безопасные читающие; идемпотентность: да.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'contract_id': common('contract_id'),
    'card_id': None,
    'count': 20,
}

DESCRIPTION = 'Получает последние транзакции v1. Передаёт contract_id, count и опциональный card_id, выводит список транзакций.'

if __name__ == "__main__":
    run('get_transactions_v1', PARAMS, mutating=False, description=DESCRIPTION)
