"""update_mpc — Перевыпустить ключи МПК и при необходимости изменить PIN.

Что делает
    Обновляет MPC/QR payload карты. Передаёт card_id, текущий PIN и необязательный новый
    PIN.
    Изменяет данные: да. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.virtual_cards.update_mpc(...)

HTTP-запрос
      POST /v2/cards/{card_id}/updateMPC
    Параметры передаются: путь URL, тело (form).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      card_id: str, обязательный — Идентификатор топливной карты.
      pin: str, обязательный — Текущий PIN мобильного профиля из 4–8 цифр.
      new_pin: str | None, необязательный, по умолчанию None — Новый PIN из 4–8 цифр. Если не передан, API перевыпускает ключи оплаты без смены PIN.
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
    MPCUpdateRequest:
      pin: str, обязательное — описание не задано
      new_pin: str | None, необязательное — описание не задано

Модели проверки исходящих данных (ответ API)
    MPCActionResponse:
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
    Повтор при сетевой ошибке: never; идемпотентность: нет.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'card_id': common("mpc_card_id"),
    'pin': method_value('update_mpc', 'pin'),
    'new_pin': None,
    'contract_id': common('contract_id'),
}

DESCRIPTION = (
    'Обновляет MPC/QR payload карты. Передаёт card_id, текущий PIN и необязательный новый PIN.'
)

if __name__ == "__main__":
    run('update_mpc', PARAMS, mutating=True, description=DESCRIPTION)
