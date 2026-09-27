---
description: "Список АЗС (API v1): пример client.dictionaries.get_azs_list_v1() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/dictionaries.yaml. Не редактируйте вручную. -->

# Список АЗС (API v1)

`client.dictionaries.get_azs_list_v1()` · [справочник метода](../../methods/dictionaries.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/dictionaries/get_azs_list_v1.py)

Получить торговые точки через первую версию API: с терминалами, ценами и услугами. Для новых интеграций удобнее `get_azs_list_v2`.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v1/AZS` | Нет | Нет | Да | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Список АЗС (API v1): client.dictionaries.get_azs_list_v1().

Получить торговые точки через первую версию API: с терминалами, ценами и услугами. Для
новых интеграций удобнее `get_azs_list_v2`.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/dictionaries/get_azs_list_v1.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/dictionaries/get_azs_list_v1/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.dictionaries.get_azs_list_v1(
        page=1, onpage=10, filter={"country": ["RUS"], "region": ["40"]}
    )
    for azs in response.data.result:
        print(f"{azs.id}  {azs.type}  регион {azs.regionCode}  {azs.belongsTo}")


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
| `page` | `int` | Нет | `1` | Номер страницы начиная с 1 |
| `onpage` | `int` | Нет | `10` | Количество элементов на странице (0 – если нужно вывести все элементы) |
| `filter` | `AzsV1Filter | Mapping[str, object] | None` | Нет | `None` | JSON-объект для фильтрации списка торговых точек. |
| `id` | `str | None` | Нет | `None` | ID торговой точки для получения одной детальной записи. |
| `q` | `str | None` | Нет | `None` | Поисковая строка запроса (Ищет по наименованию ТТ, адресу и номеру терминала) |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`AzsV1Filter`](../../data-types/dictionaries/AzsV1Filter.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `region` | `list[str] | None` | Нет | — | — |
| `country` | `list[str] | None` | Нет | — | — |
| `owntype` | `list[str] | None` | Нет | — | — |
| `type` | `list[str] | None` | Нет | — | — |
| `status` | `list[str] | None` | Нет | — | — |
| `services` | `list[int] | None` | Нет | — | — |
| `goods` | `list[str] | None` | Нет | — | — |

#### [`AzsV1Query`](../../data-types/dictionaries/AzsV1Query.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `page` | `int` | Нет | минимум: 1 | Номер страницы начиная с 1 |
| `onpage` | `int` | Нет | минимум: 0 | Количество элементов на странице (0 – если нужно вывести все элементы) |
| `filter` | `AzsV1Filter | None` | Нет | — | JSON объект для фильтрации списка |
| `q` | `str | None` | Нет | — | Поисковая строка запроса (Ищет по наименованию ТТ, адресу и номеру терминала) |
| `id` | `str | None` | Нет | минимальная длина: 1; — | ID торговой точки (для детального показа 1й ТТ) |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v1/AZS?page=1&onpage=10&filter={"region":["40"],"country":["RUS"]} HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `page` | строка запроса | `1` | string | Нет | Номер страницы начиная с 1 |
| `onpage` | строка запроса | `10` | string | Нет | Количество элементов на странице (0 – если нужно вывести все элементы) |
| `filter` | строка запроса | `{"region":["40"],"country":["RUS"]}` | string | Нет | JSON объект для фильтрации списка |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`AzsListV1Response`](../../data-types/dictionaries/AzsListV1Response.md).
Пример ответа; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 3,
    "result": [
      {
        "id": "366148",
        "siebelId": "1-DNI9R",
        "contractNumber": "AZS101258",
        "contractName": "048",
        "status": "257",
        "countryCode": "RUS",
        "regionCode": "40",
        "secessionGPN": "Северо-Запад",
        "belongsTo": "ООО СтопЭкcпресс",
        "partner": "STO408",
        "ownType": "FRAN",
        "locationType": "ROAD",
        "brand": "<>",
        "openDate": "07/11/2014",
        "closeDate": "",
        "latitude": "59.896371",
        "longitude": "30.288409",
        "type": "АЗС",
        "timeZone": "0",
        "services": [],
        "prices": [
          {
            "ID": "3788",
            "GasStationID": "366148",
            "GoodsCode": "00000000000003",
            "Price": "40.75",
            "Currency": "810;RUR",
            "DateTo": "2100-01-01T00:00:00",
            "DateFrom": "2017-11-24T23:52:54"
          },
          {
            "ID": "3786",
            "GasStationID": "366148",
            "GoodsCode": "00000000000004",
            "Price": "37.5",
            "Currency": "810;RUR",
            "DateTo": "2100-01-01T00:00:00",
            "DateFrom": "2017-11-24T23:52:54"
          }
        ],
        "terminals": [
          {
            "id": "RC780301",
            "active": true,
            "name": "Ingenico ipp320",
            "status": "Работает",
            "type": "POS-ALL",
            "connectionType": "Cопряженный с СУ",
            "number": "RC780301"
          },
          {
            "id": "RC780302",
            "active": true,
            "name": "Ingenico ipp320",
            "status": "Работает",
            "type": "POS-ALL",
            "connectionType": "Cопряженный с СУ",
            "number": "RC780302"
          }
        ],
        "address": {
          "track_id": null,
          "kmRoad": "",
          "roadSide": "Внешняя",
          "city": "г. Санкт-Петербург",
          "street": "ул. Маршала Говорова ",
          "house": "41",
          "building": "",
          "phone": "+79313559830",
          "fax": ""
        },
        "searchTxt": "АЗС <> 048 г. Санкт-Петербург ул. Маршала Говорова  RC780301 RC780302 RF050301 RF050302"
      },
      {
        "id": "8792526",
        "siebelId": "1-25O72B2",
        "contractNumber": "AZS104840",
        "contractName": "050",
        "status": "257",
        "countryCode": "RUS",
        "regionCode": "40",
        "secessionGPN": "Северо-Запад",
        "belongsTo": "ООО СтопЭкcпресс",
        "partner": "STO408",
        "ownType": "FRAN",
        "locationType": "ROAD",
        "brand": "<>",
        "openDate": "07/11/2014",
        "closeDate": "",
        "latitude": "59.855422",
        "longitude": "30.422252",
        "type": "АЗС",
        "timeZone": "0",
        "services": [],
        "phone": "78005553535",
        "height_post": "10.05",
        "working_time": [
          {
            "Weekday": "Saturday",
            "StartWorkTime": "01:00:00",
            "FinishWorkTime": "22:00:00"
          },
          {
            "Weekday": "Sunday",
            "StartWorkTime": "01:00:00",
            "FinishWorkTime": "21:00:00"
          }
        ],
        "prices": [
          {
            "ID": "3772",
            "GasStationID": "8792526",
            "GoodsCode": "00000000000003",
            "Price": "41",
            "Currency": "810;RUR",
            "DateTo": "2100-01-01T00:00:00",
            "DateFrom": "2017-11-25T00:03:12"
          },
          {
            "ID": "3770",
            "GasStationID": "8792526",
            "GoodsCode": "00000000000004",
            "Price": "37.5",
            "Currency": "810;RUR",
            "DateTo": "2100-01-01T00:00:00",
            "DateFrom": "2017-11-25T00:03:12"
          }
        ],
        "terminals": [],
        "address": {
          "track_id": null,
          "kmRoad": "",
          "roadSide": "Внешняя",
          "city": "г. Санкт-Петербург",
          "street": "ул. Софийская",
          "house": "69",
          "building": "",
          "phone": "+79013001843",
          "fax": ""
        },
        "searchTxt": "АЗС <> 050 г. Санкт-Петербург ул. Софийская "
      }
    ]
  },
  "timestamp": 1586308843
}
```

