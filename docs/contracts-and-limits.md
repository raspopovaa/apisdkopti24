---
description: Договорные операции, лимиты, ограничения и шаблоны корпоративного API топливных карт.
---

# Договорные операции и ограничения

Раздел описывает сервисы `contracts`, `ewallet`, `limits`, `region_limits`,
`restrictions` и `templates`. Операции МПК и QR описаны отдельно, в разделе
[«Оплата по QR-коду»](qr-payments.md).

## Выбор договора

После авторизации SDK сохраняет выбранный договор в сессии. Поэтому во всех
contract-bound методах `contract_id` можно не передавать:

```python
payments = await client.contracts.get_payments()
limits = await client.limits.get_limits(card_id="card-id")
templates = await client.templates.get_templates()
```

Явное значение имеет приоритет над договором сессии:

```python
payments = await client.contracts.get_payments(contract_id="other-contract-id")
```

Все публичные параметры этих сервисов являются keyword-only. Это не позволяет
случайно поменять местами идентификатор, сумму или версию API.

## Типизированные ответы

Методы возвращают полный response envelope со свойствами `status`, `data` и
`timestamp`. Например, `get_contract_data()` возвращает
`ContractDataResponse`, а `set_region_limit()`: `RegionLimitSetResponse`.

```python
contract = await client.contracts.get_contract_data()
print(contract.status.code)
print(contract.data.contractData.contract_number)
print(contract.timestamp)
```

SDK считает запрос успешным только при успешном HTTP-коде и, если он присутствует,
успешном `status.code` в payload.

## Строгие request-модели

Для изменяющих операций доступны модели `LimitRequestItem`,
`RegionLimitRequestItem` и `RestrictionRequestItem`. Неизвестные поля в них
отклоняются до отправки HTTP-запроса.

```python
from apisdkopti24.models import LimitRequestItem, RestrictionRequestItem

types = await client.dictionaries.get_dictionary(name="ProductType")
groups = await client.dictionaries.get_dictionary(name="ProductGroup")
fuel_id = next(item.id for item in types.data.result if item.name == "Топливо")
diesel_id = next(item.id for item in groups.data.result if item.name == "ДТ")
# на тестовом сервере 8 ноября 2026 года: «Топливо» 1-CK231, «ДТ» 1-CK237

await client.limits.set_limit(
    limits=[
        LimitRequestItem(
            card_id="card-id",
            productType=fuel_id,
            productGroup=diesel_id,             # без группы лимит общий на всё топливо
            sum={"currency": "810", "value": 5000},
            time={"number": 1, "type": 5},      # 5 — месяц, 4 — неделя, 3 — сутки
            term={"type": 1},                   # 1 — действует всегда
        )
    ]
)

await client.restrictions.set_restriction(
    restrictions=[
        RestrictionRequestItem(
            card_id="card-id",
            productType=fuel_id,
            productGroup=diesel_id,
            restriction_type=1,                 # 1 — разрешить, 2 — запретить
        )
    ]
)
```

Wire-имена `productType` и `productGroup` поддерживаются как aliases. `productType` — ID категории
из справочника `ProductType`, `productGroup` — ID вида топлива из `ProductGroup`; коды `Goods`
(`00000000000006`) сюда не подходят, они для цен АЗС. Подробнее — [Справочники](dictionaries.md).
`RegionLimitRequestItem` принимает существующий ID как `id` или
`regionlimit_id`, но сериализует его в поле `id`, которое API ожидает при
установке лимита.

### Изменение лимита

`set_limit()` с `id` существующего лимита меняет объём (`amount`) или сумму
(`sum`), но не период. Тестовый сервер 8 ноября 2026 года на смену `time.type`
с 3 (сутки) на 4 (неделя) и 7 (год) отвечал `200` с тем же ID, а `get_limits()`
по-прежнему возвращал `time.type = 3`. Создание лимита с периодом 4 или 7
работает. Чтобы сменить период, удалите лимит и создайте новый:

```python
await client.limits.remove_limit(limit_id=old_limit_id)
created = await client.limits.set_limit(limits=[new_limit])   # новый time.type
limits = await client.limits.get_limits(card_id="card-id")    # сверьте период
```

Пока старый лимит удалён, а новый ещё не создан, карта работает без этого
ограничения. Если `set_limit()` вернул ошибку, проверьте `get_limits()`: нового
лимита может не быть, и его нужно создать снова.

`card_id` и `group_id` взаимоисключающие. Для операций установки одного из них
достаточно и обязательно.

## Денежные операции

`order_invoice()`, `move_to_card()` и `move_to_contract()` принимают `Decimal`.
SDK проверяет, что сумма положительна и содержит не больше двух знаков после
запятой (`10.500` допустимо, `10.005`: нет), и отправляет её строкой без
промежуточного преобразования в `float`. Денежный лимит (`LimitSumRequest.value`)
проверяется так же:

```python
from decimal import Decimal

invoice = await client.contracts.order_invoice(
    amount=Decimal("15000.00"),
    email="billing@example.org",
)

transfer = await client.ewallet.move_to_card(
    card_id="card-id",
    amount=Decimal("2500.50"),
)
```

## Локальная валидация

До HTTP-вызова проверяются:

- даты в формате `YYYY-MM-DD` и порядок диапазона;
- положительные `page`, `on_page`, `count` и денежные суммы не больше чем с двумя
  знаками после запятой;
- непустые идентификаторы;
- формат документов `pdf` или `xlsx`;
- непустой список документов и от одного до пяти корректных email;
- допустимые значения типов, которые принимает API.

Ошибка во входных данных метода сервиса приводит к `RequestValidationError` (подклассу
`ValueError`). Это касается и простых параметров (идентификатор, дата, сумма, список), и
словарей, которые метод проверяет моделью запроса (например, `goods` в
`check_purchase`). Pydantic `ValidationError` возникает только там, где вызывающий код
сам создаёт модель запроса или вызывает `model_validate`. Проверка выполняется до входа
и не расходует запрос к API.
