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
| `filter` | <code>AzsV2Filter &#124; Mapping[str, object] &#124; None</code> | Нет | `None` | JSON-объект для фильтрации списка торговых точек. |
| `q` | <code>str &#124; None</code> | Нет | `None` | Поисковая строка запроса (Ищет по наименованию АЗС и адресу) |
| `id` | <code>str &#124; None</code> | Нет | `None` | ID торговой точки. |
| `page` | <code>int &#124; None</code> | Нет | `None` | Номер страницы, начиная с 1. Задаётся вместе с on_page: сервер делит ответ на страницы только при обоих, поэтому один из них SDK отклоняет (RequestValidationError). Без обоих API возвращает всю сеть АЗС одним ответом. |
| `on_page` | <code>int &#124; None</code> | Нет | `None` | Количество точек на странице. Задаётся вместе с page. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`AzsV2Filter`](../../data-types/dictionaries/AzsV2Filter.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `services_with_card` | <code>list[str] &#124; None</code> | Нет | — | — |
| `services_without_card` | <code>list[str] &#124; None</code> | Нет | — | — |
| `own_types` | <code>list[str] &#124; None</code> | Нет | — | — |
| `payment_types` | <code>list[str] &#124; None</code> | Нет | — | — |
| `fuel` | <code>list[str] &#124; None</code> | Нет | — | — |
| `diesel` | <code>list[str] &#124; None</code> | Нет | — | — |
| `gaz` | <code>list[str] &#124; None</code> | Нет | — | — |
| `electric_charging_station` | <code>list[str] &#124; None</code> | Нет | — | — |
| `adblue` | <code>list[str] &#124; None</code> | Нет | — | — |
| `poi_types` | <code>list[str] &#124; None</code> | Нет | — | — |
| `countries` | <code>list[str] &#124; None</code> | Нет | — | — |
| `regions` | <code>list[str] &#124; None</code> | Нет | — | — |

#### [`AzsV2Query`](../../data-types/dictionaries/AzsV2Query.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `q` | <code>str &#124; None</code> | Нет | — | Поисковая строка запроса (Ищет по наименованию АЗС и адресу) |
| `id` | <code>str &#124; None</code> | Нет | минимальная длина: 1; — | ID точки АЗС |
| `page` | <code>int &#124; None</code> | Нет | минимум: 1; — | Номер страницы |
| `on_page` | <code>int &#124; None</code> | Нет | минимум: 1; — | Количество записей на странице |
| `filter` | <code>AzsV2Filter &#124; None</code> | Нет | — | JSON объект для фильтрации списка |

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

Модели ответа и путь к их полям в JSON.

#### [`AzsListV2Response`](../../data-types/dictionaries/AzsListV2Response.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>AzsListV2Data &#124; None</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`AzsListV2Data`](../../data-types/dictionaries/AzsListV2Data.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | <code>int</code> | Да | Общее количество торговых точек |
| `result` | `data.result` | <code>list[AzsItemV2]</code> | Да | Список торговых точек (АЗС) |

