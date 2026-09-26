"""update_template_georestriction — Изменение геоограничителя шаблона ВК

Что делает
    Изменяет геоограничение шаблона. Передаёт template_id, georestriction_id и payload JSON,
    выводит envelope результата.
    Изменяет данные: да. Тарификация: не указано. Демо-стенд: да.
    Вызов SDK: client.templates.update_template_georestriction(...)
    Раздел спецификации 1.1.60: Изменение геоограничителя шаблона ВК

HTTP-запрос
      POST /v2/vc/templates/{template_id}/georestrictions/{georestriction_id}
      PUT /v2/vc/templates/{template_id}/georestrictions/{georestriction_id} (вариант put)
      PUT /v2/vc/templates/{template_id}/georestrictions/{georestrictions_id} (вариант put_plural_id)
    Параметры передаются: путь URL, тело (json).
    contract_id передаётся: header, json.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      template_id: str, обязательный — Идентификатор шаблона.
      georestriction_id: str, обязательный — ID геоограничителя шаблона ВК.
      payload: TemplateGeoRestrictionCreateRequest | Mapping[str, Any], обязательный — Изменяемые параметры геоограничителя: `country`, `region`, `partner`, `service_center`, `restriction_type`; `contract_id` изменить нельзя.
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID договора (Изменить нельзя)
      use_post: bool, необязательный, по умолчанию True — описание в спецификации не найдено

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TemplateGeoRestrictionCreateResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: str, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

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
    Повтор при сетевой ошибке: never; идемпотентность: нет.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'template_id': common('template_id'),
    'georestriction_id': common('template_georestriction_id'),
    'payload': method_value('update_template_georestriction', 'payload'),
    'contract_id': common('contract_id'),
    'use_post': True,
}

DESCRIPTION = 'Изменяет геоограничение шаблона. Передаёт template_id, georestriction_id и payload JSON, выводит envelope результата.'

if __name__ == "__main__":
    run('update_template_georestriction', PARAMS, mutating=True, description=DESCRIPTION)
