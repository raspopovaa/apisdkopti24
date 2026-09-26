"""get_template_georestrictions — Список геоограничителей шаблона ВК

Что делает
    Получает геоограничения шаблона. Передаёт template_id, выводит список геоограничений.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.templates.get_template_georestrictions(...)
    Раздел спецификации 1.1.60: Список геоограничителей шаблона ВК

HTTP-запрос
      GET /v2/vc/templates/{template_id}/georestrictions
    Параметры передаются: путь URL.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      template_id: str, обязательный — Идентификатор шаблона.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TemplateGeoRestrictionListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: TemplateGeoRestrictionListData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    TemplateGeoRestrictionListData:
      total_count: int, обязательное — Количество найденных геоограничителей
      result: list[TemplateGeoRestriction] | None, необязательное — Список геоограничителей шаблона
    TemplateGeoRestriction:
      id: str, обязательное — Идентификатор геоограничителя шаблона
      template_id: str, обязательное — Идентификатор шаблона
      contract_id: str, обязательное — Идентификатор договора
      date: str, обязательное — Дата создания записи
      country: str, обязательное — Код страны (например, 'RUS')
      countryName: str, обязательное — Название страны
      region: str | None, необязательное — Код региона
      regionName: str | None, необязательное — Название региона
      partner: str | None, необязательное — Код партнера (АЗС)
      partnerName: str | None, необязательное — Название партнера (АЗС)
      service_center: str | None, необязательное — Код сервисного центра
      service_centerName: str | None, необязательное — Название сервисного центра
      restriction_type: int, обязательное — Тип геоограничителя (1 — разрешение, 2 — запрет)

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
    'Получает геоограничения шаблона. Передаёт template_id, выводит список геоограничений.'
)

if __name__ == "__main__":
    run('get_template_georestrictions', PARAMS, mutating=False, description=DESCRIPTION)
