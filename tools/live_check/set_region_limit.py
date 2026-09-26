"""set_region_limit — Установка/Изменение регионального лимита по карте и группе карт

Что делает
    Создаёт или изменяет региональные лимиты. Передаёт список RegionLimitRequestItem,
    выводит envelope с ID лимитов.
    Изменяет данные: да. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.region_limits.set_region_limit(...)
    Раздел спецификации 1.1.60: Установка/Изменение регионального лимита по карте и группе карт

HTTP-запрос
      POST /v1/setRegionLimit
    Параметры передаются: тело (form).
    contract_id передаётся: form, header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      region_limits: list[RegionLimitRequestItem], обязательный — Массив параметров регионального лимита: ID лимита, карты, группы и договора, страна, регион, АЗС, партнёр и `limit_type` (`1` — разрешающий, `2` — запрещающий).
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
    RegionLimitRequestItem:
      id: str | None, необязательное — ID регионального лимита при изменении существующей записи
      contract_id: str | None, необязательное — ID договора
      card_id: str | None, необязательное — ID карты
      group_id: str | None, необязательное — ID группы карт
      country: str, обязательное — Код страны обслуживания
      region: str | None, необязательное — Код региона обслуживания
      service_center: str | None, необязательное — ID точки обслуживания
      partner: str | None, необязательное — ID партнёра
      limit_type: Literal[1, 2], обязательное — Тип лимита: 1 — разрешающий, 2 — запрещающий

Модели проверки исходящих данных (ответ API)
    RegionLimitSetResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: list[str] | None, необязательное — ID сохранённых региональных лимитов
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      validate_card_or_group_target() — RequestValidationError при недопустимом значении
      validate_model_sequence() — RequestValidationError при недопустимом значении
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

from _common import common, method_value, models, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'region_limits': [
        models.RegionLimitRequestItem.model_validate(item)
        for item in method_value('set_region_limit', 'region_limits')
    ],
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Создаёт или изменяет региональные лимиты. Передаёт список RegionLimitRequestItem, выводит envelope с ID лимитов.'

if __name__ == "__main__":
    run('set_region_limit', PARAMS, mutating=True, description=DESCRIPTION)
