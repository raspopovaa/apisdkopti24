"""order_invoice — Заказ счета на оплату

Что делает
    Создаёт счёт на оплату. Передаёт contract_id, amount и email, выводит envelope заявки на
    счёт.
    Изменяет данные: да. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.contracts.order_invoice(...)
    Раздел спецификации 1.1.60: Заказ счета на оплату

HTTP-запрос
      POST /v2/invoice
    Параметры передаются: тело (form).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      amount: Decimal, обязательный — Сумма счёта в рублях. В API параметр называется `sum`.
      email: str, обязательный, тип в спецификации: string — Email-адрес для отправки счёта.
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта (Можно передать в заголовке запроса, а не только в URI - строке)

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    InvoiceOrderResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: bool, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      validate_email() — RequestValidationError при недопустимом значении
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

from _common import common, decimal, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'amount': decimal(method_value('order_invoice', 'amount')),
    'email': common('email'),
    'contract_id': common('contract_id'),
}

DESCRIPTION = (
    'Создаёт счёт на оплату. Передаёт contract_id, amount и email, выводит envelope заявки на счёт.'
)

if __name__ == "__main__":
    run('order_invoice', PARAMS, mutating=True, description=DESCRIPTION)
