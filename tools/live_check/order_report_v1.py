"""order_report_v1 — Запрос транзакционного отчета за период на email и по ссылке

Что делает
    Заказывает отчёт v1. Передаёт contract_id, период, формат и фильтры, выводит envelope
    задачи отчёта.
    Изменяет данные: да. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.reports.order_report_v1(...)
    Раздел спецификации 1.1.60: Запрос транзакционного отчета за период на email и по ссылке

HTTP-запрос
      GET /v1/reports
    Параметры передаются: строка запроса.
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str, обязательный, тип в спецификации: string — ID договора
      start: str, обязательный, тип в спецификации: string — Дата начала отчётного периода.
      end: str, обязательный, тип в спецификации: string — Дата окончания отчётного периода.
      report_format: str, обязательный, тип в спецификации: string — Формат отчёта: `xlsx`, `xml`, `pdf` или `csv`.
      email: str | None, необязательный, по умолчанию None, тип в спецификации: string — Email-адреса для отправки отчёта.
      cards_list: list[str] | None, необязательный, по умолчанию None, тип в спецификации: [string,string] — Список 16-значных номеров карт для формирования отчёта. Если список не передан, отчёт формируется по указанной группе карт либо по всем картам договора.
      group_id: list[str] | None, необязательный, по умолчанию None, тип в спецификации: [string,string] — Список ID группы карт. Если данный параметр пустой или не передан – будет сформирован отчет либо по списку карт, если указан cards_list, либо по всем картам для указанного договора
      archive: bool, необязательный, по умолчанию False — описание в спецификации не найдено

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    ReportV1OrderResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: list[str], обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      validate_date_range() — RequestValidationError при недопустимом значении
      validate_email() — RequestValidationError при недопустимом значении
      validate_identifier_list() — RequestValidationError при недопустимом значении
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
    Повтор при сетевой ошибке: только безопасные читающие; идемпотентность: да.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'contract_id': common('contract_id'),
    'start': common("date_from"),
    'end': common("date_to"),
    'report_format': method_value('order_report_v1', 'report_format'),
    'email': None,
    'cards_list': None,
    'group_id': None,
    'archive': False,
}

DESCRIPTION = 'Заказывает отчёт v1. Передаёт contract_id, период, формат и фильтры, выводит envelope задачи отчёта.'

if __name__ == "__main__":
    run('order_report_v1', PARAMS, mutating=True, description=DESCRIPTION)
