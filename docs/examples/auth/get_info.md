---
description: "Статистика обращений к API: пример client.auth.get_info() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/auth.yaml. Не редактируйте вручную. -->

# Статистика обращений к API

`client.auth.get_info()` · [справочник метода](../../methods/auth.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/auth/get_info.py)

Узнать тариф, размер пакета запросов и сколько раз вызывались методы API за месяц или за день. Помогает следить за расходом тарифицируемых запросов.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/info` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Статистика обращений к API: client.auth.get_info().

Узнать тариф, размер пакета запросов и сколько раз вызывались методы API за месяц или за
день. Помогает следить за расходом тарифицируемых запросов.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/auth/get_info.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/auth/get_info/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.auth.get_info(period="2026-09")
    info = response.data.client_info
    print(f"Тариф: {info.PricePlan}, оплачено запросов: {info.Queries}")
    print(f"Всего вызовов за период: {response.data.methods.all}")


async def main() -> None:
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
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |
| `period` | `str | None` | Нет | `None` | Период: месяц в формате `YYYY-MM` или конкретный день в формате `YYYY-MM-DD`. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/info?period=2026-09 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `period` | строка запроса | `2026-09` | string | Нет | Период формата за весь месяц (YYYY-MM 2018-10) или за конкретный день (YYYY-MM-DD 2018-10-10) |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`GetInfoResponse`](../../data-types/auth/GetInfoResponse.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "from": "2018-10-24 00:00:00",
    "to": "2018-10-25 00:00:00",
    "client_info": {
      "Client": "1-2SWR0I3",
      "ClientType": "D",
      "Contract": "1-2SWRA1O",
      "ContractName": "ЯР014032462",
      "PricePlan": "Base",
      "Cost": 30000,
      "Queries": 20000,
      "Additional": 1
    },
    "methods": {
      "all": 18,
      "cards": 15,
      "cardgroups": 1,
      "card": 2
    },
    "methods_info": {
      "actions_bill": {
        "getpartcontractdata": "Данные по договору",
        "getpayments": "Платежи по договору",
        "documents_post": "Заказ первичных документов на почту",
        "order_cards": "Заказ топливных карт (Пластиковых)",
        "cards": "Список топливных карт (Процессинг)",
        "cards_drivers": "Список водителей по карте",
        "cards_detail": "Детальная информация по карте",
        "blockcard": "Блокировка и разблокировка карты",
        "setcardcomment": "Установить комментарий на топливную карту",
        "cards_reset_pin": "Подтверждение сброса попыток некорректного ввода PIN - кода карты",
        "setcardproduct": "Изменить тип продукта карты",
        "movetocard": "Перевести деньги с договора на кошелек",
        "movetocontract": "Перевести деньги с кошелька на договор",
        "transactions": "Список последних транзакций по договору и по карте",
        "removelimit": "Удаление продуктового лимита по карте и группе карт",
        "setlimit": "Установка/Изменение продуктового лимита по карте и группе карт",
        "restriction": "Список товарных ограничителей по договору, карте и группе карт",
        "removerestriction": "Удаление товарного ограничителя по карте и группе карт",
        "setrestriction": "Установка/Изменение товарного ограничителя по карте и группе карт",
        "regionlimit": "Список региональных лимитов по договору, карте и группе карт",
        "removeregionlimit": "Удаление регионального лимита по карте и группе карт",
        "setregionlimit": "Установка/Изменение регионального лимита по карте и группе карт",
        "setcardstogroup": "Добавление карт в группу карт",
        "removecardgroup": "Удаление группы карт",
        "setcardgroup": "Установка/Изменение группы карт",
        "reports": "Запрос транзакционного отчета за период на email",
        "getreportfile": "Генерация файла отчета",
        "invites_post": "Создание приглашения с отправкой",
        "invites_send": "Повторная отправка приглашения",
        "users_get": "Список пользователей",
        "users_post": "Создание водителя без ПДН",
        "users_attach_contracts": "Прикрепление договоров к пользователю",
        "users_detach_contracts": "Открепление договоров от пользователя",
        "users_attach_card": "Прикрепление карты к пользователю",
        "users_detach_card": "Открепление карты от пользователя",
        "users_delete": "Удаление пользователя",
        "vc_templates_post": "Создание шаблона ВК",
        "vc_templates_put": "Изменение шаблона ВК",
        "vc_templates_delete": "Удаление шаблона ВК",
        "vc_templates_limits_post": "Создание лимита шаблона ВК",
        "vc_templates_limits_put": "Изменение лимита шаблона ВК",
        "vc_templates_limits_delete": "Удаление лимита шаблона ВК",
        "vc_templates_restrictions_post": "Создание ограничителя шаблона ВК",
        "vc_templates_restrictions_put": "Изменение ограничителя шаблона ВК",
        "vc_templates_restrictions_delete": "Удаление ограничителя шаблона ВК",
        "vc_templates_georestrictions_post": "Создание геоограничителя шаблона ВК",
        "vc_templates_georestrictions_put": "Изменение геоограничителя шаблона ВК",
        "vc_templates_georestrictions_delete": "Удаление геоограничителя шаблона ВК",
        "cards_post": "Выпустить виртуальную карту"
      },
      "actions_not_bill": {
        "authuser": "Авторизация пользователя",
        "logoff": "Деавторизация пользователя",
        "info": "Статистика",
        "documents_get": "Список первичных документов по договору за период",
        "cards_cache": "Список карт договора",
        "cards_group": "Список топливных карт по группе карт",
        "cards_verify_pin": "Запрос одноразового кода для сброса попыток ввода PIN карты",
        "limit": "Список продуктовых лимитов по договору, карте и группе карт",
        "cardgroups": "Список групп карт",
        "reports_file": "Запрос транзакционного отчета за период по ссылке",
        "getreportjoblist": "Список ранее заказанных отчетов по ссылке",
        "invites_get": "Список приглашений",
        "invites_post_free": "Создание приглашения",
        "invites_delete": "Удалить приглашение",
        "vc_templates_get": "Список шаблонов ВК",
        "vc_templates_limits_get": "Список лимитов шаблона ВК",
        "vc_templates_restrictions_get": "Список ограничителей шаблона ВК",
        "vc_templates_georestrictions_get": "Список геоограничителей шаблона ВК",
        "vc_delete_mpc": "Удаление МПК",
        "vc_reset_mpc": "Сброс счетчиков МПК",
        "azs": "Список торговых точек",
        "getdictionary": "Общие справочники",
        "mpc": "Список выпущенных МПК QR",
        "pay": "Генерация QR кода оплаты",
        "init_mpc": "Инициализация выпуска МПК",
        "confirm_mpc": "Подтверждение выпуска МПК",
        "update_mpc": "Обновление МПК"
      }
    }
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Тариф: Base, оплачено запросов: 20000
Всего вызовов за период: 18
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`GetInfoResponse`](../../data-types/auth/GetInfoResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `InfoData` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`InfoData`](../../data-types/auth/InfoData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `from` | `data.from` | `datetime` | Да | string, обязательное | Начало периода статистики |
| `to` | `data.to` | `datetime` | Да | string, обязательное | Конец периода статистики |
| `client_info` | `data.client_info` | `ClientInfo` | Да | json, обязательное | Информация о клиенте |
| `methods` | `data.methods` | `MethodsCount` | Да | json, обязательное | Количество вызовов по категориям |
| `methods_info` | `data.methods_info` | `MethodsInfo` | Да | json, обязательное | Описание доступных методов API |

#### [`ClientInfo`](../../data-types/auth/ClientInfo.md) · `data.client_info`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `Client` | `data.client_info.Client` | `str` | Да | string, обязательное | ID клиента |
| `ClientType` | `data.client_info.ClientType` | `str` | Да | string, обязательное | Тип клиента (например, D) |
| `Contract` | `data.client_info.Contract` | `str | None` | Нет | string, необязательное | ID контракта |
| `ContractName` | `data.client_info.ContractName` | `str | None` | Нет | string, необязательное | Название контракта |
| `PricePlan` | `data.client_info.PricePlan` | `str | None` | Нет | string, необязательное | Тарифный план |
| `Cost` | `data.client_info.Cost` | `int | float | None` | Нет | uint, необязательное | Стоимость запросов |
| `Queries` | `data.client_info.Queries` | `int | None` | Нет | uint, необязательное | Количество запросов |
| `Additional` | `data.client_info.Additional` | `int | None` | Нет | uint, необязательное | Дополнительное значение |

#### [`MethodsCount`](../../data-types/auth/MethodsCount.md) · `data.methods`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `all` | `data.methods.all` | `int` | Да | uint, обязательное | Общее количество методов |
| `cards` | `data.methods.cards` | `int | None` | Нет | — | Методы, связанные с картами |
| `cardgroups` | `data.methods.cardgroups` | `int | None` | Нет | — | Методы, связанные с группами карт |
| `card` | `data.methods.card` | `int | None` | Нет | — | Методы, связанные с одной картой |

#### [`MethodsInfo`](../../data-types/auth/MethodsInfo.md) · `data.methods_info`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `actions_bill` | `data.methods_info.actions_bill` | `dict[str, str]` | Да | json, обязательное | Платные методы API (влияют на статистику) |
| `actions_not_bill` | `data.methods_info.actions_not_bill` | `dict[str, str]` | Да | json, обязательное | Бесплатные методы API (не влияют на статистику) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Значение `period` не соответствует форматам `YYYY-MM` или `YYYY-MM-DD`.

**Что делать:** Передайте месяц `"2026-09"` или день `"2026-09-15"`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректный период"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении get_info Сообщение сервера: Некорректный период. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Статистика». Запрос в спецификации: `GET http://localhost/vip/v1/info`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
Весь месяц:
GET: http://localhost/vip/v1/info?period=2018-10
Конкретный день:
GET: http://localhost/vip/v1/info?period=2018-10-20
```

## Что важно знать

- `period` — месяц в формате `YYYY-MM` или день в формате `YYYY-MM-DD`. Если его не передать, SDK отправит текущие дату и время в формате `YYYY-MM-DD HH:MM:SS`, которого нет в спецификации. Передавайте `period` явно.
