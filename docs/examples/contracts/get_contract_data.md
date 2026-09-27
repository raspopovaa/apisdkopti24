---
description: "Данные договора и баланс: пример client.contracts.get_contract_data() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/contracts.yaml. Не редактируйте вручную. -->

# Данные договора и баланс

`client.contracts.get_contract_data()` · [справочник метода](../../methods/contracts.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/contracts/get_contract_data.py)

Получить баланс, расход за месяц, реквизиты договора и контакты менеджера. Это основной метод, чтобы узнать, сколько денег доступно на договоре.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/getPartContractData` | Нет | Да | Да | Да: при сетевой ошибке и ответе 429/509 |

!!! warning "Вызов тарифицируется"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Данные договора и баланс: client.contracts.get_contract_data().

Получить баланс, расход за месяц, реквизиты договора и контакты менеджера. Это основной
метод, чтобы узнать, сколько денег доступно на договоре.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/contracts/get_contract_data.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/contracts/get_contract_data/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.contracts.get_contract_data()
    balance = response.data.balanceData
    print(f"Доступно: {balance.available_amount}, баланс: {balance.balance}")
    print(f"Расход за месяц: {balance.consumption_for_month}")
    print(f"Статус договора: {response.data.status}")


async def main() -> None:
    answer = input("Вызов тарифицируется на реальном API. Продолжить? [yes/no] ")
    if answer.strip().lower() != "yes":
        return
    settings = ConnectionSettings.from_env()
    credentials = EnvironmentCredentialsProvider.from_env()
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        contract_id = os.getenv("API_CONTRACT_ID")
        if contract_id:
            client.select_contract(contract_id=contract_id)
        await example(client)


if __name__ == "__main__":
    asyncio.run(main())
```

### Параметры метода

