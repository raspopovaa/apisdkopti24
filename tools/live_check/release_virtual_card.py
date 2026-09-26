"""release_virtual_card — Выпустить виртуальную карту по типу или шаблону.

Что делает
    Выпускает виртуальную карту по типу/шаблону/пользователю. Передаёт type_, template_id и
    user_id, выводит envelope виртуальной карты.
    Изменяет данные: да. Тарификация: да. Демо-стенд: нет.
    Вызов SDK: client.virtual_cards.release_virtual_card(...)
    Раздел спецификации 1.1.60: Запрос на выпуск виртуальной карты (v.2)

HTTP-запрос
      POST /v2/cards/release
    Параметры передаются: тело (form).
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      type_: str | None, необязательный, по умолчанию None — Тип карты: `limit` — лимитная схема, `wallet` — электронный кошелёк. Обязателен, если не указан `template_id`; не передаётся, если указан `template_id`.
      template_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID шаблона ВК Обязателен, если не указан type - Тип карты Не указывать, если указан type - Тип карты
      user_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID пользователя (Если указан, то выпущенная карта будет привязана к указанному клиенту)

Модели проверки входящих данных (запрос)
    VirtualCardReleaseRequest:
      type: Optional[Literal['limit', 'wallet']], необязательное — описание не задано
      template_id: Optional[Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)]], необязательное — описание не задано
      user_id: Optional[Annotated[str, StringConstraints(strip_whitespace=True, to_upper=None, to_lower=None, strict=None, min_length=1, max_length=None, pattern=None, ascii_only=None)]], необязательное — описание не задано

Модели проверки исходящих данных (ответ API)
    VirtualCardResponse:
      status: StatusModel, обязательное — Статус ответа от сервера
      data: VirtualCardData, обязательное — Информация о выпущенной виртуальной карте
      timestamp: int | None, необязательное — Время ответа сервера в формате Unix Timestamp
    StatusModel:
      code: int, обязательное — Код статуса ответа (200 — успешно, иное — ошибка)
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок операции
    VirtualCardData:
      id: str, обязательное — ID виртуальной карты
      number: str | None, необязательное — Номер виртуальной карты
      carrier: str | None, необязательное — Тип носителя, обычно 'Virtual Card'
      product: str | None, необязательное — Тип продукта карты ('wallet' или 'limit')
      status: str | None, необязательное — Статус карты (например, 'Active', 'Blocked', 'Pending')

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
    'type_': None,
    'template_id': None,
    'user_id': None,
}

DESCRIPTION = 'Выпускает виртуальную карту по типу/шаблону/пользователю. Передаёт type_, template_id и user_id, выводит envelope виртуальной карты.'

if __name__ == "__main__":
    run('release_virtual_card', PARAMS, mutating=True, description=DESCRIPTION)