Вывод примера на этом ответе:

```text
366148  АЗС  регион 40  ООО СтопЭкcпресс
8792526  АЗС  регион 40  ООО СтопЭкcпресс
8792867  АЗС  регион 40  ООО СтопЭкcпресс
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`AzsListV1Response`](../../data-types/dictionaries/AzsListV1Response.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `AzsListV1Data | None` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`AzsListV1Data`](../../data-types/dictionaries/AzsListV1Data.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Количество найденных торговых точек |
| `result` | `data.result` | `list[AzsItemV1] | None` | Нет | Список торговых точек |

#### [`AzsItemV1`](../../data-types/dictionaries/AzsItemV1.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `str` | Да | ID торговой точки (АЗС) |
| `siebelId` | `data.result[].siebelId` | `str` | Да | ID торговой точки в CRM |
| `contractNumber` | `data.result[].contractNumber` | `str` | Да | Код торговой точки (договор) |
| `contractName` | `data.result[].contractName` | `str` | Да | Название торговой точки |
| `status` | `data.result[].status` | `str` | Да | Статус точки (257 – работает, 258 – не работает) |
| `countryCode` | `data.result[].countryCode` | `str` | Да | Код страны |
| `regionCode` | `data.result[].regionCode` | `str` | Да | Код региона |
| `secessionGPN` | `data.result[].secessionGPN` | `str | None` | Нет | Отделение ГПН по географии |
| `belongsTo` | `data.result[].belongsTo` | `str` | Да | Название владельца или оператора |
| `partner` | `data.result[].partner` | `str` | Да | ID партнера |
| `ownType` | `data.result[].ownType` | `str` | Да | Тип собственности (Own / FRAN и др.) |
| `locationType` | `data.result[].locationType` | `str | None` | Нет | Тип расположения (ROAD и т.д.) |
| `brand` | `data.result[].brand` | `str | None` | Нет | Бренд торговой точки |
| `openDate` | `data.result[].openDate` | `str` | Да | Дата открытия точки |
| `closeDate` | `data.result[].closeDate` | `str | None` | Нет | Дата закрытия (если закрыта) |
| `latitude` | `data.result[].latitude` | `str` | Да | Координата широты |
| `longitude` | `data.result[].longitude` | `str` | Да | Координата долготы |
| `type` | `data.result[].type` | `str` | Да | Тип торговой точки (АЗС, СТО и т.д.) |
| `timeZone` | `data.result[].timeZone` | `str | None` | Нет | Часовой пояс точки |
| `services` | `data.result[].services` | `list[int] | None` | Нет | Массив ID услуг |
| `terminals` | `data.result[].terminals` | `list[TerminalV1] | None` | Нет | Список терминалов торговой точки |
| `address` | `data.result[].address` | `AddressV1` | Да | Адрес торговой точки |
| `prices` | `data.result[].prices` | `list[PriceItemV1] | None` | Нет | Цены товаров на точке |
| `searchTxt` | `data.result[].searchTxt` | `str` | Да | Строка поиска |
| `phone` | `data.result[].phone` | `str | None` | Нет | Контактный телефон |
| `height_post` | `data.result[].height_post` | `str | None` | Нет | Высота поста (в метрах) |
| `working_time` | `data.result[].working_time` | `list[WorkingTimeV1] | None` | Нет | Режим работы |
| `only_virtual_card` | `data.result[].only_virtual_card` | `bool | None` | Нет | Принимаются ли только виртуальные карты |
| `accept_cards` | `data.result[].accept_cards` | `bool | None` | Нет | Принимаются ли карты |
| `hidden_on_map` | `data.result[].hidden_on_map` | `bool | None` | Нет | Скрыта ли точка на карте |
| `active` | `data.result[].active` | `bool | None` | Нет | Активна ли торговая точка |
| `POIType` | `data.result[].POIType` | `str | None` | Нет | Тип торговой точки (POI-код) |

#### [`TerminalV1`](../../data-types/dictionaries/TerminalV1.md) · `data.result[].terminals[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].terminals[].id` | `str` | Да | Идентификатор терминала |
| `active` | `data.result[].terminals[].active` | `bool` | Да | Статус активности терминала (True — включен, False — выключен) |
| `name` | `data.result[].terminals[].name` | `str` | Да | Наименование терминала |
| `status` | `data.result[].terminals[].status` | `str` | Да | Статус терминала |
| `type` | `data.result[].terminals[].type` | `str` | Да | Тип терминала |
| `connectionType` | `data.result[].terminals[].connectionType` | `str` | Да | Тип подключения терминала |
| `number` | `data.result[].terminals[].number` | `str` | Да | Номер терминала |

#### [`AddressV1`](../../data-types/dictionaries/AddressV1.md) · `data.result[].address`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `track_id` | `data.result[].address.track_id` | `str | None` | Нет | Номер трассы, если применимо |
| `kmRoad` | `data.result[].address.kmRoad` | `str | None` | Нет | Километр трассы |
| `roadSide` | `data.result[].address.roadSide` | `str | None` | Нет | Сторона дороги |
| `city` | `data.result[].address.city` | `str` | Да | Город |
| `street` | `data.result[].address.street` | `str | None` | Нет | Улица |
| `house` | `data.result[].address.house` | `str | None` | Нет | Дом |
| `building` | `data.result[].address.building` | `str | None` | Нет | Строение |
| `phone` | `data.result[].address.phone` | `str | None` | Нет | Телефон торговой точки |
| `fax` | `data.result[].address.fax` | `str | None` | Нет | Факс |

#### [`PriceItemV1`](../../data-types/dictionaries/PriceItemV1.md) · `data.result[].prices[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `ID` | `data.result[].prices[].ID` | `str` | Да | Идентификатор записи цены |
| `GasStationID` | `data.result[].prices[].GasStationID` | `str` | Да | ID торговой точки (АЗС) |
| `GoodsCode` | `data.result[].prices[].GoodsCode` | `str` | Да | Код товара (см. справочник GoodsCode) |
| `Price` | `data.result[].prices[].Price` | `str` | Да | Цена товара |
| `Currency` | `data.result[].prices[].Currency` | `str` | Да | Валюта (код и наименование через ';') |
| `DateTo` | `data.result[].prices[].DateTo` | `str` | Да | Дата окончания действия цены |
| `DateFrom` | `data.result[].prices[].DateFrom` | `str` | Да | Дата начала действия цены |

#### [`WorkingTimeV1`](../../data-types/dictionaries/WorkingTimeV1.md) · `data.result[].working_time[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `Weekday` | `data.result[].working_time[].Weekday` | `str` | Да | День недели или режим работы |
| `StartWorkTime` | `data.result[].working_time[].StartWorkTime` | `str | None` | Нет | Время открытия |
| `FinishWorkTime` | `data.result[].working_time[].FinishWorkTime` | `str | None` | Нет | Время закрытия |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** Фильтр содержит неизвестный код или значение неверного типа.

**Что делать:** Проверьте значения фильтра по справочникам.

Ответ API:

```json
{
  "status": {
    "code": 400,
    "errors": [
      {
        "type": "validationFailed",
        "message": "Некорректный фильтр"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
ValidationError: [400] Некорректные параметры запроса при выполнении get_azs_list_v1 Сообщение сервера: Некорректный фильтр. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.dictionaries.get_azs_list_v1(page=0)
```

Страницы нумеруются с 1. Исключение `pydantic.ValidationError`:

```text
1 validation error for AzsV1Query
page
  Input should be greater than or equal to 1 [type=greater_than_equal]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Поля ответа v1 названы в стиле camelCase (`countryCode`, `regionCode`), а в v2 — через подчёркивание.
