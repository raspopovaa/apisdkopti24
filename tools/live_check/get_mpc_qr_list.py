"""get_mpc_qr_list — Получить список выпущенных мобильных профилей карт.

Что делает
    Получает список MPC/QR. Передаёт только session/api context, выводит список MPC.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.virtual_cards.get_mpc_qr_list(...)

HTTP-запрос
      GET /v2/MPC
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None — Идентификатор договора. Для части методов может быть получен из активного контекста SDK.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    MPCListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: MPCListData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    MPCListData:
      total_count: int, обязательное — Количество найденных МПК
      result: list[MPCItem], обязательное — Список выпущенных МПК
    MPCItem:
      _id: str, обязательное — ID записи МПК
      client_id: str, обязательное — ID клиента
      user_id: str, обязательное — ID пользователя
      login: str, обязательное — Логин пользователя
      role: str, обязательное — Роль пользователя
      contract_id: str, обязательное — ID договора
      card_id: str, обязательное — ID топливной карты
      card_number: str, обязательное — Номер топливной карты
      device_id: str, обязательное — ID устройства
      device_name: str, обязательное — Название устройства
      tries: int, обязательное — Максимальное число попыток оплаты
      transaction_count: int, обязательное — Число проведённых транзакций
      use_mpc: bool, обязательное — Признак работоспособности МПК
      updated_at: str | None, необязательное — Время обновления записи
      created_at: str, обязательное — Время создания записи

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
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Получает список MPC/QR. Передаёт только session/api context, выводит список MPC.'

if __name__ == "__main__":
    run('get_mpc_qr_list', PARAMS, mutating=False, description=DESCRIPTION)
