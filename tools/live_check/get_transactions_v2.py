"""get_transactions_v2 — Получить транзакции договора за заданный период.

Что делает
    Получает транзакции договора v2. Передаёт contract_id, период и пагинацию, выводит
    страницу транзакций.
    Изменяет данные: нет. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.transactions.get_transactions_v2(...)
    Раздел спецификации 1.1.60: Список транзакций по договору (v.2)

HTTP-запрос
      GET /v2/transactions
    Параметры передаются: строка запроса.
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.
      date_from: str, обязательный, тип в спецификации: string — Начало периода транзакций
      date_to: str, обязательный, тип в спецификации: string — Окончание периода транзакций
      page_limit: int, необязательный, по умолчанию 100, тип в спецификации: uint — Количество транзакций на странице. 500, если не указано.
      page_offset: int, необязательный, по умолчанию 0, тип в спецификации: uint — Количество транзакций, которые пропускаются

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TransactionsV2Response:
      status: ResponseStatus, обязательное — Статус ответа API
      data: TransactionsV2Data, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    TransactionsV2Data:
      total_count: int, обязательное — Общее количество транзакций
      result: list[TransactionItemV2] | None, необязательное — Список транзакций (v2)
    TransactionItemV2:
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

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      validate_month_span() — RequestValidationError при недопустимом значении
      validate_offset_pagination() — RequestValidationError при недопустимом значении
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
    'date_from': common('date_from'),
    'date_to': common('date_to'),
    'page_limit': 100,
    'page_offset': 0,
}

DESCRIPTION = 'Получает транзакции договора v2. Передаёт contract_id, период и пагинацию, выводит страницу транзакций.'

if __name__ == "__main__":
    run('get_transactions_v2', PARAMS, mutating=False, description=DESCRIPTION)
