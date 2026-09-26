"""get_reports — Список доступных отчетов (v.2)

Что делает
    Получает список доступных отчётов v2. Передаёт только session/api context, выводит
    список отчётов.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.reports.get_reports(...)
    Раздел спецификации 1.1.60: Список доступных отчетов (v.2)

HTTP-запрос
      GET /v2/reports
    Параметры передаются: без параметров.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      нет параметров

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    ReportListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: ReportList, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    ReportList:
      total_count: int, обязательное — Количество доступных отчетов
      result: list[ReportItem] | None, необязательное — Массив отчетов
    ReportItem:
      id: str, обязательное — Идентификатор отчета
      name: str, обязательное — Название отчета
      formats: list[str], обязательное — Список поддерживаемых форматов (pdf, xlsx, csv и т.д.)
      parameters: list[ReportParameter], обязательное — Список параметров отчета
    ReportParameter:
      name: str, обязательное — Имя параметра, используемое в запросах
      value: str | None, необязательное — Значение параметра
      label: str | None, обязательное — Отображаемое название параметра; реальный API может вернуть null
      default_value: str | None, необязательное — Значение по умолчанию
      menu_values: list[ReportParameterMenuValue] | None, необязательное — Список возможных значений для выбора из меню
      type: str, обязательное — Тип параметра (например, date, Contract, Group)
    ReportParameterMenuValue:
      labels: str | None, необязательное — Отображаемое имя пункта меню
      values: str | None, необязательное — Значение пункта меню

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
PARAMS: dict = {}

DESCRIPTION = 'Получает список доступных отчётов v2. Передаёт только session/api context, выводит список отчётов.'

if __name__ == "__main__":
    run('get_reports', PARAMS, mutating=False, description=DESCRIPTION)
