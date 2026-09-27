---
description: "Поиск АЗС (API v2): пример client.dictionaries.get_azs_list_v2() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/dictionaries.yaml. Не редактируйте вручную. -->

# Поиск АЗС (API v2)

`client.dictionaries.get_azs_list_v2()` · [справочник метода](../../methods/dictionaries.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/dictionaries/get_azs_list_v2.py)

Найти торговые точки по фильтрам и строке поиска: адрес, бренд, тип точки, услуги и цены. Основной метод для поиска АЗС.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| GET | `v2/azs` | Нет | Нет | Нет | Да: при сетевой ошибке и ответе 429/509 |

## Пример

```python
"""Поиск АЗС (API v2): client.dictionaries.get_azs_list_v2().

Найти торговые точки по фильтрам и строке поиска: адрес, бренд, тип точки, услуги и
цены. Основной метод для поиска АЗС.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/dictionaries/get_azs_list_v2.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/dictionaries/get_azs_list_v2/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider


async def example(client: APIClient) -> None:
    response = await client.dictionaries.get_azs_list_v2(
        filter={"poi_types": ["AZS"], "countries": ["RUS"]}, q="Поспелиха", page=1, on_page=20
    )
    print(f"Найдено точек: {response.data.total_count}")
    for azs in response.data.result:
        print(f"{azs.id}  {azs.full_name}  {azs.address_full}")


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
| `filter` | `AzsV2Filter | Mapping[str, object] | None` | Нет | `None` | JSON-объект для фильтрации списка торговых точек. |
| `q` | `str | None` | Нет | `None` | Поисковая строка запроса (Ищет по наименованию АЗС и адресу) |
| `id` | `str | None` | Нет | `None` | ID точки АЗС |
| `page` | `int | None` | Нет | `None` | Номер страницы |
| `on_page` | `int | None` | Нет | `None` | Количество записей на странице |
| `api_version` | `str | None` | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`AzsV2Filter`](../../data-types/dictionaries/AzsV2Filter.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `services_with_card` | `list[str] | None` | Нет | — | — |
| `services_without_card` | `list[str] | None` | Нет | — | — |
| `own_types` | `list[str] | None` | Нет | — | — |
| `payment_types` | `list[str] | None` | Нет | — | — |
| `fuel` | `list[str] | None` | Нет | — | — |
| `diesel` | `list[str] | None` | Нет | — | — |
| `gaz` | `list[str] | None` | Нет | — | — |
| `electric_charging_station` | `list[str] | None` | Нет | — | — |
| `adblue` | `list[str] | None` | Нет | — | — |
| `poi_types` | `list[str] | None` | Нет | — | — |
| `countries` | `list[str] | None` | Нет | — | — |
| `regions` | `list[str] | None` | Нет | — | — |

#### [`AzsV2Query`](../../data-types/dictionaries/AzsV2Query.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `q` | `str | None` | Нет | — | Поисковая строка запроса (Ищет по наименованию АЗС и адресу) |
| `id` | `str | None` | Нет | минимальная длина: 1; — | ID точки АЗС |
| `page` | `int | None` | Нет | минимум: 1; — | Номер страницы |
| `on_page` | `int | None` | Нет | минимум: 1; — | Количество записей на странице |
| `filter` | `AzsV2Filter | None` | Нет | — | JSON объект для фильтрации списка |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
GET /vip/v2/azs?q=Поспелиха&page=1&on_page=20&filter={"poi_types":["AZS"],"countries":["RUS"]} HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
date_time: 2026-01-15 10:30:00
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `q` | строка запроса | `Поспелиха` | string | Нет | Поисковая строка запроса (Ищет по наименованию АЗС и адресу) |
| `page` | строка запроса | `1` | string | Нет | Номер страницы |
| `on_page` | строка запроса | `20` | string | Нет | Количество записей на странице |
| `filter` | строка запроса | `{"poi_types":["AZS"],"countries":["RUS"]}` | string | Нет | JSON объект для фильтрации списка |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`AzsListV2Response`](../../data-types/dictionaries/AzsListV2Response.md).
Пример ответа взят из спецификации API 1.1.60; списки сокращены до 2 элементов.

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "total_count": 3,
    "result": [
      {
        "id": "10805156",
        "siebel_id": "1-5ZZSIFT",
        "status": "257",
        "full_name": "АЗС 181 Газпромнефть",
        "brand": "Газпромнефть",
        "poi_type_name": "АЗС",
        "poi_type_code": "AZS",
        "own_type_name": "Франчайзинг Газпромнефть",
        "own_type_code": "FRAN",
        "contract_name": "181",
        "contract_number": "AZS106044",
        "phone": null,
        "working_time": [
          {
            "Weekday": null,
            "StartWorkTime": null,
            "FinishWorkTime": null,
            "Everyday": false,
            "Round-The-Clock": true
          }
        ],
        "utc_timezone": "+7",
        "time_zone": "+4",
        "open_date": "11/27/2017",
        "close_date": "11/23/2017",
        "last_update": "2025-04-25T03:19:42.000000Z",
        "height_post": null,
        "address": {
          "track_id": null,
          "kmRoad": "",
          "roadSide": "",
          "city": "Поспелиха",
          "street": "Объездная",
          "house": "19",
          "building": "",
          "phone": "",
          "fax": ""
        },
        "address_full": "Алтайский край, Поспелиха, М12,686км, справа, 19",
        "country_name": "Россия",
        "country_code": "RUS",
        "region_name": "Алтайский край",
        "region_code": "01",
        "location": {
          "type": "Point",
          "coordinates": [
            81.846248,
            51.990691
          ]
        },
        "longitude": "81.846248",
        "latitude": "51.990691",
        "location_type": "CITY_IND",
        "adblue": {
          "name": "AdBlue",
          "items": [
            {
              "name": "AdBlue фасованный",
              "code": "AdBlue фасованный",
              "sort": 2
            }
          ]
        },
        "electric_charging_station": {
          "name": "Электрозаправка",
          "items": [
            {
              "name": "Зарядка для электромобилей",
              "code": "Charging for electric vehicles",
              "sort": 500
            }
          ]
        },
        "services_with_card": [],
        "services_without_card": {
          "name": "Сервисы для водителей",
          "items": [
            {
              "name": "Вода",
              "code": "Water",
              "sort": null
            },
            {
              "name": "Кафе",
              "code": "Cafe",
              "sort": null
            }
          ]
        },
        "prices": [
          {
            "ID": "187946350",
            "GasStationID": "10805156",
            "GoodsCode": "00000000000004",
            "Price": "51.1",
            "Currency": "810;RUR",
            "DateTo": "2100-01-01T00:00:00",
            "DateFrom": "2024-07-23T19:58:49",
            "name": "АИ-92",
            "hex_color": "#fbbc17",
            "CurrencyName": "руб.",
            "sort": 1
          },
          {
            "ID": "192714130",
            "GasStationID": "10805156",
            "GoodsCode": "00000000000003",
            "Price": "58.8",
            "Currency": "810;RUR",
            "DateTo": "2100-01-01T00:00:00",
            "DateFrom": "2024-08-07T08:20:53",
            "name": "АИ-95",
            "hex_color": "#e63026",
            "CurrencyName": "руб.",
            "sort": 6
          }
        ],
        "payment_type": [
          {
            "code": "Plastic",
            "name": "Пластиковая карта"
          },
          {
            "code": "OCR",
            "name": "Показать QR-код"
          }
        ],
        "terminals": [
          {
            "id": "RF191811",
            "active": true,
            "name": "PAX_Q25",
            "status": "Работает",
            "type": "POS-ALL",
            "connectionType": "Сопряженный с СУ",
            "number": "RF191811"
          },
          {
            "id": "RF191812",
            "active": true,
            "name": "PAX_Q25",
            "status": "Работает",
            "type": "POS-ALL",
            "connectionType": "Сопряженный с СУ",
            "number": "RF191812"
          }
        ],
        "partner": "STO464",
        "belongs_to": "",
        "info": "ETALON=0000000740;",
        "search_txt": "АЗС Газпромнефть 181 Россия Алтайский край Поспелиха Объездная RF191811 RF191812 RF19181G",
        "secession_gpn": "Офис продаж в регионе Новосибирск",
        "accept_cards": false
      }
    ]
  },
  "timestamp": 1747722423
}
```

