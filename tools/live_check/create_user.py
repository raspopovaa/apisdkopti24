"""create_user — Создание водителя без персональных данных

Что делает
    Создаёт пользователя. Передаёт uuid и mobile, выводит envelope с ID/результатом
    создания.
    Изменяет данные: да. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.users.create_user(...)
    Раздел спецификации 1.1.60: Создание водителя без персональных данных

HTTP-запрос
      POST /v2/users
    Параметры передаются: тело (form).
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      uuid: str, обязательный, тип в спецификации: string — Внутренний ID водителя в системе клиента.
      mobile: str, обязательный, тип в спецификации: string — Телефон водителя, используемый как логин.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    UserCreateResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: str, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок

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
    Повтор при сетевой ошибке: never; идемпотентность: нет.
"""

from _common import common, method_value, run  # noqa: F401

# Значения берутся из test_data.json: common — общие данные, methods — данные метода,
# overrides — замена любого параметра ниже. Файл создаётся генератором
# (tools/live_check/_generate.py): меняйте значения в test_data.json, а не здесь.
PARAMS = {
    'uuid': method_value('create_user', 'uuid'),
    'mobile': method_value('create_user', 'mobile'),
}

DESCRIPTION = (
    'Создаёт пользователя. Передаёт uuid и mobile, выводит envelope с ID/результатом создания.'
)

if __name__ == "__main__":
    run('create_user', PARAMS, mutating=True, description=DESCRIPTION)
