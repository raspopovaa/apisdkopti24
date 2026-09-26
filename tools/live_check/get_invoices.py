"""get_invoices — Счета на оплату

Что делает
    Получает счета договора. Передаёт contract_id, выводит список счетов.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.contracts.get_invoices(...)
    Раздел спецификации 1.1.60: Счета на оплату

HTTP-запрос
      GET /v2/invoices
    Параметры передаются: без параметров.
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта (Можно передать в заголовке запроса, а не только в URI - строке)

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    InvoicesResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: InvoicesData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    InvoicesData:
      total_count: int, обязательное — Количество найденных счетов
      result: list[InvoiceItem] | None, необязательное — Список счетов на оплату
    InvoiceItem:
      id: str, обязательное — Уникальный идентификатор счёта
      contract_id: str, обязательное — ID договора, к которому относится счёт
      ref_number: str, обязательное — Номер счёта, указанный в системе
      date_start: str, обязательное — Дата начала периода счёта (YYYY-MM-DD)
      date_end: int | str, обязательное — Дата окончания периода счёта
      last_update: float | str, обязательное — Дата и время последнего обновления счёта (ISO формат)
      currency: float | str, обязательное — Код валюты, например '810'
      amount: float | str, обязательное — Сумма счёта
      paid_amount: str, обязательное — Оплаченная сумма
      status: str, обязательное — Статус счёта, например 'OPEN' или 'PAID'
      comment: str | None, необязательное — Комментарий к счёту, например 'Intermediate Invoice'

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

DESCRIPTION = 'Получает счета договора. Передаёт contract_id, выводит список счетов.'

if __name__ == "__main__":
    run('get_invoices', PARAMS, mutating=False, description=DESCRIPTION)
