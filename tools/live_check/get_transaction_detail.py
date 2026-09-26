"""get_transaction_detail — Получить детальную информацию об одной транзакции.

Что делает
    Получает детальную информацию по транзакции. Передаёт transaction_id и contract_id,
    выводит detail envelope.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.transactions.get_transaction_detail(...)
    Раздел спецификации 1.1.60: Данные по транзакции

HTTP-запрос
      GET /v2/transactions/{transaction_id}
    Параметры передаются: путь URL, строка запроса.
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      transaction_id: str, обязательный, тип в спецификации: uint — ID транзакции
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TransactionDetailResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: TransactionDetailData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    TransactionDetailData:
      total_count: int, обязательное — Общее количество транзакций
      result: list[TransactionDetailItem] | None, необязательное — Детали транзакции
    TransactionDetailItem:
      id: int | str, обязательное — ID транзакции
      timestamp: datetime.datetime, обязательное — Время транзакции (локальное)
      utc_time: datetime.datetime, обязательное — Время транзакции в UTC
      card_id: str, обязательное — ID карты
      poi_id: str, обязательное — ID точки продаж (АЗС)
      terminal_id: str, обязательное — ID терминала
      type: str, обязательное — Тип операции (P — покупка, R — возврат)
      product_id: str, обязательное — ID продукта
      product_name: str, обязательное — Наименование продукта
      product_category_id: str, обязательное — Категория продукта (например, НП)
      currency: str, обязательное — Код валюты (например, RUR)
      check_id: int | str, обязательное — Номер чека
      stor_transaction_id: int | str | None, обязательное — ID сторнируемой транзакции
      is_storno: bool, обязательное — Признак сторно
      is_manual_correction: bool, обязательное — Признак ручной корректировки
      qty: int | float, обязательное — Количество
      price: float | str, обязательное — Цена за единицу
      price_no_discount: float | str, обязательное — Цена без скидки
      sum: float | str, обязательное — Сумма с учетом скидки
      sum_no_discount: float | str, обязательное — Сумма без скидки
      discount: float | str, обязательное — Размер скидки
      exchange_rate: float | str, обязательное — Курс обмена
      card_number: str, обязательное — Номер карты
      payment_type: str, обязательное — Тип оплаты (например, Карта)
      date: str, обязательное — Дата транзакции

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
    'transaction_id': common('transaction_id'),
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Получает детальную информацию по транзакции. Передаёт transaction_id и contract_id, выводит detail envelope.'

if __name__ == "__main__":
    run('get_transaction_detail', PARAMS, mutating=False, description=DESCRIPTION)
