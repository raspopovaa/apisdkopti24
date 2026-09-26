"""set_restriction — Установка/Изменение товарного ограничителя по карте и группе карт

Что делает
    Создаёт или изменяет товарные ограничители. Передаёт список RestrictionRequestItem,
    выводит envelope с ID ограничителей.
    Изменяет данные: да. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.restrictions.set_restriction(...)
    Раздел спецификации 1.1.60: Установка/Изменение товарного ограничителя по карте и группе карт

HTTP-запрос
      POST /v1/setRestriction
    Параметры передаются: тело (form).
    contract_id передаётся: form, header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      restrictions: list[RestrictionRequestItem], обязательный — Массив параметров товарного ограничителя: ID ограничителя, карты, группы и договора, группа и тип продукта, а также `restriction_type` (`1` — разрешающий, `2` — запрещающий).
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
    RestrictionRequestItem:
      id: str | None, необязательное — ID изменяемого ограничителя
      contract_id: str | None, необязательное — ID договора
      card_id: str | None, необязательное — ID карты
      group_id: str | None, необязательное — ID группы карт
      productType: str, обязательное — ID типа продукта
      productGroup: str | None, необязательное — ID группы продуктов
      restriction_type: Literal[1, 2], обязательное — Тип ограничителя: 1 — разрешающий, 2 — запрещающий

Модели проверки исходящих данных (ответ API)
    RestrictionSetResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: list[str], обязательное — Типизированные данные ответа API
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
    'restrictions': [
        models.RestrictionRequestItem.model_validate(item)
        for item in method_value('set_restriction', 'restrictions')
    ],
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Создаёт или изменяет товарные ограничители. Передаёт список RestrictionRequestItem, выводит envelope с ID ограничителей.'

if __name__ == "__main__":
    run('set_restriction', PARAMS, mutating=True, description=DESCRIPTION)
