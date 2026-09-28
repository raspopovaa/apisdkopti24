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
| `status` | `status` | `ResponseStatus` | Да | Статус ответа API |
| `data` | `data` | `AzsListV2Data | None` | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | `int | None` | Нет | Метка времени ответа API |

#### [`AzsListV2Data`](../../data-types/dictionaries/AzsListV2Data.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `total_count` | `data.total_count` | `int` | Да | Общее количество торговых точек |
| `result` | `data.result` | `list[AzsItemV2]` | Да | Список торговых точек (АЗС) |

#### [`AzsItemV2`](../../data-types/dictionaries/AzsItemV2.md) · `data.result[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].id` | `str` | Да | ID торговой точки |
| `siebel_id` | `data.result[].siebel_id` | `str` | Да | Идентификатор Siebel |
| `status` | `data.result[].status` | `str` | Да | Статус торговой точки (257 – работает, 258 – не работает) |
| `full_name` | `data.result[].full_name` | `str | None` | Нет | Полное наименование торговой точки |
| `brand` | `data.result[].brand` | `str | None` | Нет | Бренд |
| `poi_type_name` | `data.result[].poi_type_name` | `str | None` | Нет | Именование типа |
| `poi_type_code` | `data.result[].poi_type_code` | `str | None` | Нет | Код типа |
| `own_type_name` | `data.result[].own_type_name` | `str` | Да | Тип собственности (наименование) |
| `own_type_code` | `data.result[].own_type_code` | `str` | Да | Код типа собственности (по отношению к ГПН) |
| `contract_name` | `data.result[].contract_name` | `str | None` | Нет | Название договора |
| `contract_number` | `data.result[].contract_number` | `str | None` | Нет | Номер договора |
| `phone` | `data.result[].phone` | `str | None` | Нет | Телефон контактный |
| `utc_timezone` | `data.result[].utc_timezone` | `str | None` | Да | UTC часовой пояс АЗС (+5) |
| `time_zone` | `data.result[].time_zone` | `str | None` | Нет | Часовой пояс АЗС относительно Москвы |
| `open_date` | `data.result[].open_date` | `str | None` | Нет | Дата открытия (MM/DD/YYYY) |
| `close_date` | `data.result[].close_date` | `str | None` | Нет | Дата закрытия (MM/DD/YYYY) |
| `last_update` | `data.result[].last_update` | `str | None` | Нет | Дата последнего обновления |
| `height_post` | `data.result[].height_post` | `str | None` | Нет | Высота поста (в метрах) |
| `country_name` | `data.result[].country_name` | `str | None` | Да | Название страны |
| `country_code` | `data.result[].country_code` | `str | None` | Да | Код страны |
| `region_name` | `data.result[].region_name` | `str | None` | Нет | Название региона |
| `region_code` | `data.result[].region_code` | `str | None` | Нет | Код региона |
| `address_full` | `data.result[].address_full` | `str | None` | Нет | Полный адрес торговой точки |
| `location` | `data.result[].location` | `Coordinates | None` | Нет | Географические координаты |
| `latitude` | `data.result[].latitude` | `str | None` | Нет | Широта |
| `longitude` | `data.result[].longitude` | `str | None` | Нет | Долгота |
| `location_type` | `data.result[].location_type` | `str | None` | Нет | Тип локации |
| `secession_gpn` | `data.result[].secession_gpn` | `str | None` | Нет | Отделение ГПН |
| `partner` | `data.result[].partner` | `str | None` | Нет | ID партнёра |
| `belongs_to` | `data.result[].belongs_to` | `str | None` | Нет | Принадлежность |
| `info` | `data.result[].info` | `str | None` | Нет | Дополнительная информация о точке |
| `search_txt` | `data.result[].search_txt` | `str | None` | Да | Строка для запроса поиска |
| `accept_cards` | `data.result[].accept_cards` | `bool | None` | Да | Принимаются ли банковские карты |
| `adblue` | `data.result[].adblue` | `ServiceGroup | None` | Нет | Услуги AdBlue |
| `electric_charging_station` | `data.result[].electric_charging_station` | `ServiceGroup | None` | Нет | Электрозарядные станции |
| `services_with_card` | `data.result[].services_with_card` | `ServiceGroup | None` | Нет | Услуги, доступные при оплате картой |
| `services_without_card` | `data.result[].services_without_card` | `ServiceGroup | None` | Нет | Услуги, доступные без карты |
| `prices` | `data.result[].prices` | `list[PriceItemV2] | None` | Нет | Список товаров с указанием цен |
| `payment_type` | `data.result[].payment_type` | `list[PaymentType] | None` | Нет | Доступные способы оплаты |
| `terminals` | `data.result[].terminals` | `list[TerminalV2] | None` | Нет | Список терминалов |
| `address` | `data.result[].address` | `AddressV2 | None` | Нет | Адрес торговой точки |
| `working_time` | `data.result[].working_time` | `list[WorkingTimeV2] | None` | Нет | Расписание работы торговой точки |

#### [`Coordinates`](../../data-types/dictionaries/Coordinates.md) · `data.result[].location`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `type` | `data.result[].location.type` | `str | None` | Нет | Тип геоданных (обычно 'Point') |
| `coordinates` | `data.result[].location.coordinates` | `list[float]` | Нет | Координаты в формате [долгота, широта] |

#### [`ServiceGroup`](../../data-types/dictionaries/ServiceGroup.md) · `data.result[].adblue`

