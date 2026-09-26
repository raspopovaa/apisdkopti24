"""get_final_prices — Получение финальных цен на АЗС по карте

Что делает
    Рассчитывает финальные цены для карты и точки продаж. Передаёт card_id, poi_id и список
    goods, выводит envelope цен.
    Изменяет данные: нет. Тарификация: нет. Демо-стенд: нет.
    Вызов SDK: client.final_prices.get_final_prices(...)
    Раздел спецификации 1.1.60: Получение финальных цен на АЗС по карте

HTTP-запрос
      POST /v2/cards/{card_id}/calculatePrices
    Параметры передаются: путь URL, тело (form).
    contract_id передаётся: header.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      card_id: str, обязательный — Идентификатор топливной карты.
      poi_id: str, обязательный, тип в спецификации: string — ID точки обслуживания.
      goods: list[str], обязательный, тип в спецификации: array — Массив идентификаторов продуктов.
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID договора (Можно передать в заголовке запроса, а не только в URI - строке)

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    FinalPricesResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: FinalPricesData, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    FinalPricesData:
      total_count: int, обязательное — Количество товарных позиций в ответе
      goods: list[FinalPriceItem], обязательное — Список товарных позиций с рассчитанными финальными ценами
    FinalPriceItem:
      code: str, обязательное — Код товарной позиции
      price: float, обязательное — Финальная цена товара (с учетом всех скидок и тарифов)

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
    'card_id': common('card_id'),
    'poi_id': common('poi_id'),
    'goods': [common("goods_code")],
    'contract_id': common('contract_id'),
}

DESCRIPTION = 'Рассчитывает финальные цены для карты и точки продаж. Передаёт card_id, poi_id и список goods, выводит envelope цен.'

if __name__ == "__main__":
    run('get_final_prices', PARAMS, mutating=False, description=DESCRIPTION)
