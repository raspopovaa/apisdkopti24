"""get_documents — Список первичных документов по договору за период

Что делает
    Получает список документов договора. Передаёт contract_id, date_start, date_end и
    пагинацию, выводит список документов.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.contracts.get_documents(...)
    Раздел спецификации 1.1.60: Список первичных документов по договору за период

HTTP-запрос
      GET /v2/documents
    Параметры передаются: строка запроса.
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      date_start: str, обязательный, тип в спецификации: string — Дата начала периода в формате `YYYY-MM-DD`.
      date_end: str, обязательный, тип в спецификации: string — Дата окончания периода в формате `YYYY-MM-DD`.
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта (Можно передать в заголовке запроса, а не только в URI - строке)
      page: int, необязательный, по умолчанию 1, тип в спецификации: string — Номер страницы (Пагинация)
      on_page: int, необязательный, по умолчанию 10, тип в спецификации: string — Количество элементов на странице.

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    DocumentsResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: DocumentsData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    DocumentsData:
      total_count: int, обязательное — Количество найденных документов
      result: list[DocumentItem] | None, необязательное — Список найденных документов
    DocumentItem:
      id: str, обязательное — Уникальный идентификатор документа (UUID)
      name: str, обязательное — Название документа, например 'УПД'
      name_doc: str | None, необязательное — Системное имя документа, например 'СчетФактураВыданный'
      number: str, обязательное — Номер документа, например 'CSC0000000533998'
      date: int, обязательное — Дата документа в формате UNIX timestamp
      total: float, обязательное — Общая сумма документа
      vat: float, обязательное — Сумма НДС
      sum: float, обязательное — Сумма без НДС
      currency: str, обязательное — Валюта документа, например 'руб.'
      consignee: str | None, необязательное — Грузополучатель (организация)
      contract_id: str, обязательное — ID договора, к которому относится документ
      contract_name: str, обязательное — Номер или название договора

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
    'date_start': common("date_from"),
    'date_end': common("date_to"),
    'contract_id': common('contract_id'),
    'page': 1,
    'on_page': 10,
}

DESCRIPTION = 'Получает список документов договора. Передаёт contract_id, date_start, date_end и пагинацию, выводит список документов.'

if __name__ == "__main__":
    run('get_documents', PARAMS, mutating=False, description=DESCRIPTION)