| Параметр | Python-тип | Обязательный | По умолчанию | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | `None` | ID контракта |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`ContractQuery`](../../data-types/request_parts/ContractQuery.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str` | Да | — | ID договора |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/getPartContractData?contract_id=1-2Q4CN99 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Да | ID контракта |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`ContractDataResponse`](../../data-types/contracts/ContractDataResponse.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "mpc": true,
    "template_id": "1-4FKRL45",
    "status": "Active",
    "status_crm": "Active",
    "Is_dealer": false,
    "balanceData": {
      "available_amount": "63363.02",
      "own_balance": "63363.02",
      "balance": "63363.02",
      "consumption_for_month": "0",
      "consumption_for_month_volume": "0",
      "consumption_for_prev_month_volume": "50",
      "last_payment_sum": "40000",
      "last_payment_date": "2017-09-01",
      "currency": "810"
    },
    "contractData": {
      "contract_id": "1-7MMKF",
      "way_id": "602920",
      "contract_number": "МС014005503",
      "unique_payment_id": "2000000001160521000000000",
      "client": "1-3K159",
      "client_category": "Commercial",
      "contract_category": "№МС014005503 от 21.08.2015",
      "country": "RUS",
      "region": "45",
      "fin_institution": "ГПН Россия",
      "invoice_scheme": "ON",
      "invoice_period": "",
      "invoice_pmt_delay": "14",
      "contract_status": "Active",
      "contract_status_name": "Активен",
      "pay_scheme": "PRE",
      "discount_scheme ": "TRF_APPLY_Y",
      "auto_pay": "0",
      "auto_pay_type": "",
      "credit_limit": null,
      "current_amount_limiter": "500000.1",
      "balance_amount_limiter": "499999.9",
      "max_amount_limiter": "1000000",
      "date_open": "2015-08-21",
      "effective_date": "2015-08-21",
      "end_date": "2030-01-01",
      "date_expire": "",
      "product_type ": true,
      "type_code": "",
      "supplier_name": "Газпромнефть-Корпоративные продажи ООО"
    },
    "cardsData": {
      "cards_quantity_all": "800",
      "cards_quantity_active": "73",
      "card_groups_quantity_all": "6"
    },
    "managerData": {
      "email": "user@example.com",
      "first_name": "Иван",
      "last_name": "Иванов",
      "middle_name": "Иванович",
      "work_phone": "79990000000"
    }
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Доступно: 63363.02, баланс: 63363.02
Расход за месяц: 0
Статус договора: Active
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`ContractDataResponse`](../../data-types/contracts/ContractDataResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `ContractResponse` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`ContractResponse`](../../data-types/contracts/ContractResponse.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `mpc` | `data.mpc` | `bool` | Да | bool, обязательное | Разрешен ли выпуск виртуальных карт |
| `template_id` | `data.template_id` | `str` | Да | string, обязательное | ID шаблона виртуальных карт |
| `status` | `data.status` | `str` | Да | string, обязательное | Статус Way4 |
| `status_crm` | `data.status_crm` | `str` | Да | string, обязательное | Статус CRM |
| `payment_term_id` | `data.payment_term_id` | `str | None` | Нет | string, необязательное | ID справочника условия оплаты |
| `payment_scheme_id` | `data.payment_scheme_id` | `str | None` | Нет | string, необязательное | ID справочника схема оплаты |
| `is_dealer` | `data.is_dealer` | `bool` | Да | — | Признак дилерский |
| `balanceData` | `data.balanceData` | `BalanceData` | Да | json, обязательное | Данные по расходу и балансу договора |
| `contractData` | `data.contractData` | `ContractData` | Да | json, обязательное | Данные договора |
| `managerData` | `data.managerData` | `ManagerData` | Да | json, обязательное | Данные по менеджеру договора |
| `cardsData` | `data.cardsData` | `CardsData` | Да | json, обязательное | Данные по количеству карт и групп карт на договоре |

#### [`BalanceData`](../../data-types/contracts/BalanceData.md) · `data.balanceData`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `available_amount` | `data.balanceData.available_amount` | `str` | Да | string, обязательное | Доступный остаток |
| `own_balance` | `data.balanceData.own_balance` | `str` | Да | string, обязательное | Собственные средства |
| `balance` | `data.balanceData.balance` | `str` | Да | string, обязательное | Собственные средства клиента с учетом блокировок |
| `consumption_for_month` | `data.balanceData.consumption_for_month` | `str` | Да | string, обязательное | Расход в текущем месяце (в валюте контракта) |
| `consumption_for_month_volume` | `data.balanceData.consumption_for_month_volume` | `str` | Да | string, обязательное | Объем потребления в текущем месяце (в литрах) |
| `consumption_for_prev_month_volume` | `data.balanceData.consumption_for_prev_month_volume` | `str` | Да | string, обязательное | Объем потребления в предыдущем месяце (в литрах) |
| `last_payment_sum` | `data.balanceData.last_payment_sum` | `str | None` | Нет | string, необязательное | Сумма последнего платежа |
| `last_payment_date` | `data.balanceData.last_payment_date` | `str | None` | Нет | string, необязательное | Дата последнего платежа |
| `currency` | `data.balanceData.currency` | `str` | Да | string, обязательное | Валюта договора |

#### [`ContractData`](../../data-types/contracts/ContractData.md) · `data.contractData`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `contract_id` | `data.contractData.contract_id` | `str` | Да | string, обязательное | ID договора |
| `way_id` | `data.contractData.way_id` | `str` | Да | string, обязательное | ID договора в процессинге |
| `contract_number` | `data.contractData.contract_number` | `str` | Да | string, обязательное | Номер договора |
| `unique_payment_id` | `data.contractData.unique_payment_id` | `str` | Да | string, обязательное | Уникальный идентификатор платежа (УИП) |
| `client` | `data.contractData.client` | `str` | Да | string, обязательное | ID клиента |
| `client_category` | `data.contractData.client_category` | `str` | Да | string, обязательное | Категория клиента |
| `contract_category` | `data.contractData.contract_category` | `str` | Да | string, обязательное | Категория договора |
| `country` | `data.contractData.country` | `str` | Да | string, обязательное | Страна заключения |
| `region` | `data.contractData.region` | `str` | Да | string, обязательное | Регион заключения |
| `fin_institution` | `data.contractData.fin_institution` | `str` | Да | string, обязательное | Финансовый институт |
| `invoice_scheme` | `data.contractData.invoice_scheme` | `str` | Да | string, обязательное | Подключение инвойсирования |
| `invoice_period` | `data.contractData.invoice_period` | `str | None` | Нет | string, необязательное | Дни выставления счетов |
| `invoice_pmt_delay` | `data.contractData.invoice_pmt_delay` | `str | None` | Нет | string, необязательное | Количество дней на оплату инвойса |
| `contract_status` | `data.contractData.contract_status` | `str` | Да | string, обязательное | ID статуса договора |
| `contract_status_name` | `data.contractData.contract_status_name` | `str` | Да | string, обязательное | Значение статуса договора |
| `pay_scheme` | `data.contractData.pay_scheme` | `str` | Да | string, обязательное | Условия оплаты |
| `discount_scheme` | `data.contractData.discount_scheme` | `str` | Да | string, обязательное | Схема расчета скидки (код из справочника DiscountScheme) |
| `auto_pay` | `data.contractData.auto_pay` | `str` | Да | string, обязательное | Признак разрешения для подключения автосписания с р/с |
| `auto_pay_type` | `data.contractData.auto_pay_type` | `str` | Да | string, обязательное | Тип подключения автоматического платежа |
| `credit_limit` | `data.contractData.credit_limit` | `str | None` | Нет | string, необязательное | Кредитный лимит |
| `current_amount_limiter` | `data.contractData.current_amount_limiter` | `str` | Да | string, обязательное | Накопленная сумма по контракту |
| `balance_amount_limiter` | `data.contractData.balance_amount_limiter` | `str | None` | Нет | string, необязательное | Доступная сумма по контракту (max – current) |
| `max_amount_limiter` | `data.contractData.max_amount_limiter` | `str | None` | Нет | string, необязательное | Ограничение лимита на сумму договора |
| `date_open` | `data.contractData.date_open` | `str` | Да | string, обязательное | Дата заключения договора |
| `effective_date` | `data.contractData.effective_date` | `str` | Да | string, обязательное | Дата вступления в силу |
| `end_date` | `data.contractData.end_date` | `str` | Да | string, обязательное | Дата окончания |
| `date_expire` | `data.contractData.date_expire` | `str` | Да | string, обязательное | Дата закрытия |
| `product_type` | `data.contractData.product_type` | `bool` | Да | bool, обязательное | Признак универсального топливного продукта (false – старый продукт, true – УТП) |
| `type_code` | `data.contractData.type_code` | `str` | Да | string, обязательное | Тип договора |
| `supplier_name` | `data.contractData.supplier_name` | `str` | Да | string, обязательное | Имя поставщика |

#### [`ManagerData`](../../data-types/contracts/ManagerData.md) · `data.managerData`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `email` | `data.managerData.email` | `str` | Да | string, обязательное | Email менеджера |
| `first_name` | `data.managerData.first_name` | `str` | Да | string, обязательное | Имя менеджера |
| `last_name` | `data.managerData.last_name` | `str` | Да | string, обязательное | Фамилия менеджера |
| `middle_name` | `data.managerData.middle_name` | `str | None` | Нет | string, необязательное | Отчество менеджера |
| `work_phone` | `data.managerData.work_phone` | `str | None` | Нет | string, необязательное | Рабочий телефон менеджера |

#### [`CardsData`](../../data-types/contracts/CardsData.md) · `data.cardsData`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `cards_quantity_all` | `data.cardsData.cards_quantity_all` | `str` | Да | string, обязательное | Число карт договора |
| `cards_quantity_active` | `data.cardsData.cards_quantity_active` | `str` | Да | string, обязательное | Число активных карт договора |
| `card_groups_quantity_all` | `data.cardsData.card_groups_quantity_all` | `str | None` | Нет | string, необязательное | Число групп карт на договоре |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Пользователь API не имеет доступа к договору.

**Что делать:** Проверьте `contract_id` и права пользователя.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Нет доступа к договору"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_contract_data Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Данные по договору». Запрос в спецификации: `GET http://localhost/vip/v1/getPartContractData`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- `contract_id` в API обязателен. Если его не передать, SDK подставит договор, выбранный при авторизации.
- В примере ответа спецификации нет обязательных полей `data.status`, `data.status_crm`, `data.Is_dealer`; в пример на этой странице добавлены условные значения.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET: http://localhost/vip/v1/getPartContractData?contract_id=1-13WR9S2
```

## Что важно знать

- Суммы приходят строками, например `"63363.02"`. Для расчётов переводите их в `Decimal`, а не во `float`.
