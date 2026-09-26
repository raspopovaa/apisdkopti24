"""get_template_restrictions — Список ограничителей шаблона ВК

Что делает
    Получает товарные ограничения шаблона. Передаёт template_id, выводит список ограничений.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.templates.get_template_restrictions(...)
    Раздел спецификации 1.1.60: Список ограничителей шаблона ВК

HTTP-запрос
      GET /v2/vc/templates/{template_id}/restrictions
    Параметры передаются: путь URL.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      template_id: str, обязательный — Идентификатор шаблона.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TemplateRestrictionListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: TemplateRestrictionListData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    TemplateRestrictionListData:
      total_count: int, обязательное — Количество найденных ограничителей
      result: list[TemplateRestriction] | None, необязательное — Список ограничителей шаблона
    TemplateRestriction:
      id: str, обязательное — Идентификатор ограничителя шаблона
      template_id: str, обязательное — Идентификатор шаблона
      contract_id: str, обязательное — Идентификатор договора
      date: str, обязательное — Дата создания ограничителя
      productType: str, обязательное — Тип продукта
      productGroup: str | None, необязательное — Группа продукта
      productTypeName: str, обязательное — Название типа продукта
      productGroupName: str | None, необязательное — Название группы продукта
      restriction_type: int, обязательное — Тип ограничителя (1 — разрешение, 2 — запрет)

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
    'template_id': common('template_id'),
}

DESCRIPTION = (
    'Получает товарные ограничения шаблона. Передаёт template_id, выводит список ограничений.'
)

if __name__ == "__main__":
    run('get_template_restrictions', PARAMS, mutating=False, description=DESCRIPTION)
