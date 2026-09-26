"""reset_mpc — Сбросить блокировку выпуска или оплаты по МПК.

Что делает
    Сбрасывает MPC/QR состояние карты. Передаёт card_id и type_, выводит envelope
    результата.
    Изменяет данные: да. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.virtual_cards.reset_mpc(...)

HTTP-запрос
      POST /v2/cards/{card_id}/resetMPC
    Параметры передаются: путь URL, тело (form).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      card_id: str, обязательный — Идентификатор топливной карты.
      type_: str, необязательный, по умолчанию 'ResetCounterCode' — `ResetCounterCode` сбрасывает блокировку оплаты, `ResetCounterMPC` — блокировку выпуска МПК.
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
    MPCResetRequest:
      type: Literal['ResetCounterCode', 'ResetCounterMPC'], необязательное — описание не задано

Модели проверки исходящих данных (ответ API)
    ResetMPCResponse:
      status: StatusModel, обязательное — Статус выполнения операции сброса
      data: bool, обязательное — Результат операции (True — успешно)
      timestamp: int, обязательное — Время выполнения запроса (Unix Timestamp)
    StatusModel:
      code: int, обязательное — Код статуса ответа (200 — успешно, иное — ошибка)
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок операции

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
    'type_': 'ResetCounterCode',
    'contract_id': common('contract_id'),
}

DESCRIPTION = (
    'Сбрасывает MPC/QR состояние карты. Передаёт card_id и type_, выводит envelope результата.'
)

if __name__ == "__main__":
    run('reset_mpc', PARAMS, mutating=True, description=DESCRIPTION)