Вывод примера на этом ответе:

```text
Найдено точек: 3
10805156  АЗС 181 Газпромнефть  Алтайский край, Поспелиха, М12,686км, справа, 19
```

### Модели ответа

Модели ответа и путь к их полям в JSON. Колонка «В спецификации» — тип и обязательность поля по спецификации 1.1.60; `—` означает, что спецификация поле не описывает.

#### [`AzsListV2Response`](../../data-types/dictionaries/AzsListV2Response.md)

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `status` | `status` | `ResponseStatus` | Да | — | Статус ответа API |
| `data` | `data` | `AzsListV2Data | None` | Да | — | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | — | Метка времени ответа API |

#### [`AzsListV2Data`](../../data-types/dictionaries/AzsListV2Data.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `total_count` | `data.total_count` | `int` | Да | int, обязательное | Общее количество торговых точек |
| `result` | `data.result` | `list[AzsItemV2]` | Да | array, обязательное | Список торговых точек (АЗС) |

#### [`AzsItemV2`](../../data-types/dictionaries/AzsItemV2.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `id` | `data.result[].id` | `str` | Да | int, обязательное | ID торговой точки |
| `siebel_id` | `data.result[].siebel_id` | `str` | Да | int, обязательное | Идентификатор Siebel |
| `status` | `data.result[].status` | `str` | Да | string, обязательное | Статус торговой точки (257 – работает, 258 – не работает) |
| `full_name` | `data.result[].full_name` | `str | None` | Нет | string, необязательное | Полное наименование торговой точки |
| `brand` | `data.result[].brand` | `str | None` | Нет | string, необязательное | Бренд |
| `poi_type_name` | `data.result[].poi_type_name` | `str | None` | Нет | string, необязательное | Именование типа |
| `poi_type_code` | `data.result[].poi_type_code` | `str | None` | Нет | string, необязательное | Код типа |
| `own_type_name` | `data.result[].own_type_name` | `str` | Да | string, обязательное | Тип собственности (наименование) |
| `own_type_code` | `data.result[].own_type_code` | `str` | Да | string, обязательное | Код типа собственности (по отношению к ГПН) |
| `contract_name` | `data.result[].contract_name` | `str | None` | Нет | string, необязательное | Название договора |
| `contract_number` | `data.result[].contract_number` | `str | None` | Нет | string, необязательное | Номер договора |
| `phone` | `data.result[].phone` | `str | None` | Нет | string, необязательное | Телефон контактный |
| `utc_timezone` | `data.result[].utc_timezone` | `str | None` | Да | string, обязательное | UTC часовой пояс АЗС (+5) |
| `time_zone` | `data.result[].time_zone` | `str | None` | Нет | string, необязательное | Часовой пояс АЗС относительно Москвы |
| `open_date` | `data.result[].open_date` | `str | None` | Нет | string, необязательное | Дата открытия |
| `close_date` | `data.result[].close_date` | `str | None` | Нет | string, необязательное | Дата закрытия |
| `last_update` | `data.result[].last_update` | `str | None` | Нет | string, необязательное | Дата последнего обновления |
| `height_post` | `data.result[].height_post` | `str | None` | Нет | string, необязательное | Высота поста (в метрах) |
| `country_name` | `data.result[].country_name` | `str | None` | Да | string, обязательное | Название страны |
| `country_code` | `data.result[].country_code` | `str | None` | Да | string, обязательное | Код страны |
| `region_name` | `data.result[].region_name` | `str | None` | Нет | string, необязательное | Название региона |
| `region_code` | `data.result[].region_code` | `str | None` | Нет | string, необязательное | Код региона |
| `address_full` | `data.result[].address_full` | `str | None` | Нет | string, необязательное | Полный адрес торговой точки |
| `location` | `data.result[].location` | `Coordinates | None` | Нет | object, необязательное | Географические координаты |
| `latitude` | `data.result[].latitude` | `str | None` | Нет | string, необязательное | Широта |
| `longitude` | `data.result[].longitude` | `str | None` | Нет | string, необязательное | Долгота |
| `location_type` | `data.result[].location_type` | `str | None` | Нет | string, необязательное | Тип локации |
| `secession_gpn` | `data.result[].secession_gpn` | `str | None` | Нет | string, необязательное | Отделение ГПН |
| `partner` | `data.result[].partner` | `str | None` | Нет | string, необязательное | ID партнёра |
| `belongs_to` | `data.result[].belongs_to` | `str | None` | Нет | string, необязательное | Принадлежность |
| `info` | `data.result[].info` | `str | None` | Нет | string, необязательное | Дополнительная информация о точке |
| `search_txt` | `data.result[].search_txt` | `str | None` | Да | string, обязательное | Строка для запроса поиска |
| `accept_cards` | `data.result[].accept_cards` | `bool | None` | Да | bool, обязательное | Принимаются ли банковские карты |
| `adblue` | `data.result[].adblue` | `ServiceGroup | None` | Нет | object, необязательное | Услуги AdBlue |
| `electric_charging_station` | `data.result[].electric_charging_station` | `ServiceGroup | None` | Нет | object, необязательное | Электрозарядные станции |
| `services_with_card` | `data.result[].services_with_card` | `ServiceGroup | None` | Нет | object, необязательное | Услуги, доступные при оплате картой |
| `services_without_card` | `data.result[].services_without_card` | `ServiceGroup | None` | Нет | object, необязательное | Услуги, доступные без карты |
| `prices` | `data.result[].prices` | `list[PriceItemV2] | None` | Нет | array, необязательное | Список товаров с указанием цен |
| `payment_type` | `data.result[].payment_type` | `list[PaymentType] | None` | Нет | array, необязательное | Доступные способы оплаты |
| `terminals` | `data.result[].terminals` | `list[TerminalV2] | None` | Нет | array, необязательное | Список терминалов |
| `address` | `data.result[].address` | `AddressV2 | None` | Нет | object, необязательное | Адрес торговой точки |
| `working_time` | `data.result[].working_time` | `list[WorkingTimeV2] | None` | Нет | array, необязательное | Расписание работы торговой точки |

