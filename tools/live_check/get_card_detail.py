"""get_card_detail — Получить детальную информацию о топливной карте.

Что делает
    Получает детальную информацию по карте. Передаёт card_id и contract_id, выводит card
    detail envelope.
    Изменяет данные: нет. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.cards.get_card_detail(...)
    Раздел спецификации 1.1.60: Детальная информация по карте

HTTP-запрос
      GET /v1/cards
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      card_id: str, обязательный, тип в спецификации: string — ID карты
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    CardDetailResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: CardDetailData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    CardDetailData:
      total_count: int, обязательное — Количество записей
      result: list[CardDetail] | None, необязательное — Список карт
    CardDetail:
      id: str, обязательное — Идентификатор карты
      contract_id: str, обязательное — ID договора
      number: str, обязательное — Номер карты
      status: str, обязательное — Статус карты
      can_work_offline: bool, обязательное — Может работать офлайн
      card_auth_type: str, обязательное — Тип аутентификации карты
      comment: str | None, необязательное — Комментарий к карте
      date_last_usage: datetime.datetime | str | None, необязательное — Дата последнего использования (может быть пустой строкой)
      date_released: datetime.datetime | str | None, необязательное — Дата выпуска карты
      servicecenter_last_usage_name: str | None, необязательное — Название АЗС последнего использования
      transaction_timeout: TransactionTimeout | None, необязательное — Таймаут транзакции
      product: str, обязательное — Тип продукта (limit/wallet)
      carrier: str, обязательное — Тип карты (Plastic/Virtual)
      available: str, обязательное — Доступный лимит или баланс
      currency: str, обязательное — Валюта
      payment_of_tolls: str, обязательное — Признак оплаты дорожных сборов
      mpc: bool, обязательное — Признак доступности мобильного профиля карты
      pin_reset: int, обязательное — Количество доступных попыток сброса PIN
      pin_counter: int, обязательное — Счётчик попыток ввода PIN
      previous: str | None, необязательное — ID предыдущей карты
      next: str | None, необязательное — ID следующей карты
    TransactionTimeout:
      type: int | str | None, обязательное — Тип таймаута ('H', 'N' или числовое значение)
      value: int | str, обязательное — Значение таймаута

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
    'card_id': common('card_id'),
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Получает детальную информацию по карте. Передаёт card_id и contract_id, выводит card detail envelope.'

if __name__ == "__main__":
    run('get_card_detail', PARAMS, mutating=False, description=DESCRIPTION)