#### [`AzsItemV2`](../../data-types/dictionaries/AzsItemV2.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | <code>str</code> | Да | ID торговой точки |
| `siebel_id` | `data.result[].siebel_id` | <code>str</code> | Да | Идентификатор Siebel |
| `status` | `data.result[].status` | <code>str</code> | Да | Статус торговой точки (257 – работает, 258 – не работает) |
| `full_name` | `data.result[].full_name` | <code>str &#124; None</code> | Нет | Полное наименование торговой точки |
| `brand` | `data.result[].brand` | <code>str &#124; None</code> | Нет | Бренд |
| `poi_type_name` | `data.result[].poi_type_name` | <code>str &#124; None</code> | Нет | Именование типа |
| `poi_type_code` | `data.result[].poi_type_code` | <code>str &#124; None</code> | Нет | Код типа |
| `own_type_name` | `data.result[].own_type_name` | <code>str</code> | Да | Тип собственности (наименование) |
| `own_type_code` | `data.result[].own_type_code` | <code>str</code> | Да | Код типа собственности (по отношению к ГПН) |
| `contract_name` | `data.result[].contract_name` | <code>str &#124; None</code> | Нет | Название договора |
| `contract_number` | `data.result[].contract_number` | <code>str &#124; None</code> | Нет | Номер договора |
| `phone` | `data.result[].phone` | <code>str &#124; None</code> | Нет | Телефон контактный |
| `utc_timezone` | `data.result[].utc_timezone` | <code>str &#124; None</code> | Да | UTC часовой пояс АЗС (+5) |
| `time_zone` | `data.result[].time_zone` | <code>str &#124; None</code> | Нет | Часовой пояс АЗС относительно Москвы |
| `open_date` | `data.result[].open_date` | <code>str &#124; None</code> | Нет | Дата открытия (MM/DD/YYYY) |
| `close_date` | `data.result[].close_date` | <code>str &#124; None</code> | Нет | Дата закрытия (MM/DD/YYYY) |
| `last_update` | `data.result[].last_update` | <code>str &#124; None</code> | Нет | Дата последнего обновления |
| `height_post` | `data.result[].height_post` | <code>str &#124; None</code> | Нет | Высота поста (в метрах) |
| `country_name` | `data.result[].country_name` | <code>str &#124; None</code> | Да | Название страны |
| `country_code` | `data.result[].country_code` | <code>str &#124; None</code> | Да | Код страны |
| `region_name` | `data.result[].region_name` | <code>str &#124; None</code> | Нет | Название региона |
| `region_code` | `data.result[].region_code` | <code>str &#124; None</code> | Нет | Код региона |
| `address_full` | `data.result[].address_full` | <code>str &#124; None</code> | Нет | Полный адрес торговой точки |
| `location` | `data.result[].location` | <code>Coordinates &#124; None</code> | Нет | Географические координаты |
| `latitude` | `data.result[].latitude` | <code>str &#124; None</code> | Нет | Широта |
| `longitude` | `data.result[].longitude` | <code>str &#124; None</code> | Нет | Долгота |
| `location_type` | `data.result[].location_type` | <code>str &#124; None</code> | Нет | Тип локации |
| `secession_gpn` | `data.result[].secession_gpn` | <code>str &#124; None</code> | Нет | Отделение ГПН |
| `partner` | `data.result[].partner` | <code>str &#124; None</code> | Нет | ID партнёра |
| `belongs_to` | `data.result[].belongs_to` | <code>str &#124; None</code> | Нет | Принадлежность |
| `info` | `data.result[].info` | <code>str &#124; None</code> | Нет | Дополнительная информация о точке |
| `search_txt` | `data.result[].search_txt` | <code>str &#124; None</code> | Да | Строка для запроса поиска |
| `accept_cards` | `data.result[].accept_cards` | <code>bool &#124; None</code> | Да | Принимаются ли банковские карты |
| `adblue` | `data.result[].adblue` | <code>ServiceGroup &#124; None</code> | Нет | Услуги AdBlue |
| `electric_charging_station` | `data.result[].electric_charging_station` | <code>ServiceGroup &#124; None</code> | Нет | Электрозарядные станции |
| `services_with_card` | `data.result[].services_with_card` | <code>ServiceGroup &#124; None</code> | Нет | Услуги, доступные при оплате картой |
| `services_without_card` | `data.result[].services_without_card` | <code>ServiceGroup &#124; None</code> | Нет | Услуги, доступные без карты |
| `prices` | `data.result[].prices` | <code>list[PriceItemV2] &#124; None</code> | Нет | Список товаров с указанием цен |
| `payment_type` | `data.result[].payment_type` | <code>list[PaymentType] &#124; None</code> | Нет | Доступные способы оплаты |
| `terminals` | `data.result[].terminals` | <code>list[TerminalV2] &#124; None</code> | Нет | Список терминалов |
| `address` | `data.result[].address` | <code>AddressV2 &#124; None</code> | Нет | Адрес торговой точки |
| `working_time` | `data.result[].working_time` | <code>list[WorkingTimeV2] &#124; None</code> | Нет | Расписание работы торговой точки |

#### [`Coordinates`](../../data-types/dictionaries/Coordinates.md) · `data.result[].location`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `type` | `data.result[].location.type` | <code>str &#124; None</code> | Нет | Тип геоданных (обычно 'Point') |
| `coordinates` | `data.result[].location.coordinates` | <code>list[float]</code> | Нет | Координаты в формате [долгота, широта] |

