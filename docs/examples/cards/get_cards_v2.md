---
description: "Список карт договора (API v2): пример client.cards.get_cards_v2() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/cards.yaml. Не редактируйте вручную. -->

# Список карт договора (API v2)

`client.cards.get_cards_v2()` · [справочник метода](../../methods/cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/cards/get_cards_v2.py)

Получить первую страницу активных карт договора и вывести номер, статус и группу каждой карты. Это основной метод для списков карт: он поддерживает фильтры, поиск и пагинацию.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/cards` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Список карт договора (API v2): client.cards.get_cards_v2().

Получить первую страницу активных карт договора и вывести номер, статус и группу каждой
карты. Это основной метод для списков карт: он поддерживает фильтры, поиск и пагинацию.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/cards/get_cards_v2.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/cards/get_cards_v2/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.cards.get_cards_v2(status="Active", page=1, onpage=20)
    print(f"Найдено карт: {response.total_count}")
    for card in response.result:
        print(f"{card.id}  {card.number}  {card.status_name}  группа: {card.group_name}")


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
| `contract_id` | `str | None` | Нет | `None` | ID договора (Можно передать в заголовке запроса, а не только в URI - строке). Если не передать, то подставим 1й договор из списка. |
| `sort` | `str` | Нет | `'-id'` | Сортировка (sort=-id). Поле для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC). |
| `q` | `str | None` | Нет | `None` | Поисковый запрос (Ищет по комментарию на карте, по номерам карт). |
| `status` | `str | None` | Нет | `None` | Фильтрует по статусам карт (Справочник CardStatus) |
| `carrier` | `str | None` | Нет | `None` | Фильтрует по типу карты (Plastic – физическая карта, Virtual Card – виртуальная карта). |
| `platon` | `bool | None` | Нет | `None` | Отобразит карты с подключенной услугой Платон. |
| `avtodor` | `bool | None` | Нет | `None` | Отобразит карты с подключенной услугой Автодор. |
| `users` | `bool | None` | Нет | `None` | С помощью данного параметра подгружаются пользователи и в списке карт заполняются поля users и mpc. Время ответа зависит от количества карт и количества пользователей. |
| `group_id` | `str | None` | Нет | `None` | ID группы карт. При передаче параметра отобразит только карты этой группы. |
| `page` | `int | None` | Нет | `None` | Номер страницы (Пагинация). |
| `onpage` | `int | None` | Нет | `None` | Элементов на странице (Пагинация). |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`CardsV2Query`](../../data-types/cards/CardsV2Query.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `contract_id` | `str | None` | Нет | минимальная длина: 1; — | ID договора (Можно передать в заголовке запроса, а не только в URI - строке). Если не передать, то подставим 1й договор из списка. |
| `group_id` | `str | None` | Нет | минимальная длина: 1; — | ID группы карт. При передаче параметра отобразит только карты этой группы. |
| `sort` | `str` | Нет | минимальная длина: 1 | Сортировка (sort=-id). Поле для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC). |
| `q` | `str | None` | Нет | — | Поисковый запрос (Ищет по комментарию на карте, по номерам карт). |
| `status` | `str | None` | Нет | — | Фильтрует по статусам карт (Справочник CardStatus) |
| `carrier` | `str | None` | Нет | — | Фильтрует по типу карты (Plastic – физическая карта, Virtual Card – виртуальная карта). |
| `platon` | `bool | None` | Нет | — | Отобразит карты с подключенной услугой Платон. |
| `avtodor` | `bool | None` | Нет | — | Отобразит карты с подключенной услугой Автодор. |
| `users` | `bool | None` | Нет | — | С помощью данного параметра подгружаются пользователи и в списке карт заполняются поля users и mpc. Время ответа зависит от количества карт и количества пользователей. |
| `page` | `int | None` | Нет | минимум: 1; — | Номер страницы (Пагинация). |
| `onpage` | `int | None` | Нет | минимум: 1; — | Элементов на странице (Пагинация). |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/cards?contract_id=1-2Q4CN99&sort=-id&status=Active&page=1&onpage=20 HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-2Q4CN99
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `contract_id` | строка запроса | `1-2Q4CN99` | string | Нет | ID договора (Можно передать в заголовке запроса, а не только в URI - строке). Если не передать, то подставим 1й договор из списка. |
| `sort` | строка запроса | `-id` | string | Нет | Сортировка (sort=-id). Поле для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC). |
| `status` | строка запроса | `Active` | string | Нет | Фильтрует по статусам карт (Справочник CardStatus) |
| `page` | строка запроса | `1` | string | Нет | Номер страницы (Пагинация). |
| `onpage` | строка запроса | `20` | string | Нет | Элементов на странице (Пагинация). |
| `contract_id` | заголовок | `1-2Q4CN99` | string | — | Договор в заголовке запроса. Спецификация разрешает передавать его так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`CardsV2Response`](../../data-types/cards/CardsV2Response.md).
Пример ответа взят из спецификации API 1.1.60.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 2,
    "result": [
      {
        "id": "19647206",
        "group_id": "1-1F56KR",
        "group_name": "Тестовая группа",
        "contract_id": "1-1FLW4T7",
        "contract_name": "СЗ01590002",
        "number": "7000000000000000",
        "status": "Active",
        "status_name": "Активна",
        "comment": null,
        "product": "limit",
        "product_name": "Лимитная схема",
        "carrier": "Virtual Card",
        "carrier_name": "Виртуальная карта",
        "platon": false,
        "avtodor": true,
        "sync_group_state": "Не синхронизирована",
        "users": [
          "1-PBQRL0E"
        ],
        "mpc": true
      },
      {
        "id": "19121808",
        "group_id": "1-O86M9OJ",
        "group_name": "Гараж 5",
        "contract_id": "1-1FLW4T7",
        "contract_name": "СЗ01590002",
        "number": "7000000000000000",
        "status": "Locked(Client)",
        "status_name": "Заблокирована (Клиент)",
        "comment": "Камаз 100",
        "product": "wallet",
        "product_name": "Электронный кошелёк",
        "carrier": "Plastic",
        "carrier_name": "Пластиковая карта",
        "platon": true,
        "avtodor": false,
        "sync_group_state": "Синхронизирована",
        "users": [],
        "mpc": false
      }
    ]
  },
  "timestamp": 1608251286
}
```

