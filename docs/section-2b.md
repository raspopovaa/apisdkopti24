# Договорные операции и ограничения

Раздел соответствует спецификации API для корпоративных клиентов версии
**1.1.60**. Он описывает сервисы `contracts`, `ewallet`, `limits`,
`region_limits`, `restrictions` и `templates`. QR/MPC-операции в этот контракт
не входят.

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
`ContractDataResponse`, а `set_region_limit()` — `RegionLimitSetResponse`.

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
from api_client_opti24.models import LimitRequestItem, RestrictionRequestItem

await client.limits.set_limit(
    limits=[
        LimitRequestItem(
            card_id="card-id",
            productType="product-type-id",
            sum={"currency": "810", "value": 5000},
            time={"number": 1, "type": 5},
        )
    ]
)

await client.restrictions.set_restriction(
    restrictions=[
        RestrictionRequestItem(
            card_id="card-id",
            productType="product-type-id",
            restriction_type=1,
        )
    ]
)
```

Wire-имена `productType` и `productGroup` поддерживаются как aliases.
`RegionLimitRequestItem` принимает существующий ID как `id` или
`regionlimit_id`, но сериализует его в поле `id`, указанное спецификацией для
установки лимита.

`card_id` и `group_id` взаимоисключающие. Для операций установки одного из них
достаточно и обязательно.

## Денежные операции

`order_invoice()`, `move_to_card()` и `move_to_contract()` принимают `Decimal`.
SDK проверяет положительное значение и отправляет сумму строкой без промежуточного
преобразования в `float`:

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
- положительные `page`, `on_page`, `count` и денежные суммы;
- непустые идентификаторы;
- формат документов `pdf` или `xlsx`;
- непустой список документов и от одного до пяти корректных email;
- допустимые значения типов, явно перечисленные в спецификации.

Ошибка в этих данных приводит к `ValueError` или Pydantic `ValidationError` и не
расходует запрос к API.
