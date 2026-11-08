---
description: "Справочники OPTI 24: состав, поля, связи, какие ID куда передавать и особенности ответов сервера."
---

# Справочники

Справочники читаются методом [`dictionaries.get_dictionary(name=...)`](methods/dictionaries.md#clientdictionariesget_dictionary). Метод не тарифицируется, данные меняются редко: кешируйте их на сутки (см. [Практическое применение](practical-use.md)).

Числа записей и примеры ниже взяты из ответов тестового сервера OPTI 24 8 ноября 2026 года. На другом контуре и в другой день состав может отличаться.

## Состав

| Справочник | Записей | `id` | Поля записи | Назначение |
|---|---:|---|---|---|
| `CardStatus` | 20 | английский код: `Active`, `Locked(Client)` | `id`, `value`, `sid`, `active`, `last_update` | статусы карт |
| `ContractStatus` | 11 | английский код: `Active`, `Blocked SB` | `id`, `value`, `sid`, `active`, `last_update` | статусы договора и АЗС |
| `Country` | 35 | ISO 3166 alpha-3: `RUS` | `id`, `value`, `char` (alpha-2), `numeric`, `used`, `active` | страны |
| `Currency` | 8 | цифровой код ISO 4217: `810` | `id`, `code`, `name`, `short_name`, `active` | валюты |
| `Goods` | 23 | 14 цифр: `00000000000006` | `id`, `name`, `group_code`, `hex_color` | топливо в ценах АЗС |
| `PaymentScheme` | 9 | `1-…` | `id`, `value` (`7+7`, `30+15`), `code` (Постоплата/Предоплата), `active` | схемы оплаты договора |
| `PaymentTerm` | 2 | `1-…` | `id`, `value`, `code` (`Prepayment`/`Postpayment`), `active` | условия оплаты |
| `ProductType` | 6 | `1-…` | `id`, `code`, `name`, `unit`, `name_normal`, `active` | категории товаров |
| `ProductGroup` | 48 | `1-…` | `id`, `code`, `name`, `type`, `unit`, `type_structured`, `active` | группы товаров, в том числе виды топлива |
| `POIType` | 15 | число | `id`, `code`, `name`, `icon_url` | типы торговых точек |
| `Region` | 160 | код региона оператора: `50`, `BY-HO` | `id`, `name`, `country_id`, `type` (`STATE`/`CITY`), `active` | регионы |
| `Services` | 31 | число | `id`, `sid`, `code`, `name`, `sort`, `group_code`, `icon_url`, `active` | услуги на АЗС |
| `Unit` | 2 | `IT`, `LIT` | `id`, `value`, `active` | единицы измерения: штуки и литры |
| `Office` | 27 | `1-…` | адрес, координаты, телефон, email, график работы, `region`, `staff` | офисы продаж |
| `POIPartner` | 1421 | число | `id`, `code` (`STO…`, `NPO…`), `name`, `active`, `h2h_link_id` | партнёры — владельцы АЗС |
| `DiscountScheme` | 3 | `1-…` | `id`, `value`, `code` (`TRF_APPLY_I`/`_N`/`_Y`), `active` | схема расчёта скидки: индивидуальная, текущий или предыдущий месяц |
| `OwnType` | 6 | `1`…`6` | `id`, `code`, `type`, `name` | принадлежность АЗС: Газпромнефть, ОПТИ 24, франчайзинг, партнёр, аренда |

`OwnType` не входит в перечень спецификации, на него ссылается описание фильтров `get_azs_list_v1`.

## Какой ID куда передавать

| Нужно | Справочник | Пример |
|---|---|---|
| Продукт лимита, товарного ограничителя | `ProductGroup.id` (вид топлива) или `ProductType.id` (категория) | ДТ `1-CK237`, «Топливо» `1-CK231` |
| Регион регионального ограничения | `Region.id` | Новосибирская область `50` |
| Офис для заказа карт (`order_cards`) | `Office.id` | `1-13JW` |
| Топливо в ценах и фильтрах АЗС | `Goods.id` | ДТ `00000000000006` |
| Товары для `get_final_prices` | `Goods.id` | сервер принимает коды Goods; с ID категории `1-CK231` отвечает `400` «Услуга не найдена» |

С кодом Goods сервер принимает запрос `get_final_prices` и проверяет карту в процессинге: если на договоре не хватает денег, ответ `403` «ОТКАЗ. Недостаточно средств» с кодом процессинга `51` (`ProcessingRefusalError`). Успешный ответ с ценами SDK пока не видел; на тестовом контуре метод отвечает `500` без подробностей.

## Как получить ID в коде {#id-in-code}

Справочники бесплатны. Запросите их один раз при старте и найдите нужную запись по названию:

```python
types = await client.dictionaries.get_dictionary(name="ProductType")
groups = await client.dictionaries.get_dictionary(name="ProductGroup")

fuel_type = next(item.id for item in types.data.result if item.name == "Топливо")
diesel = next(item.id for item in groups.data.result if item.name == "ДТ" and item.active is not False)

limit = LimitRequestItem.model_validate(
    {
        "card_id": "card-id",
        "productType": fuel_type,     # 1-CK231 на тестовом сервере
        "productGroup": diesel,       # 1-CK237; без группы лимит действует на всё топливо
        "amount": {"value": 500, "unit": "LIT"},
        "time": {"number": 1, "type": 4},  # неделя
        "term": {"type": 1},
    }
)
```

Список всех групп с категорией: у записи `ProductGroup` поле `type` (в `item.model_extra`) — ID категории из `ProductType`, `type_structured` — вид: 6 — бензины, 7 — дизельное топливо, 8 — газ.

```python
for item in groups.data.result:
    if item.active is not False:
        print(item.id, item.name, (item.model_extra or {}).get("type"))
```

## Топливо: Goods и ProductGroup

Вид топлива имеет два разных ID. `Goods` используется в ценах АЗС (`prices[].GoodsCode`) и фильтрах `get_azs_filters`, `ProductGroup` — в лимитах, ограничителях и операциях. Общего ключа у них нет; таблица составлена по названиям.

| Топливо | `Goods.id` | `ProductGroup.id` и `code` |
|---|---|---|
| АИ-80 | `00000000000001` | `1-CK232` `FUEL80` |
| АИ-92 | `00000000000004` | `1-CK235` `FUEL92` |
| АИ-92 Премиум | `00000000000054` | `1-35FMHF5` `FUEL92PR` |
| АИ-92 ОПТИ | `00000000000024` | нет |
| АИ-93 | `00000000000040` | нет |
| АИ-95 | `00000000000003` | `1-CK234` `FUEL95` |
| АИ-95 Премиум | `00000000000053` | `1-35FMHF7` `FUEL95PR` |
| АИ-95 ОПТИ | `00000000000023` | нет |
| АИ-98 | `00000000000002` | `1-CK233` `FUEL98` |
| АИ-98 Премиум | нет | `1-35FWIX5` `FUEL98PR` |
| АИ-100 | `00000000000019` | `1-5A07K7A` `FUEL100` |
| G-92 | `00000000000011` | `1-CK23B` `FUELG92` |
| G-95 | `00000000000007` | `1-CK238` `FUELG95` |
| G-98 | `00000000000009` | `1-CK239` `FUELG98` |
| G-100 | `00000000000017` | `1-50GTO2W` `FUELG100` |
| G-100 с присадкой | `00000000000018` | нет |
| ДТ | `00000000000006` | `1-CK237` `FUELDT` |
| ДТ Премиум | `00000000000056` | `1-VF193` `FUELDTPR` |
| ДТ Зимнее | `00000000000021` | нет |
| ДТ ОПТИ | `00000000000008` | нет |
| G-ДТ | `00000000000010` | `1-CK23A` `FUELGDT` |
| СУГ | `00000000000005` | `1-CK236` `FUELSUG` |
| КПГ | `00000000000012` | `1-CK23C` `FUELKPG` |
| AdBlue | `9900000050678` | нет |

Группировки:

- `Goods.group_code`: `fuel` (бензины), `diesel`, `gaz`, `adblue`. Те же группы у фильтров `fuel`, `diesel`, `gaz`, `adblue` в `get_azs_filters`.
- `ProductGroup.type` ссылается на `ProductType.id`: Топливо `1-CK231`, Еда `1-C8J1M`, Кафе `1-C8J1I`, Товары `1-C8J1Z`, Услуги `1-C8J2B`, Услуги ГПН-РП `1-4SE0LKU`.
- `ProductGroup.type_structured`: 6 — бензины, 7 — дизельное топливо, 8 — газ, 2 — услуги, 3 — кафе, 4 — еда, 5 — товары; у услуг ГПН-РП `null`.

## Особенности ответов

- Ответ: `{"status": …, "data": {"total_count": N, "result": [...]}, "timestamp": …}`. `OwnType` отвечает иначе: `data.totalCount`, а `timestamp` внутри `data`; SDK принимает оба написания.
- Поля записей различаются между справочниками: в одних название в `value`, в других в `name`. Типизированы общие поля (`id`, `code`, `value`, `name`, `active`, `sid`, `last_update`); остальные доступны через `item.model_extra`.
- Признак удаления `deleted` в выгрузке тестового сервера 8 ноября 2026 года не пришёл ни в одном справочнике; актуальность записи показывает `active`. Пример ответа в спецификации 1.1.60 (`getDictionary?name=Unit`) содержит `deleted: 0`: источники расходятся, поэтому SDK принимает оба варианта.
- В `CardStatus` девять кодов (`Returned`, `Inactive`, `Locked(Manager)` и другие) встречаются дважды: старая запись с `active=false` и новая с `active=true`, у них разные `sid`. Для подписи статуса берите запись с `active=true`.
- `id` у `POIType` и `Services` числовой; SDK приводит его к строке.
- `Region.id` у регионов России — код оператора, а не код ГИБДД и не ISO: `50` — Новосибирская область, `46` — Московская область, `7110` — ХМАО. У Беларуси коды ISO 3166-2 (`BY-HO`). Этот же код приходит в `region_code` АЗС.
- В `Currency` рубль `643 RUB` помечен неактивным; в ценах АЗС и операциях валюта `810` (`RUR`).
- Справочника `GoodsCode`, на который ссылается описание фильтров `get_azs_list_v1`, сервер не знает (`404`).

## Справочники АЗС

`get_azs_filters` возвращает 11 фильтров со значениями `{code, name}`: `fuel`, `gaz`, `diesel`, `services_without_card`, `electric_charging_station`, `adblue`, `own_types`, `poi_types`, `payment_types` (`LKK`, `Plastic`, `OCR`, `LKP`, `TMB`, `NFC`), `countries` и `regions`. В фильтрах только страны и регионы, где есть точки: 6 стран и 119 регионов против 35 и 160 в справочниках.

| | `get_azs_list_v1` | `get_azs_list_v2` |
|---|---|---|
| Точек на тестовом контуре | 9489 | 8417 |
| Имена полей | camelCase: `siebelId`, `regionCode`, `ownType` | snake_case: `siebel_id`, `region_code`, `own_type_code` |
| `id` | числовой | числовой; у точек H2H без числового ID — `-` и Siebel ID, например `-1-ZYK56YO` |
| Цены | `prices[]`: `GoodsCode`, `Price`, `Currency`, `DateFrom`, `DateTo` | то же и `name`, `hex_color`, `sort` |
| Услуги | `services[]` | `services_with_card`, `services_without_card`, `adblue`, `electric_charging_station` — объекты `{name, items[]}` |

Цены есть примерно у трети точек. Принадлежность (`own_type_code` / `ownType`) — код из `OwnType`, тип точки (`poi_type_code` / `POIType`) — код из `POIType`, регион — `Region.id`.
