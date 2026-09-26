"""get_contract_data — Данные по договору

Что делает
    Получает данные договора. Передаёт contract_id, выводит баланс, параметры договора,
    менеджера и статистику карт.
    Изменяет данные: нет. Тарификация: да. Демо-стенд: да.
    Вызов SDK: client.contracts.get_contract_data(...)
    Раздел спецификации 1.1.60: Данные по договору

HTTP-запрос
      GET /v1/getPartContractData
    Параметры передаются: строка запроса.
    contract_id передаётся: header, query.
    Заголовки: api_key, date_time, session_id (после авторизации).

Параметры метода SDK
      contract_id: str | None, необязательный, по умолчанию None, тип в спецификации: string — ID контракта

Модели проверки входящих данных (запрос)
      отдельной модели нет: параметры проверяются сигнатурой и проверками метода

Модели проверки исходящих данных (ответ API)
    ContractDataResponse:
      status: ResponseStatus, обязательное — Статус ответа API
      data: ContractResponse, обязательное — Типизированные данные ответа API
      timestamp: int | None, необязательное — Метка времени ответа API
    ResponseStatus:
      code: int, обязательное — Код выполнения API-операции
      message: str | None, необязательное — Текст статуса API-операции
      errors: list[dict[str, object]] | None, необязательное — Массив ошибок; отсутствует, если операция завершилась без ошибок
    ContractResponse:
      mpc: bool, обязательное — Разрешен ли выпуск виртуальных карт
      template_id: str, обязательное — ID шаблона виртуальных карт
      status: str, обязательное — Статус Way4
      status_crm: str, обязательное — Статус CRM
      payment_term_id: str | None, необязательное — ID справочника условия оплаты
      payment_scheme_id: str | None, необязательное — ID справочника схема оплаты
      is_dealer: bool, обязательное — Признак дилерский
      balanceData: BalanceData, обязательное — Данные по расходу и балансу договора
      contractData: ContractData, обязательное — Данные договора
      managerData: ManagerData, обязательное — Данные по менеджеру договора
      cardsData: CardsData, обязательное — Данные по количеству карт и групп карт на договоре
    BalanceData:
      available_amount: str, обязательное — Доступный остаток
      own_balance: str, обязательное — Собственные средства
      balance: str, обязательное — Собственные средства клиента с учетом блокировок
      consumption_for_month: str, обязательное — Расход в текущем месяце (в валюте контракта)
      consumption_for_month_volume: str, обязательное — Объем потребления в текущем месяце (в литрах)
      consumption_for_prev_month_volume: str, обязательное — Объем потребления в предыдущем месяце (в литрах)
      last_payment_sum: str | None, необязательное — Сумма последнего платежа
      last_payment_date: str | None, необязательное — Дата последнего платежа
      currency: str, обязательное — Валюта договора
    ContractData:
      contract_id: str, обязательное — ID договора
      way_id: str, обязательное — ID договора в процессинге
      contract_number: str, обязательное — Номер договора
      unique_payment_id: str, обязательное — Уникальный идентификатор платежа (УИП)
      client: str, обязательное — ID клиента
      client_category: str, обязательное — Категория клиента
      contract_category: str, обязательное — Категория договора
      country: str, обязательное — Страна заключения
      region: str, обязательное — Регион заключения
      fin_institution: str, обязательное — Финансовый институт
      invoice_scheme: str, обязательное — Подключение инвойсирования
      invoice_period: str | None, необязательное — Дни выставления счетов
      invoice_pmt_delay: str | None, необязательное — Количество дней на оплату инвойса
      contract_status: str, обязательное — ID статуса договора
      contract_status_name: str, обязательное — Значение статуса договора
      pay_scheme: str, обязательное — Условия оплаты
      discount_scheme: str, обязательное — Схема расчета скидки (код из справочника DiscountScheme)
      auto_pay: str, обязательное — Признак разрешения для подключения автосписания с р/с
      auto_pay_type: str, обязательное — Тип подключения автоматического платежа
      credit_limit: str | None, необязательное — Кредитный лимит
      current_amount_limiter: str, обязательное — Накопленная сумма по контракту
      balance_amount_limiter: str | None, необязательное — Доступная сумма по контракту (max – current)
      max_amount_limiter: str | None, необязательное — Ограничение лимита на сумму договора
      date_open: str, обязательное — Дата заключения договора
      effective_date: str, обязательное — Дата вступления в силу
      end_date: str, обязательное — Дата окончания
      date_expire: str, обязательное — Дата закрытия
      product_type: bool, обязательное — Признак универсального топливного продукта (false – старый продукт, true – УТП)
      type_code: str, обязательное — Тип договора
      supplier_name: str, обязательное — Имя поставщика
    ManagerData:
      email: str, обязательное — Email менеджера
      first_name: str, обязательное — Имя менеджера
      last_name: str, обязательное — Фамилия менеджера
      middle_name: str | None, необязательное — Отчество менеджера
      work_phone: str | None, необязательное — Рабочий телефон менеджера
    CardsData:
      cards_quantity_all: str, обязательное — Число карт договора
      cards_quantity_active: str, обязательное — Число активных карт договора
      card_groups_quantity_all: str | None, необязательное — Число групп карт на договоре

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

DESCRIPTION = 'Получает данные договора. Передаёт contract_id, выводит баланс, параметры договора, менеджера и статистику карт.'

if __name__ == "__main__":
    run('get_contract_data', PARAMS, mutating=False, description=DESCRIPTION)
