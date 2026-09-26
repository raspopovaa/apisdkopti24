"""order_documents_email — Заказ первичных документов на почту

Что делает
    Заказывает отправку документов на email. Передаёт ids, формат и emails, выводит envelope
    результата.
    Изменяет данные: да. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.contracts.order_documents_email(...)
    Раздел спецификации 1.1.60: Заказ первичных документов на почту

HTTP-запрос
      POST /v2/documents
    Параметры передаются: тело (json).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      ids: list[str], обязательный — Список ID документов. В API параметр называется `id`.
      fmt: Literal['pdf', 'xlsx'], обязательный — Формат документа: `pdf` или `xlsx`. В API параметр называется `format`.
      emails: list[str], обязательный, тип в спецификации: json — Список email-адресов для отправки документов, не более пяти.
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    DocumentsOrderResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: bool, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      validate_document_order() — RequestValidationError при недопустимом значении
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

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'ids': method_value('order_documents_email', 'ids'),
    'fmt': method_value('order_documents_email', 'fmt'),
    'emails': method_value('order_documents_email', 'emails'),
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Заказывает отправку документов на email. Передаёт ids, формат и emails, выводит envelope результата.'

if __name__ == "__main__":
    run('order_documents_email', PARAMS, mutating=True, description=DESCRIPTION)
