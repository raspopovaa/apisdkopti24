# Миграция на SDK 3.0

SDK 3.0 вводит явные границы управления сессией, строгие batch-модели и общий
бюджет выполнения операции. Изменения несовместимы с частью кода линии 2.x,
поэтому требуют осознанной миграции.

!!! info "Релизная версия"
    Публичный контракт этого руководства соответствует `apisdkopti24 3.2.0`.

## Управление сессией

Свойства `session_id` и `contract_id` стали доступны только для чтения. Прямое
присваивание больше не поддерживается, потому что позволяло создавать
несогласованное состояние сессии.

### Восстановление доверенной сессии

Было:

```python
client.session_id = saved_session_id
client.contract_id = saved_contract_id
```

Стало:

```python
client.restore_session(
    session_id=saved_session_id,
    contract_id=saved_contract_id,
)
```

Метод принимает только полную пару идентификаторов и валидирует пустые значения.
Используйте его лишь для сессии, полученной из доверенного защищённого хранилища.

### Выбор договора

Было:

```python
client.contract_id = "contract-id"
```

Стало:

```python
client.select_contract(contract_id="contract-id")
```

Существующий `session_id` сохраняется, а новый договор применяется к последующим
запросам. Передаваемый договор должен быть доступен текущему пользователю.

### Очистка локальной сессии

Было:

```python
client.session_id = None
client.contract_id = None
```

Стало:

```python
client.clear_session()
```

`clear_session()` не вызывает серверный `logoff`. Для завершения серверной сессии
используйте `await client.auth.logoff()`; локальное состояние будет очищено даже
при ошибке ответа.

Контекстный менеджер закрывает только ресурсы клиента и не выполняет
автоматический серверный `logoff`:

```python
async with APIClient(...) as client:
    await client.cards.get_cards_v2()
```

## Владение transport

`APIClient` закрывает transport, который создал самостоятельно. Переданный извне
transport остаётся собственностью вызывающего кода:

```python
transport = AsyncTransport(...)
client = APIClient(..., transport=transport)
await client.aclose()
await transport.aclose()
```

Это позволяет безопасно разделять один transport между несколькими клиентами.

## Строгие batch-модели

Методы установки лимитов и ограничителей принимают только типизированные модели:

- `LimitRequestItem`;
- `RegionLimitRequestItem`;
- `RestrictionRequestItem`.

Было:

```python
await client.limits.set_limit(
    limits=[{"card_id": "card-id", "productType": "fuel", ...}],
)
```

Стало:

```python
from apisdkopti24.models.limits import LimitRequestItem

item = LimitRequestItem.model_validate(
    {
        "card_id": "card-id",
        "productType": "fuel",
        "amount": {"value": 100},
        "time": {"number": 1, "type": 5},
    }
)
await client.limits.set_limit(limits=[item])
```

SDK отклоняет пустой список, неверный тип элемента, одновременные `card_id` и
`group_id`, отсутствующую цель и смешанные договоры до выполнения HTTP-запроса.

## Deadline и retry budget

Один вызов публичного метода получает общий deadline и единый лимит HTTP-попыток.
В бюджет входят ожидание rate limit, сетевые retry и повтор бизнес-запроса после
восстановления сессии. Timeout отдельной попытки не превышает оставшееся время
операции.

Новые исключения доступны из корня пакета:

```python
from apisdkopti24 import OperationTimeoutError, RetryBudgetExceededError

try:
    await client.transactions.get_transactions_v2(...)
except OperationTimeoutError:
    ...
except RetryBudgetExceededError:
    ...
```

`OperationTimeoutError` означает исчерпание общего времени операции.
`RetryBudgetExceededError` означает исчерпание разрешённого числа HTTP-попыток.
Внешний безусловный retry после этих ошибок не рекомендуется: сначала проверьте
идемпотентность операции и причину исчерпания бюджета.
