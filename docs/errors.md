---
description: Обработка HTTP- и API-ошибок, восстановления сессии и безопасных повторов в apisdkopti24.
---

# Ошибки и retry

SDK проверяет одновременно HTTP-статус и `payload.status.code`. Успешный код в
теле ответа не может скрыть HTTP-ошибку.

## Обработайте исключения API

| Код/тип | Исключение | Типичная причина |
|---|---|---|
| `400` | `ValidationError` | Некорректные параметры или payload |
| `401` | `NotAuthenticatedError` | Недействительная сессия или credentials |
| `403` | `AccessDeniedError` | Роль, API key, IP, договор или квота |
| `404` | `NotFoundError` | Объект или маршрут не найден |
| `409` | `DuplicateConflictError` | Повтор операции или конфликт |
| `429`, `509` | `RateLimitError` | Превышен лимит запросов |
| `5xx` | `ServerError` | Серверная ошибка |

Все перечисленные специализированные исключения наследуют `APIError`.

## Локальные ошибки execution policy

Ошибки общего бюджета операции не являются ответами API и не наследуют
`APIError`:

- `OperationTimeoutError` — исчерпан общий deadline бизнес-операции;
- `RetryBudgetExceededError` — исчерпан общий лимит HTTP-попыток.

```python
from apisdkopti24 import OperationTimeoutError, RetryBudgetExceededError

try:
    await client.cards.get_cards_v2()
except OperationTimeoutError:
    print("Общий deadline операции исчерпан")
except RetryBudgetExceededError:
    print("Лимит HTTP-попыток исчерпан")
```

Timeout каждой отдельной HTTP-попытки ограничивается оставшимся временем общего
deadline. Ожидание rate limit и retry backoff также должно помещаться в остаток
бюджета; SDK не начинает заведомо неуспевающее ожидание.

`OperationTimeoutError` не содержит HTTP- или API-код: сервер не успел вернуть
ответ. В audit-журнале такая ситуация получает символьный код
`operation_timeout`; назначать ей фиктивный HTTP `408` или `500` нельзя.

## Читайте структурированный audit-журнал

Каждая операция, дошедшая до executor, завершается одним терминальным событием:

- `completed` — операция завершена успешно;
- `failed` — операция завершилась исключением;
- `cancelled` — async-задача отменена вызывающим приложением.

Для `failed` и `cancelled` JSONL-аудит содержит безопасные диагностические поля:

| Поле | Содержание |
|---|---|
| `sdk_error_code` | Стабильный символьный код SDK |
| `error_source` | `api`, `network`, `sdk`, `validation`, `filesystem` или `application` |
| `exception_type` | Класс Python-исключения |
| `error_message` | Короткий очищенный текст без исходного payload |
| `http_status_code` | HTTP-код или `null`, если ответ не получен |
| `api_status_code` | `status.code` из ответа или `null` |
| `api_error_type` | Тип ошибки API или `null` |
| `retryable` | Признак допустимости повтора с точки зрения класса ошибки |

`retryable=true` не является разрешением безусловно повторять мутацию. Решение о
повторе по-прежнему зависит от `OperationSpec.retry_class` и idempotency операции.

Основные локальные коды: `operation_timeout`, `retry_budget_exceeded`,
`network_timeout`, `network_error`, `response_validation_failed`,
`filesystem_error`, `operation_cancelled` и `sdk_internal_error`. Ошибки API
используют коды `api_validation_failed`, `api_not_authenticated`,
`api_access_denied`, `api_not_found`, `api_duplicate_conflict`,
`api_rate_limited` и `api_server_error`.

Ошибки конфигурации, создание некорректного DTO и другие сбои до входа в executor
не являются API-операцией и автоматически в request audit не записываются. Их
должно обработать приложение на своей внешней границе. Аналогично `SKIPPED` в
интерактивном проверочном сценарии означает, что запрос не отправлялся.

## Ошибка выбора договора

`ContractSelectionError` наследует `ValueError`, а не `APIError`: это локальная
ошибка выбора контекста сессии, а не ошибка HTTP API.

Она возникает, когда:

- одновременно переданы `contract_id` и `contract_number`;
- указанный договор не найден;
- номер договора неоднозначен;
- доступно несколько договоров, но выбор не указан.

Доступные пары `(id, number)` находятся в `exc.available_contracts`. Они не
включаются в текст исключения, поэтому обычный `str(exc)` не раскрывает список
договоров в журнале.

```python
from apisdkopti24 import ContractSelectionError

try:
    await client.auth.auth_user()
except ContractSelectionError as exc:
    for contract_id, contract_number in exc.available_contracts:
        print(contract_id, contract_number)
    selected_contract_id = input("Введите ID договора: ").strip()
    await client.auth.auth_user(contract_id=selected_contract_id)
```

Не передавайте `available_contracts` во внешнюю telemetry без необходимости.
Первый вызов нужен для обнаружения договоров. При нескольких договорах повторная
авторизация с выбранным `contract_id` создаёт рабочий контекст сессии.

## Обработка ошибки API

```python
from apisdkopti24 import APIError, RateLimitError, ValidationError

try:
    cards = await client.cards.get_cards_v2(page=1, onpage=20)
except ValidationError as exc:
    print("Некорректный запрос:", exc.context.messages)
except RateLimitError as exc:
    print("Повтор возможен:", exc.context.retryable)
except APIError as exc:
    print("HTTP:", exc.context.http_status_code)
    print("API:", exc.context.api_status_code)
    print("Подсказка:", exc.context.hint)
```

!!! danger "Персональные данные"
    Полный ответ, возвращаемый явным вызовом `APIError.get_raw_payload()`, может
    содержать договорные или персональные данные. Не передавайте его в общие
    логи и внешнюю telemetry без очистки. Обычный `repr(exc.context)` raw payload
    не содержит.

## Учитывайте автоматический re-auth

Для защищённой операции SDK выполняет не более одного восстановления сессии и
одного повторного запроса. `auth_user` выполняется через низкоуровневый executor
без auth-recovery, поэтому рекурсивный захват session lock исключён.

Выбранный `contract_id` сохраняется при re-auth и повторно проверяется по
актуальному списку договоров. Если доступ к договору отозван, SDK возвращает
`ContractSelectionError` и не переключается на другой договор.

Повтор бизнес-запроса после re-auth использует тот же operation budget, поэтому
восстановление сессии не обнуляет deadline и счётчик попыток исходной операции.

## Настройте retry только для безопасных операций

Автоматический retry разрешён только если одновременно выполняются условия
`OperationSpec.retry_class` и `OperationSpec.idempotent`.

- безопасные операции чтения могут повторяться после временной сетевой ошибки;
- операции изменения не повторяются после неопределённого сетевого результата;
- `429` и `509` повторяются только для разрешённых policy операций;
- duplicate conflict не считается основанием для автоматического retry;
- JSON и binary download используют одну и ту же execution policy;
- задержка retry использует full jitter в диапазоне от нуля до текущего backoff cap.

## Примените безопасную обработку ошибок

1. Не добавляйте внешний retry вокруг всех вызовов без учёта idempotency.
2. Сохраняйте `method_name`, HTTP/API-коды и sanitized correlation data.
3. Не журналируйте credentials, session ID и исходный payload ошибки.
4. Для длительных сбоев используйте circuit breaker на уровне приложения.