#### [`ServiceGroup`](../../data-types/dictionaries/ServiceGroup.md) · `data.result[].adblue`

Та же модель описывает и `data.result[].electric_charging_station`, `data.result[].services_with_card`, `data.result[].services_without_card`.

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `name` | `data.result[].adblue.name` | <code>str</code> | Да | Наименование группы услуг |
| `items` | `data.result[].adblue.items` | <code>list[ServiceItem]</code> | Да | Список услуг, входящих в группу |

#### [`PriceItemV2`](../../data-types/dictionaries/PriceItemV2.md) · `data.result[].prices[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `ID` | `data.result[].prices[].ID` | <code>str &#124; None</code> | Нет | Идентификатор цены |
| `GasStationID` | `data.result[].prices[].GasStationID` | <code>str &#124; None</code> | Нет | ID торговой точки (АЗС) |
| `GoodsCode` | `data.result[].prices[].GoodsCode` | <code>str &#124; None</code> | Нет | Код товара (из справочника GoodsCode) |
| `Price` | `data.result[].prices[].Price` | <code>str &#124; None</code> | Нет | Цена товара |
| `Currency` | `data.result[].prices[].Currency` | <code>str &#124; None</code> | Нет | Код валюты, например '810;RUR' |
| `DateTo` | `data.result[].prices[].DateTo` | <code>str &#124; None</code> | Нет | Дата действия цены до |
| `DateFrom` | `data.result[].prices[].DateFrom` | <code>str &#124; None</code> | Нет | Дата начала действия цены |
| `hex_color` | `data.result[].prices[].hex_color` | <code>str &#124; None</code> | Нет | HEX-код цвета товара (если указан) |
| `name` | `data.result[].prices[].name` | <code>str &#124; None</code> | Нет | Название товара |
| `CurrencyName` | `data.result[].prices[].CurrencyName` | <code>str &#124; None</code> | Нет | Наименование валюты |
| `sort` | `data.result[].prices[].sort` | <code>int &#124; None</code> | Нет | Порядковый номер отображения |

#### [`PaymentType`](../../data-types/dictionaries/PaymentType.md) · `data.result[].payment_type[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `data.result[].payment_type[].code` | <code>str &#124; None</code> | Нет | Код способа оплаты |
| `name` | `data.result[].payment_type[].name` | <code>str &#124; None</code> | Нет | Название способа оплаты |

#### [`TerminalV2`](../../data-types/dictionaries/TerminalV2.md) · `data.result[].terminals[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].terminals[].id` | <code>str &#124; None</code> | Нет | Идентификатор терминала |
| `active` | `data.result[].terminals[].active` | <code>bool &#124; None</code> | Нет | Активен ли терминал (true — включен) |
| `name` | `data.result[].terminals[].name` | <code>str &#124; None</code> | Нет | Наименование терминала |
| `status` | `data.result[].terminals[].status` | <code>str &#124; None</code> | Нет | Статус терминала |
| `type` | `data.result[].terminals[].type` | <code>str &#124; None</code> | Нет | Тип терминала |
| `connectionType` | `data.result[].terminals[].connectionType` | <code>str &#124; None</code> | Нет | Тип подключения |
| `number` | `data.result[].terminals[].number` | <code>str &#124; None</code> | Нет | Номер терминала |

#### [`AddressV2`](../../data-types/dictionaries/AddressV2.md) · `data.result[].address`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `track_id` | `data.result[].address.track_id` | <code>str &#124; None</code> | Нет | Номер трассы |
| `kmRoad` | `data.result[].address.kmRoad` | <code>str &#124; None</code> | Нет | Километр трассы |
| `roadSide` | `data.result[].address.roadSide` | <code>str &#124; None</code> | Нет | Сторона дороги |
| `city` | `data.result[].address.city` | <code>str &#124; None</code> | Нет | Город |
| `street` | `data.result[].address.street` | <code>str &#124; None</code> | Нет | Улица |
| `house` | `data.result[].address.house` | <code>str &#124; None</code> | Нет | Дом |
| `building` | `data.result[].address.building` | <code>str &#124; None</code> | Нет | Строение |
| `phone` | `data.result[].address.phone` | <code>str &#124; None</code> | Нет | Телефон |
| `fax` | `data.result[].address.fax` | <code>str &#124; None</code> | Нет | Факс |

