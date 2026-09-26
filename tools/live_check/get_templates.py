"""get_templates — Список шаблонов ВК

Что делает
    Получает шаблоны виртуальных карт договора. Передаёт contract_id, выводит список
    шаблонов.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: да.
    Вызов SDK: client.templates.get_templates(...)
    Раздел спецификации 1.1.60: Список шаблонов ВК

HTTP-запрос
      GET /v2/vc/templates
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если не передать, то в ответе придут все шаблоны клиента.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    TemplatesListResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: TemplatesListData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    TemplatesListData:
      total_count: int, обязательное — Общее количество найденных шаблонов
      result: list[TemplateItem] | None, необязательное — Список найденных шаблонов ВК
    TemplateItem:
      id: str, обязательное — Идентификатор шаблона ВК
      name: str, обязательное — Название шаблона ВК
      type: str, обязательное — Тип шаблона (Limit — лимитная, Wallet — электронная карта)
      contract_id: str, обязательное — Идентификатор договора, к которому относится шаблон

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
    'contract_id': common('contract_id'),
}

DESCRIPTION = (
    'Получает шаблоны виртуальных карт договора. Передаёт contract_id, выводит список шаблонов.'
)

if __name__ == "__main__":
    run('get_templates', PARAMS, mutating=False, description=DESCRIPTION)
