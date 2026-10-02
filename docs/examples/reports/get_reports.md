---
description: "Доступные отчёты: пример client.reports.get_reports() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/reports.yaml. Не редактируйте вручную. -->

# Доступные отчёты

`client.reports.get_reports()` · [справочник метода](../../methods/reports.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/reports/get_reports.py)

Получить отчёты, которые можно заказать: ID отчёта, форматы файла и параметры. ID и параметры передаются в `order_report`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/reports` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Доступные отчёты: client.reports.get_reports().

Получить отчёты, которые можно заказать: ID отчёта, форматы файла и параметры. ID и
параметры передаются в `order_report`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/reports/get_reports.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/reports/get_reports/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.reports.get_reports()
    for report in response.data.result:
        params = ", ".join(parameter.name for parameter in report.parameters)
        print(f"{report.id}: {report.name} [{', '.join(report.formats)}] параметры: {params}")


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
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Отдельной модели запроса у метода нет: SDK проверяет параметры сигнатурой метода и общими правилами идентификаторов.

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/reports HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`ReportListResponse`](../../data-types/reports/ReportListResponse.md).
Пример ответа; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 8,
    "result": [
      {
        "id": "atc_report_account_balance",
        "name": "Отчет по остаткам средств на счете клиента",
        "formats": [
          "xlsx",
          "xml"
        ],
        "parameters": [
          {
            "name": "start_date",
            "value": null,
            "label": "Период с",
            "default_value": "2022-12-13 00:00:00",
            "menu_values": null,
            "type": "date"
          },
          {
            "name": "id_agreement",
            "value": null,
            "label": "Договор",
            "default_value": null,
            "menu_values": null,
            "type": "Contract"
          }
        ]
      },
      {
        "id": "tsc_total_transaction_protocol",
        "name": "Итоговый протокол транзакций (ведомость)",
        "formats": [
          "xlsx",
          "xml"
        ],
        "parameters": [
          {
            "name": "start_date",
            "value": null,
            "label": "Период с",
            "default_value": "2022-11-13 00:00:00",
            "menu_values": null,
            "type": "date"
          },
          {
            "name": "end_date",
            "value": null,
            "label": "Период по",
            "default_value": "2022-12-13 00:00:00",
            "menu_values": null,
            "type": "date"
          }
        ]
      }
    ]
  },
  "timestamp": 1670882544
}
```

Вывод примера на этом ответе:

```text
atc_report_account_balance: Отчет по остаткам средств на счете клиента [xlsx, xml, pdf, rtf, csv] параметры: start_date, id_agreement, id_client
tsc_total_transaction_protocol: Итоговый протокол транзакций (ведомость) [xlsx, xml, pdf, rtf, csv] параметры: start_date, end_date, id_card, card_group_code, id_agreement, id_client
tsc_report_card_limits: Отчет о текущих лимитах по картам [xlsx, xml, pdf, rtf, csv] параметры: card_group_name, card_status, id_card, card_group_code, id_agreement, id_client
tsc_report_card_trading_volume: Оборот по картам по типам клиентов в разрезе цен на продукты, услуги за период [xlsx, xml, pdf, rtf, csv] параметры: start_date, end_date, id_card, card_group_code, id_agreement, id_client, detail
tsc_report_card_status: Отчет о картах по статусу за период [xlsx, xml, pdf, rtf, csv] параметры: card_status, start_date, end_date, id_agreement, id_client, card_group_code, id_card
tsc_transaction_protocol: Протокол транзакций (ведомость) [xlsx, xml, pdf, rtf, csv] параметры: start_date, end_date, id_card, card_group_code, id_agreement, id_client
tsc_report_trading_volume_product: Оборот по обслуживанию по видам продуктов и услуг за период [xlsx, pdf, rtf] параметры: start_date, end_date, id_card, card_group_code, id_agreement, id_client
tsc_report_transaction_reriod: Транзакционный отчет за период [xlsx, pdf, rtf] параметры: start_date, end_date, id_card, card_group_code, id_agreement, id_client
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`ReportListResponse`](../../data-types/reports/ReportListResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>ReportList</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`ReportList`](../../data-types/reports/ReportList.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Количество доступных отчетов |
| `result` | `data.result` | <code>list[ReportItem] &#124; None</code> | Нет | Массив отчетов |

#### [`ReportItem`](../../data-types/reports/ReportItem.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | Идентификатор отчета |
| `name` | `data.result[].name` | <code>str</code> | Да | Название отчета |
| `formats` | `data.result[].formats` | <code>list[str]</code> | Да | Список поддерживаемых форматов (pdf, xlsx, csv и т.д.) |
| `parameters` | `data.result[].parameters` | <code>list[ReportParameter]</code> | Да | Список параметров отчета |

#### [`ReportParameter`](../../data-types/reports/ReportParameter.md) · `data.result[].parameters[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `name` | `data.result[].parameters[].name` | <code>str</code> | Да | Имя параметра, используемое в запросах |
| `value` | `data.result[].parameters[].value` | <code>str &#124; None</code> | Нет | Значение параметра |
| `label` | `data.result[].parameters[].label` | <code>str &#124; None</code> | Да | Отображаемое название параметра; реальный API может вернуть null |
| `default_value` | `data.result[].parameters[].default_value` | <code>str &#124; None</code> | Нет | Значение по умолчанию |
| `menu_values` | `data.result[].parameters[].menu_values` | <code>list[ReportParameterMenuValue] &#124; None</code> | Нет | Список возможных значений для выбора из меню |
| `type` | `data.result[].parameters[].type` | <code>str</code> | Да | Тип параметра (например, date, Contract, Group) |

#### [`ReportParameterMenuValue`](../../data-types/reports/ReportParameterMenuValue.md) · `data.result[].parameters[].menu_values[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `labels` | `data.result[].parameters[].menu_values[].labels` | <code>str &#124; None</code> | Нет | Отображаемое имя пункта меню |
| `values` | `data.result[].parameters[].menu_values[].values` | <code>str &#124; None</code> | Нет | Значение пункта меню |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Роль пользователя не позволяет заказывать отчёты.

**Что делать:** Проверьте роль пользователя API.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Доступ запрещён"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении get_reports Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Поле `data.result[].parameters[].label`: бывает `null`. Тип в модели SDK: <code>str &#124; None</code>.