#### [`Coordinates`](../../data-types/dictionaries/Coordinates.md) · `data.result[].location`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `type` | `data.result[].location.type` | `str | None` | Нет | string, необязательное | Тип геоданных (обычно 'Point') |
| `coordinates` | `data.result[].location.coordinates` | `list[float]` | Нет | array[float], необязательное | Координаты в формате [долгота, широта] |

#### [`ServiceGroup`](../../data-types/dictionaries/ServiceGroup.md) · `data.result[].adblue`

Та же модель описывает и `data.result[].electric_charging_station`, `data.result[].services_with_card`, `data.result[].services_without_card`.

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `name` | `data.result[].adblue.name` | `str` | Да | string, обязательное | Наименование группы услуг |
| `items` | `data.result[].adblue.items` | `list[ServiceItem]` | Да | array, обязательное | Список услуг, входящих в группу |

#### [`PriceItemV2`](../../data-types/dictionaries/PriceItemV2.md) · `data.result[].prices[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `ID` | `data.result[].prices[].ID` | `str | None` | Нет | string, необязательное | Идентификатор цены |
| `GasStationID` | `data.result[].prices[].GasStationID` | `str | None` | Нет | string, необязательное | ID торговой точки (АЗС) |
| `GoodsCode` | `data.result[].prices[].GoodsCode` | `str | None` | Нет | string, необязательное | Код товара (из справочника GoodsCode) |
| `Price` | `data.result[].prices[].Price` | `str | None` | Нет | string, необязательное | Цена товара |
| `Currency` | `data.result[].prices[].Currency` | `str | None` | Нет | string, необязательное | Код валюты, например '810;RUR' |
| `DateTo` | `data.result[].prices[].DateTo` | `str | None` | Нет | string, необязательное | Дата действия цены до |
| `DateFrom` | `data.result[].prices[].DateFrom` | `str | None` | Нет | string, необязательное | Дата начала действия цены |
| `hex_color` | `data.result[].prices[].hex_color` | `str | None` | Нет | string, необязательное | HEX-код цвета товара (если указан) |
| `name` | `data.result[].prices[].name` | `str | None` | Нет | string, необязательное | Название товара |
| `CurrencyName` | `data.result[].prices[].CurrencyName` | `str | None` | Нет | string, необязательное | Наименование валюты |
| `sort` | `data.result[].prices[].sort` | `int | None` | Нет | int, необязательное | Порядковый номер отображения |

