"""order_report — Создать задание на формирование отчета.

Что делает
    Заказывает отчёт v2. Передаёт report_id, format, params и emails, выводит envelope
    задачи отчёта.
    Изменяет данные: да. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.reports.order_report(...)
    Раздел спецификации 1.1.60: Заказ отчета на email и по ссылке (v.2)

HTTP-запрос
      POST /v2/reports
    Параметры передаются: тело (json).
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      report_id: str, обязательный — Идентификатор отчета.
      format: str, обязательный, тип в спецификации: string — Формат отчёта; допустимые форматы приведены в поле `formats` метода получения списка доступных отчётов.
      params: dict[str, Any], обязательный, тип в спецификации: json — Параметры отчёта; набор параметров приведён в поле `parameters` метода получения списка доступных отчётов.
      emails: str | None, необязательный, по умолчанию None, тип в спецификации: [string,string] — Список email-адресов получателей отчёта.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    ReportOrderResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: ReportOrderData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    ReportOrderData:
      job_id: list[str] | None, необязательное — Идентификаторы созданных заданий на генерацию отчета

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      require_identifier() — RequestValidationError при недопустимом значении
      validate_email() — RequestValidationError при недопустимом значении
      validate_non_empty_value() — RequestValidationError при недопустимом значении
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
    'report_id': common('report_id'),
    'format': method_value('order_report', 'format'),
    'params': method_value('order_report', 'params'),
    'emails': None,
}

DESCRIPTION = 'Заказывает отчёт v2. Передаёт report_id, format, params и emails, выводит envelope задачи отчёта.'

if __name__ == "__main__":
    run('order_report', PARAMS, mutating=True, description=DESCRIPTION)