Вывод примера на этом ответе:

```text
Найдено карт: 2
19647206  7000000000000000  Активна  группа: Тестовая группа
19121808  7000000000000000  Заблокирована (Клиент)  группа: Гараж 5
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`CardsV2Response`](../../data-types/cards/CardsV2Response.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `CardsV2Data` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`CardsV2Data`](../../data-types/cards/CardsV2Data.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `total_count` | `data.total_count` | `int` | Да | uint, обязательное | Общее количество найденных карт |
| `result` | `data.result` | `list[CardV2Item] | None` | Нет | json, необязательное | Список карт договора |

#### [`CardV2Item`](../../data-types/cards/CardV2Item.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `id` | `data.result[].id` | `str` | Да | string, обязательное | Уникальный идентификатор карты |
| `group_id` | `data.result[].group_id` | `str | None` | Нет | string, необязательное | ID группы карт, если назначена |
| `group_name` | `data.result[].group_name` | `str | None` | Нет | string, необязательное | Название группы карт |
| `contract_id` | `data.result[].contract_id` | `str` | Да | string, обязательное | ID договора, к которому принадлежит карта |
| `contract_name` | `data.result[].contract_name` | `str` | Да | string, обязательное | Название договора |
| `number` | `data.result[].number` | `str` | Да | string, обязательное | Номер топливной карты |
| `status` | `data.result[].status` | `str` | Да | string, обязательное | Системное значение статуса карты |
| `status_name` | `data.result[].status_name` | `str | None` | Нет | string, необязательное | Отображаемое имя статуса (например 'Активна') |
| `comment` | `data.result[].comment` | `str | None` | Нет | string, необязательное | Комментарий, установленный пользователем |
| `product` | `data.result[].product` | `str` | Да | string, обязательное | Тип продукта, например 'limit' или 'wallet' |
| `product_name` | `data.result[].product_name` | `str | None` | Нет | string, необязательное | Отображаемое имя продукта |
| `carrier` | `data.result[].carrier` | `str` | Да | string, обязательное | Тип носителя карты ('Plastic' или 'Virtual Card') |
| `carrier_name` | `data.result[].carrier_name` | `str | None` | Нет | string, необязательное | Название типа носителя карты |
| `platon` | `data.result[].platon` | `bool` | Да | bool, обязательное | Признак наличия поддержки Platon (оплата проезда) |
| `avtodor` | `data.result[].avtodor` | `bool` | Да | bool, обязательное | Признак наличия поддержки Автодора |
| `sync_group_state` | `data.result[].sync_group_state` | `str | None` | Нет | string, необязательное | Состояние синхронизации группы карт |
| `users` | `data.result[].users` | `list[str] | None` | Нет | [string, string], необязательное | Список ID пользователей, привязанных к карте |
| `mpc` | `data.result[].mpc` | `bool | None` | Нет | bool, необязательное | Признак наличия мультипроцессингового центра (mpc) |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Фильтр содержит значение, которого нет в справочнике, например `status="active"` вместо `status="Active"`.

**Что делать:** Возьмите допустимые значения из справочника `CardStatus`.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректное значение параметра status"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении get_cards_v2 Сообщение сервера: Некорректное значение параметра status. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### 403 · `AccessDeniedError`

**Почему:** Пользователь API не имеет доступа к выбранному договору или его роли не разрешено читать карты.

**Что делать:** Проверьте `contract_id`, список договоров из `client.auth.auth_user()` и права пользователя в личном кабинете.

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
AccessDeniedError: [403] Доступ запрещён при выполнении get_cards_v2 Сообщение сервера: Нет доступа к договору. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.cards.get_cards_v2(page=0)
```

Страницы нумеруются с 1, поэтому модель запроса отклоняет `page=0`. Исключение `pydantic.ValidationError`:

```text
1 validation error for CardsV2Query
page
  Input should be greater than or equal to 1 [type=greater_than_equal]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Список карт договора (v.2)». Запрос в спецификации: `GET http://localhost/vip/v2/cards`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET: http://localhost/vip/v2/cards?sort=-id&q=700582009&status=Active&carrier=Plastic&platon=true&avtodor=true&users=true&page=1&onpage=10
```

## Что важно знать

- `contract_id` можно не передавать: SDK возьмёт договор, выбранный при авторизации, и отправит его в строке запроса и в заголовке `contract_id`.
- Страницы нумеруются с 1. Чтобы обойти все карты, используйте `client.cards.iter_cards_v2()`: он сам запрашивает страницы по очереди.
- Значения фильтра `status` берутся из справочника `CardStatus`: `client.dictionaries.get_dictionary(name="CardStatus")`.
