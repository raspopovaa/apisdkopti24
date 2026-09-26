"""get_template_limits — Список лимитов шаблона ВК

Что делает
    Получает лимиты шаблона. Передаёт template_id, выводит список лимитов.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.templates.get_template_limits(...)
    Раздел спецификации 1.1.60: Список лимитов шаблона ВК

HTTP-запрос
      GET /v2/vc/templates/{template_id}/limits
    Параметры передаются: путь URL.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      template_id: str, обязательный — Идентификатор шаблона.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TemplateLimitListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: TemplateLimitListData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    TemplateLimitListData:
      total_count: int, обязательное — Количество найденных лимитов
      result: list[TemplateLimit] | None, необязательное — Список лимитов шаблона
    TemplateLimit:
      id: str, обязательное — Идентификатор лимита шаблона
      template_id: str, обязательное — Идентификатор шаблона, которому принадлежит лимит
      contract_id: str, обязательное — Идентификатор договора, на который распространяется лимит
      amount: LimitAmount | None, необязательное — Объемный лимит (в литрах и т.д.)
      sum: LimitSum | None, необязательное — Суммовой лимит (в рублях и т.д.)
      time: LimitTime, обязательное — Период действия лимита
      term: LimitTerm, обязательное — Дополнительные временные ограничения
      transactions: LimitTransactions, обязательное — Информация по транзакциям лимита
      date: str, обязательное — Дата создания лимита
      productType: str, обязательное — Тип продукта (топливо, услуга и т.д.)
      productGroup: str | None, необязательное — Группа продукта (например, G-95)
      productTypeName: str, обязательное — Название типа продукта
      productGroupName: str | None, необязательное — Название группы продукта
    LimitAmount:
      unit: str, обязательное — Единица измерения (например, 'LIT')
      value: float, обязательное — Количество или объем в единицах измерения
    LimitSum:
      currency: str, обязательное — Код валюты (например, '810')
      currencyName: str | None, необязательное — Название валюты (например, 'р.')
      value: float, обязательное — Сумма лимита в указанной валюте
    LimitTime:
      type: int, обязательное — Тип периода лимита (например, 3 — день, 5 — месяц)
      number: int, обязательное — Количество единиц выбранного периода
    LimitTerm:
      days: str | None, необязательное — Маска дней действия лимита (например, '1111100')
      type: int, обязательное — Тип временного ограничения
      time: LimitTermTime | None, необязательное — Временные границы лимита
    LimitTermTime:
      from: str | None, необязательное — Начало временного диапазона (например, '03:00')
      to: str | None, необязательное — Конец временного диапазона (например, '08:00')
    LimitTransactions:
      count: int, обязательное — Количество транзакций, на которое распространяется лимит

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

DESCRIPTION = 'Получает лимиты шаблона. Передаёт template_id, выводит список лимитов.'

if __name__ == "__main__":
    run('get_template_limits', PARAMS, mutating=False, description=DESCRIPTION)