#### [`PaymentType`](../../data-types/dictionaries/PaymentType.md) · `data.result[].payment_type[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `code` | `data.result[].payment_type[].code` | `str | None` | Нет | string, необязательное | Код способа оплаты |
| `name` | `data.result[].payment_type[].name` | `str | None` | Нет | string, необязательное | Название способа оплаты |

#### [`TerminalV2`](../../data-types/dictionaries/TerminalV2.md) · `data.result[].terminals[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `id` | `data.result[].terminals[].id` | `str | None` | Нет | string, необязательное | Идентификатор терминала |
| `active` | `data.result[].terminals[].active` | `bool | None` | Нет | bool, необязательное | Активен ли терминал (true — включен) |
| `name` | `data.result[].terminals[].name` | `str | None` | Нет | string, необязательное | Наименование терминала |
| `status` | `data.result[].terminals[].status` | `str | None` | Нет | string, необязательное | Статус терминала |
| `type` | `data.result[].terminals[].type` | `str | None` | Нет | string, необязательное | Тип терминала |
| `connectionType` | `data.result[].terminals[].connectionType` | `str | None` | Нет | string, необязательное | Тип подключения |
| `number` | `data.result[].terminals[].number` | `str | None` | Нет | string, необязательное | Номер терминала |

#### [`AddressV2`](../../data-types/dictionaries/AddressV2.md) · `data.result[].address`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `track_id` | `data.result[].address.track_id` | `str | None` | Нет | string, необязательное | Номер трассы |
| `kmRoad` | `data.result[].address.kmRoad` | `str | None` | Нет | string, необязательное | Километр трассы |
| `roadSide` | `data.result[].address.roadSide` | `str | None` | Нет | string, необязательное | Сторона дороги |
| `city` | `data.result[].address.city` | `str | None` | Нет | string, необязательное | Город |
| `street` | `data.result[].address.street` | `str | None` | Нет | string, необязательное | Улица |
| `house` | `data.result[].address.house` | `str | None` | Нет | string, необязательное | Дом |
| `building` | `data.result[].address.building` | `str | None` | Нет | string, необязательное | Строение |
| `phone` | `data.result[].address.phone` | `str | None` | Нет | string, необязательное | Телефон |
| `fax` | `data.result[].address.fax` | `str | None` | Нет | string, необязательное | Факс |

