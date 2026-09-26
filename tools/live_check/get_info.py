"""get_info — Статистика

Что делает
    Получает информацию о клиенте и тарифных запросах. Передаёт period при необходимости,
    выводит envelope client_info.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.auth.get_info(...)
    Раздел спецификации 1.1.60: Статистика

HTTP-запрос
      GET /v1/info
    Параметры передаются: строка запроса.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      period: str | None, необязательный, по умолчанию None, тип в спецификации: string — Период: месяц в формате `YYYY-MM` или конкретный день в формате `YYYY-MM-DD`.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    GetInfoResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: InfoData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    InfoData:
      from: datetime.datetime, обязательное — Начало периода статистики
      to: datetime.datetime, обязательное — Конец периода статистики
      client_info: ClientInfo, обязательное — Информация о клиенте
      methods: MethodsCount, обязательное — Количество вызовов по категориям
      methods_info: MethodsInfo, обязательное — Описание доступных методов API
    ClientInfo:
      Client: str, обязательное — ID клиента
      ClientType: str, обязательное — Тип клиента (например, D)
      Contract: str | None, необязательное — ID контракта
      ContractName: str | None, необязательное — Название контракта
      PricePlan: str | None, необязательное — Тарифный план
      Cost: int | float | None, необязательное — Стоимость запросов
      Queries: int | None, необязательное — Количество запросов
      Additional: int | None, необязательное — Дополнительное значение
    MethodsCount:
      all: int, обязательное — Общее количество методов
      cards: int | None, необязательное — Методы, связанные с картами
      cardgroups: int | None, необязательное — Методы, связанные с группами карт
      card: int | None, необязательное — Методы, связанные с одной картой
    MethodsInfo:
      actions_bill: dict[str, str], обязательное — Платные методы API (влияют на статистику)
      actions_not_bill: dict[str, str], обязательное — Бесплатные методы API (не влияют на статистику)

Возможные ошибки
    До отправки запроса (локальные проверки SDK):
      специальных проверок нет
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
    'period': None,
}

DESCRIPTION = 'Получает информацию о клиенте и тарифных запросах. Передаёт period при необходимости, выводит envelope client_info.'

if __name__ == "__main__":
    run('get_info', PARAMS, mutating=False, description=DESCRIPTION)
