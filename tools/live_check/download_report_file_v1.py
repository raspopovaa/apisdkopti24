"""download_report_file_v1 — Генерация файла отчета

Что делает
    Скачивает файл отчёта v1. Передаёт job_id и archive, выводит размер bytes-ответа.
    Изменяет данные: нет. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.reports.download_report_file_v1(...)
    Раздел спецификации 1.1.60: Генерация файла отчета

HTTP-запрос
      GET /v1/getReportFile
    Параметры передаются: строка запроса.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      job_id: str, обязательный, тип в спецификации: string — Job_ID отчета
      archive: bool, необязательный, по умолчанию False, тип в спецификации: bool — Архивировать отчёт в ZIP.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
      ответ — файл (bytes); модель не применяется

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
    'job_id': common('job_id'),
    'archive': False,
}

DESCRIPTION = 'Скачивает файл отчёта v1. Передаёт job_id и archive, выводит размер bytes-ответа.'

if __name__ == "__main__":
    run('download_report_file_v1', PARAMS, mutating=False, description=DESCRIPTION)
