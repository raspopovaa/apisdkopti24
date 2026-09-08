---
description: Практические сценарии авторизации, работы с картами, документами и отчётами через apisdkopti24.
---

---
description: Практические сценарии авторизации, работы с картами, отчётами и ошибками в apisdkopti24.
---

# Типовые сценарии

Примеры используют условные идентификаторы и не содержат credentials. Перед
вызовом изменяющего метода проверьте его тарификацию и DEMO-доступность в
[каталоге методов](methods.md).

## Авторизация и получение карт

```python
from apisdkopti24 import ContractSelectionError

try:
    await client.auth.auth_user()
except ContractSelectionError as exc:
    for contract_id, contract_number in exc.available_contracts:
        print(contract_id, contract_number)
    selected_contract_id = input("Введите ID договора: ").strip()
    await client.auth.auth_user(contract_id=selected_contract_id)

cards = await client.cards.get_cards_v2(
    status="Active",
    page=1,
    onpage=20,
)
```

При первом подключении заранее знать договор не нужно. Единственный договор
выбирается автоматически. При нескольких договорах выберите ID из
`ContractSelectionError.available_contracts` и повторите авторизацию; SDK не
выбирает первый договор по порядку. После выбора contract-bound методы используют
договор из сессии, поэтому повторно передавать `contract_id` не требуется.
Session ID SDK хранит самостоятельно. Не выводите его в терминал и не передавайте
в telemetry.

## Защита утраченной карты

```python
await client.cards.block_card(
    contract_id="contract-id",
    card_ids=["card-id"],
    block=True,
)
```

Блокировка изменяет состояние карты. Если соединение оборвалось после отправки
запроса, сначала проверьте состояние карты, а не повторяйте операцию безусловно.

## Лимит и товарное ограничение

Если договор выбран при авторизации, `contract_id` подставляется из сессии.
Для работы с другим договором передайте его явно в метод.

```python
from apisdkopti24.models import LimitRequestItem, RestrictionRequestItem

await client.limits.set_limit(
    limits=[
        LimitRequestItem(
            card_id="card-id",
            sum={"currency": "810", "value": 5000.0},
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

Для изменения существующего лимита или ограничителя передавайте его `id`. Перед
созданием новой записи полезно запросить текущее состояние соответствующим GET-
методом.

Подробные правила aliases, response envelope и локальной валидации описаны в
[разделе договорных операций](section-2b.md).

## Заказ и получение отчёта

```python
available = await client.reports.get_reports()
print(available.data.total_count)

job = await client.reports.order_report(
    report_id="report-id",
    format="xlsx",
    params={
        "contract_id": "contract-id",
        "date_from": "2026-01-01",
        "date_to": "2026-01-31",
    },
)

jobs = await client.reports.get_report_jobs()
print(jobs.data.total_count)

report_path = await client.reports.download_report_file_to(
    job_id=job.data.job_id[0],
    destination="reports/report.xlsx",
)
```

Формирование файла выполняется асинхронно на стороне API. Не запускайте частый
polling: учитывайте rate limit и ожидаемое время подготовки отчёта. Binary download
использует ту же retry-политику, что и JSON, но только для безопасных и
идемпотентных операций.

## Приглашение и виртуальная карта

```python
invite = await client.invites.create_invite(
    data={
        "role": "Driver",
        "mobile": "79990000000",
        "contracts": [{"sid": "contract-id"}],
    },
    with_send=False,
)

card = await client.virtual_cards.release_virtual_card(
    template_id="template-id",
    user_id="user-id",
)
```

Сначала настройте шаблон лимитов и ограничений. В журналирование не должны
попадать телефон, ссылка приглашения и идентификаторы пользователя.

## Оплата по QR-коду

QR-оплата требует предварительно выпущенного и подтверждённого мобильного
профиля карты. Полный порядок вызовов, ограничения PIN и правила работы со
сроком действия платёжной строки приведены в разделе
[«Оплата по QR-коду»](qr-payments.md).
