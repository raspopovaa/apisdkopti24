"""delete_template_restriction — Удаление ограничителя шаблона ВК

Что делает
    Удаляет товарное ограничение шаблона. Передаёт template_id и restriction_id, выводит
    bool-envelope результата.
    Изменяет данные: да. Тарификация: не указано. Демо-стенд: да.
    Вызов SDK: client.templates.delete_template_restriction(...)
    Раздел спецификации 1.1.60: Удаление ограничителя шаблона ВК

HTTP-запрос
      DELETE /v2/vc/templates/{template_id}/restrictions/{restriction_id}
      DELETE /v2/vc/templates/{template_id}/restrictions/{restrictions_id} (вариант plural_id)
      POST /v2/vc/templates/{template_id}/restrictions/{restriction_id} (вариант post_override)
    Параметры передаются: путь URL, тело (form).
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      template_id: str, обязательный — Идентификатор шаблона.
      restriction_id: str, обязательный — ID ограничителя шаблона ВК.
      use_post: bool, необязательный, по умолчанию False — описание в спецификации не найдено

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TemplateRestrictionDeleteResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: bool, обязательное — Типизированные данные ответа API
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
    Повтор при сетевой ошибке: never; идемпотентность: да.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'template_id': common('template_id'),
    'restriction_id': common('template_restriction_id'),
    'use_post': False,
}

DESCRIPTION = 'Удаляет товарное ограничение шаблона. Передаёт template_id и restriction_id, выводит bool-envelope результата.'

if __name__ == "__main__":
    run('delete_template_restriction', PARAMS, mutating=True, description=DESCRIPTION)