#### [`WorkingTimeV2`](../../data-types/dictionaries/WorkingTimeV2.md) · `data.result[].working_time[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `Weekday` | `data.result[].working_time[].Weekday` | <code>str &#124; None</code> | Нет | День недели или режим работы (Monday, Everyday, Round-The-Clock) |
| `StartWorkTime` | `data.result[].working_time[].StartWorkTime` | <code>str &#124; None</code> | Нет | Время открытия, формат HH:MM |
| `FinishWorkTime` | `data.result[].working_time[].FinishWorkTime` | <code>str &#124; None</code> | Нет | Время закрытия, формат HH:MM |
| `Everyday` | `data.result[].working_time[].Everyday` | <code>bool</code> | Да | Признак работы ежедневно |
| `Round-The-Clock` | `data.result[].working_time[].Round-The-Clock` | <code>bool</code> | Да | Признак круглосуточного режима |

#### [`ServiceItem`](../../data-types/dictionaries/ServiceItem.md) · `data.result[].adblue.items[]`

Та же модель описывает и `data.result[].electric_charging_station.items[]`, `data.result[].services_with_card.items[]`, `data.result[].services_without_card.items[]`.

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `name` | `data.result[].adblue.items[].name` | <code>str</code> | Да | Наименование услуги |
| `code` | `data.result[].adblue.items[].code` | <code>int &#124; str</code> | Да | Код услуги (числовой или строковый) |
| `sort` | `data.result[].adblue.items[].sort` | <code>int &#124; None</code> | Нет | Порядок сортировки |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

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
await client.dictionaries.get_azs_list_v2(on_page=1000)
```

Без `page` сервер игнорирует `on_page` и возвращает всю сеть, поэтому SDK требует оба параметра вместе. Исключение `RequestValidationError`:

```text
page и on_page задаются вместе: сервер без одного из них возвращает всю сеть АЗС
```

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

## Что важно знать

- `filter` можно передать словарём или моделью `AzsV2Filter`. SDK проверяет его моделью и отправляет строкой JSON в параметре запроса `filter`.
- Коды для фильтров возвращает `get_azs_filters()`.
- Всегда передавайте оба параметра — `page` и `on_page`. Сервер делит ответ на страницы только при обоих; вызов с одним из них SDK отклоняет до запроса (`RequestValidationError`). Без обоих параметров или с очень большим `on_page` API возвращает всю сеть АЗС одним ответом (около 30 МБ). Он больше предела `API_MAX_JSON_RESPONSE_BYTES` (16 МиБ по умолчанию), и SDK прерывает чтение с `ResponseTooLargeError`.
- Чтобы выгрузить все АЗС, листайте страницы: `page=1, 2, …` с `on_page=1000`, пока не наберёте `data.total_count` точек. Страница из 1000 точек весит около 4 МБ, вся сеть — около 8 бесплатных запросов. Другой способ — один запрос без `page` и `on_page` с поднятым `API_MAX_JSON_RESPONSE_BYTES` (например, 64 МиБ); тогда весь ответ целиком хранится в памяти.
- Если на точке нет услуг группы (`electric_charging_station`, `adblue`, `services_with_card`, `services_without_card`), API присылает пустой массив `[]` вместо объекта; SDK превращает его в `None`.
- Параметр `page`, `on_page`: ответ делится на страницы только при обоих; без одного из них — вся сеть АЗС (около 30 МБ). В SDK — требует оба параметра вместе или ни одного (`RequestValidationError`).
- Поле `data.result[].utc_timezone`: `null` у части АЗС. Тип в модели SDK: <code>str &#124; None</code>.
- Поле `data.result[].id`, `siebel_id`: строки. Тип в модели SDK: `str`.
- Поле коды в `adblue`, `services_with_card`, `services_without_card`: строки. Тип в модели SDK: <code>int &#124; str</code>.
- Поле `electric_charging_station`, `adblue`, `services_with_card`, `services_without_card`: `[]`, если услуг нет. Тип в модели SDK: пустой список приводится к `None`.