Та же модель описывает и `data.result[].electric_charging_station`, `data.result[].services_with_card`, `data.result[].services_without_card`.

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `name` | `data.result[].adblue.name` | `str` | Да | Наименование группы услуг |
| `items` | `data.result[].adblue.items` | `list[ServiceItem]` | Да | Список услуг, входящих в группу |

#### [`PriceItemV2`](../../data-types/dictionaries/PriceItemV2.md) · `data.result[].prices[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `ID` | `data.result[].prices[].ID` | `str | None` | Нет | Идентификатор цены |
| `GasStationID` | `data.result[].prices[].GasStationID` | `str | None` | Нет | ID торговой точки (АЗС) |
| `GoodsCode` | `data.result[].prices[].GoodsCode` | `str | None` | Нет | Код товара (из справочника GoodsCode) |
| `Price` | `data.result[].prices[].Price` | `str | None` | Нет | Цена товара |
| `Currency` | `data.result[].prices[].Currency` | `str | None` | Нет | Код валюты, например '810;RUR' |
| `DateTo` | `data.result[].prices[].DateTo` | `str | None` | Нет | Дата действия цены до |
| `DateFrom` | `data.result[].prices[].DateFrom` | `str | None` | Нет | Дата начала действия цены |
| `hex_color` | `data.result[].prices[].hex_color` | `str | None` | Нет | HEX-код цвета товара (если указан) |
| `name` | `data.result[].prices[].name` | `str | None` | Нет | Название товара |
| `CurrencyName` | `data.result[].prices[].CurrencyName` | `str | None` | Нет | Наименование валюты |
| `sort` | `data.result[].prices[].sort` | `int | None` | Нет | Порядковый номер отображения |

#### [`PaymentType`](../../data-types/dictionaries/PaymentType.md) · `data.result[].payment_type[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `data.result[].payment_type[].code` | `str | None` | Нет | Код способа оплаты |
| `name` | `data.result[].payment_type[].name` | `str | None` | Нет | Название способа оплаты |

#### [`TerminalV2`](../../data-types/dictionaries/TerminalV2.md) · `data.result[].terminals[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `id` | `data.result[].terminals[].id` | `str | None` | Нет | Идентификатор терминала |
| `active` | `data.result[].terminals[].active` | `bool | None` | Нет | Активен ли терминал (true — включен) |
| `name` | `data.result[].terminals[].name` | `str | None` | Нет | Наименование терминала |
| `status` | `data.result[].terminals[].status` | `str | None` | Нет | Статус терминала |
| `type` | `data.result[].terminals[].type` | `str | None` | Нет | Тип терминала |
| `connectionType` | `data.result[].terminals[].connectionType` | `str | None` | Нет | Тип подключения |
| `number` | `data.result[].terminals[].number` | `str | None` | Нет | Номер терминала |

#### [`AddressV2`](../../data-types/dictionaries/AddressV2.md) · `data.result[].address`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `track_id` | `data.result[].address.track_id` | `str | None` | Нет | Номер трассы |
| `kmRoad` | `data.result[].address.kmRoad` | `str | None` | Нет | Километр трассы |
| `roadSide` | `data.result[].address.roadSide` | `str | None` | Нет | Сторона дороги |
| `city` | `data.result[].address.city` | `str | None` | Нет | Город |
| `street` | `data.result[].address.street` | `str | None` | Нет | Улица |
| `house` | `data.result[].address.house` | `str | None` | Нет | Дом |
| `building` | `data.result[].address.building` | `str | None` | Нет | Строение |
| `phone` | `data.result[].address.phone` | `str | None` | Нет | Телефон |
| `fax` | `data.result[].address.fax` | `str | None` | Нет | Факс |

#### [`WorkingTimeV2`](../../data-types/dictionaries/WorkingTimeV2.md) · `data.result[].working_time[]`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `Weekday` | `data.result[].working_time[].Weekday` | `str | None` | Нет | День недели или режим работы (Monday, Everyday, Round-The-Clock) |
| `StartWorkTime` | `data.result[].working_time[].StartWorkTime` | `str | None` | Нет | Время открытия, формат HH:MM |
| `FinishWorkTime` | `data.result[].working_time[].FinishWorkTime` | `str | None` | Нет | Время закрытия, формат HH:MM |
| `Everyday` | `data.result[].working_time[].Everyday` | `bool` | Да | Признак работы ежедневно |
| `Round-The-Clock` | `data.result[].working_time[].Round-The-Clock` | `bool` | Да | Признак круглосуточного режима |

#### [`ServiceItem`](../../data-types/dictionaries/ServiceItem.md) · `data.result[].adblue.items[]`

Та же модель описывает и `data.result[].electric_charging_station.items[]`, `data.result[].services_with_card.items[]`, `data.result[].services_without_card.items[]`.

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `name` | `data.result[].adblue.items[].name` | `str` | Да | Наименование услуги |
| `code` | `data.result[].adblue.items[].code` | `int | str` | Да | Код услуги (числовой или строковый) |
| `sort` | `data.result[].adblue.items[].sort` | `int | None` | Нет | Порядок сортировки |

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
- Всегда передавайте `page` и `on_page`. Без них API возвращает всю сеть АЗС одним ответом; он больше предела `API_MAX_JSON_RESPONSE_BYTES` (16 МиБ по умолчанию), и SDK прерывает чтение с `ResponseTooLargeError`. Общее число точек — в `data.total_count`.
- Если на точке нет услуг группы (`electric_charging_station`, `adblue`, `services_with_card`, `services_without_card`), API присылает пустой массив `[]` вместо объекта; SDK превращает его в `None`.
- Поле `data.result[].utc_timezone`: `null` у части АЗС. Тип в модели SDK: `str | None`.
