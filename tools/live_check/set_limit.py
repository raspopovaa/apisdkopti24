"""set_limit — Установить или изменить продуктовый лимит карты.

Что делает
    Создаёт или изменяет продуктовые лимиты. Передаёт список LimitRequestItem, выводит
    envelope с ID лимитов.
    Изменяет данные: да. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.limits.set_limit(...)
    Раздел спецификации 1.1.60: Установка/Изменение продуктового лимита по карте и группе карт

HTTP-запрос
      POST /v1/setLimit
    Параметры передаются: тело (form).
    contract_id передаётся: form, header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      limits: list[LimitRequestItem], обязательный — описание в спецификации не найдено
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
    SetLimitRequest:
      limits: list[LimitRequestItem], обязательное — описание не задано
    LimitRequestItem:
      id: str | None, необязательное — ID изменяемого лимита
      contract_id: str | None, необязательное — ID договора
      card_id: str | None, необязательное — ID карты
      group_id: str | None, необязательное — ID группы карт
      productType: str | None, необязательное — ID типа продукта
      productGroup: str | None, необязательное — ID группы продуктов
      amount: LimitAmountRequest | None, необязательное — Объёмный лимит
      sum: LimitSumRequest | None, необязательное — Денежный лимит
      term: LimitTermRequest | None, необязательное — Условия действия лимита
      transactions: LimitTransactionsRequest | None, необязательное — Лимит количества транзакций
      time: LimitTimeRequest, обязательное — Период действия лимита
    LimitAmountRequest:
      unit: str, обязательное — Единица измерения
      value: float, обязательное — Размер объёмного лимита
    LimitSumRequest:
      currency: str, обязательное — Код валюты
      value: float, обязательное — Размер денежного лимита
    LimitTermRequest:
      days: str | None, необязательное — Маска дней недели
      type: Literal[1, 2, 3], обязательное — Тип применения ограничения
      time: LimitTermTimeRequest | None, необязательное — Интервал обслуживания
    LimitTermTimeRequest:
      from: str, обязательное — Начало интервала
      to: str, обязательное — Окончание интервала
    LimitTransactionsRequest:
      count: int, обязательное — Количество транзакций
    LimitTimeRequest:
      number: int, обязательное — Количество периодов
      type: Literal[2, 3, 4, 5, 6, 7], обязательное — Тип периода

Модели проверки исходящих данных (ответ API)
    SetLimitResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: list[str], обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      TypeError: limits[{index}] должен иметь тип LimitRequestItem
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
    'limits': [
        models.LimitRequestItem.model_validate(item) for item in method_value('set_limit', 'limits')
    ],
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Создаёт или изменяет продуктовые лимиты. Передаёт список LimitRequestItem, выводит envelope с ID лимитов.'

if __name__ == "__main__":
    run('set_limit', PARAMS, mutating=True, description=DESCRIPTION)