#### [`WorkingTimeV2`](../../data-types/dictionaries/WorkingTimeV2.md) · `data.result[].working_time[]`

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `Weekday` | `data.result[].working_time[].Weekday` | `str | None` | Нет | string, необязательное | День недели или режим работы (Monday, Everyday, Round-The-Clock) |
| `StartWorkTime` | `data.result[].working_time[].StartWorkTime` | `str | None` | Нет | string, необязательное | Время открытия, формат HH:MM |
| `FinishWorkTime` | `data.result[].working_time[].FinishWorkTime` | `str | None` | Нет | string, необязательное | Время закрытия, формат HH:MM |
| `Everyday` | `data.result[].working_time[].Everyday` | `bool` | Да | bool, обязательное | Признак работы ежедневно |
| `Round-The-Clock` | `data.result[].working_time[].Round-The-Clock` | `bool` | Да | bool, обязательное | Признак круглосуточного режима |

#### [`ServiceItem`](../../data-types/dictionaries/ServiceItem.md) · `data.result[].adblue.items[]`

Та же модель описывает и `data.result[].electric_charging_station.items[]`, `data.result[].services_with_card.items[]`, `data.result[].services_without_card.items[]`.

| Поле | Путь в JSON | Python-тип | Обязательное | В спецификации | Описание |
|---|---|---|:---:|---|---|
| `name` | `data.result[].adblue.items[].name` | `str` | Да | string, обязательное | Наименование услуги |
| `code` | `data.result[].adblue.items[].code` | `int | str` | Да | int, обязательное | Код услуги (числовой или строковый) |
| `sort` | `data.result[].adblue.items[].sort` | `int | None` | Нет | int, необязательное | Порядок сортировки |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у реального API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 400 · `ValidationError`

**Почему:** В фильтре указан код, которого нет в списке фильтров.

**Что делать:** Возьмите коды из `get_azs_filters()`.

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
ValidationError: [400] Некорректные параметры запроса при выполнении get_azs_list_v2 Сообщение сервера: Некорректный фильтр. Подсказка: Проверьте структуру запроса и корректность передаваемых параметров.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.dictionaries.get_azs_list_v2(filter={"fuel_type": ["AI95"]})
```

Модель фильтра не знает поля `fuel_type`: SDK отклоняет неизвестные поля, чтобы опечатка не превратилась в поиск без фильтра. Исключение `pydantic.ValidationError`:

```text
1 validation error for AzsV2Query
filter.fuel_type
  Extra inputs are not permitted [type=extra_forbidden]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Особенности по спецификации

- Раздел спецификации 1.1.60: «Список торговых точек (v.2)». Запрос в спецификации: `GET http://localhost/vip/v2/azs`.
- Статус контракта — `provisional`: модели построены по спецификации, ответ реального API с ними ещё не сверен полностью. Если ответ не прошёл проверку модели, сообщите о расхождении.
- Реальный API отличается от спецификации: поле `data.result[].utc_timezone` — в спецификации строка, обязательное, фактически `null` у части АЗС. Тип в модели SDK: `str | None`.

Пример запроса из спецификации (секреты удалены при подготовке спецификации):

```text
GET http://localhost/vip/v2/azs?filter={"diesel":["00000000000006"],"poi_types":["AZS"]}&q=Москва
GET http://localhost/vip/v2/azs
GET http://localhost/vip/v2/azs?filter={"countries":["ROU","KAZ"]}
GET http://localhost/vip/v2/azs?filter={"regions":["KZ-KAR","92"]}
```

## Что важно знать

- `filter` можно передать словарём или моделью `AzsV2Filter`. SDK проверяет его моделью и отправляет строкой JSON в параметре запроса `filter`.
- Коды для фильтров возвращает `get_azs_filters()`.
