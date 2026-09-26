"""get_report_jobs — Список ранее заказанных отчетов по ссылке (v.2)

Что делает
    Получает список задач отчётов v2. Передаёт только session/api context, выводит список
    задач.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.reports.get_report_jobs(...)
    Раздел спецификации 1.1.60: Список ранее заказанных отчетов по ссылке (v.2)

HTTP-запрос
      GET /v2/reports/jobs
    Параметры передаются: без параметров.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      нет параметров

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    ReportJobListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: ReportJobList, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    ReportJobList:
      total_count: int, обязательное — Количество найденных отчетов
      result: list[ReportJobItem] | None, необязательное — Список заказанных отчетов
    ReportJobItem:
      date: str, обязательное — Дата создания заказа отчета
      client_id: str, обязательное — ID клиента
      user_id: str, обязательное — ID пользователя
      contract_id: str, обязательное — ID договора
      contract_name: str | None, необязательное — Название договора
      job_id: str, обязательное — Идентификатор задания (Job ID)
      report_name: str, обязательное — Название отчета
      report_format: str, обязательное — Формат отчета (pdf, xlsx и т.д.)
      available_after: int, обязательное — Количество секунд до доступности отчета

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

DESCRIPTION = (
    'Получает список задач отчётов v2. Передаёт только session/api context, выводит список задач.'
)

if __name__ == "__main__":
    run('get_report_jobs', PARAMS, mutating=False, description=DESCRIPTION)
