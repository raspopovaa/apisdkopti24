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

SDK также различает локальные причины, которые раньше выглядели как общий
`ValueError` или `TypeError`:

| Исключение | Значение |
|---|---|
| `SDKConfigurationError` | Неверная конфигурация клиента до начала операции |
| `RequestValidationError` | Публичные параметры не прошли проверку SDK |
| `RequestPreparationError` | Параметр нельзя разместить в запросе этой операции |
| `ResponseTooLargeError` | Ответ превысил настроенный in-memory лимит |
| `ResponseShapeError` | Верхний уровень ответа имеет неожиданную структуру |
| `FileWriteError` | Файл не удалось безопасно сохранить |

Эти классы сохраняют совместимость с прежними обработчиками: ошибки конфигурации
и запроса наследуют `ValueError`, ошибка структуры — `TypeError`, а ошибка записи —
`OSError`.

## Читайте структурированный audit-журнал

Каждая операция, дошедшая до executor, завершается одним терминальным событием:

- `completed` — операция завершена успешно;
- `failed` — операция завершилась исключением;
- `cancelled` — async-задача отменена вызывающим приложением.

Для `failed` и `cancelled` JSONL-аудит содержит безопасные диагностические поля:

| Поле | Содержание |
|---|---|
| `operation_id` | Случайный локальный идентификатор, связывающий события одной операции |
| `elapsed_ms` | Длительность до terminal-события в миллисекундах |
| `attempts_used` | Число фактически начатых HTTP-попыток |
| `sdk_error_code` | Стабильный символьный код SDK |
| `error_source` | `api`, `network`, `response`, `sdk`, `configuration`, `validation`, `filesystem` или `application` |
| `exception_type` | Класс Python-исключения |
| `error_message` | Короткий очищенный текст без исходного payload |
| `http_status_code` | HTTP-код или `null`, если ответ не получен |
| `api_status_code` | `status.code` из ответа или `null` |
| `api_error_type` | Тип ошибки API или `null` |
| `transient` | Причина может быть временной независимо от конкретного метода |
| `retry_allowed` | Повтор допускается metadata конкретной `OperationSpec` |
| `retryable` | Совместимый alias поля `retry_allowed` |

`transient=true` не разрешает повтор. Для мутации после сетевого timeout сервер
мог применить изменение, даже если ответ не дошёл до клиента. Ориентируйтесь на
`retry_allowed`, которое уже учитывает `OperationSpec.retry_class` и
идемпотентность операции. Поле `retryable` оставлено для совместимости и содержит
то же operation-aware значение.

Основные локальные коды: `operation_timeout`, `retry_budget_exceeded`,
`network_timeout`, `network_error`, `response_too_large`,
`response_shape_invalid`, `response_validation_failed`, `file_write_failed`,
`filesystem_error`, `sdk_configuration_invalid`, `request_validation_failed`,
`request_preparation_failed`, `operation_cancelled` и `sdk_internal_error`. Ошибки API
используют коды `api_validation_failed`, `api_not_authenticated`,
`api_access_denied`, `api_not_found`, `api_duplicate_conflict`,
`api_rate_limited` и `api_server_error`.

Ошибки конфигурации, создание некорректного DTO и другие сбои до входа в executor
не являются API-операцией и автоматически в request audit не записываются. Их
должно обработать приложение на своей внешней границе. Аналогично `SKIPPED` в
интерактивном проверочном сценарии означает, что запрос не отправлялся.

Ожидаемые отказы (`400`, `401`, `403`, `404`, `409`, rate limit и локальная
валидация) записываются с уровнем `WARNING`; server/network/schema/filesystem и
неожиданные ошибки — с `ERROR`; отмена задачи — с `INFO`. Классификация уровня не
меняет Python-исключение: SDK всегда повторно выбрасывает исходный объект.

```python
try:
    await client.cards.get_cards_v2(page=0)
except Exception:
    # Внешняя граница приложения отвечает за ошибки, возникшие до SDK executor.
    application_logger.error("Вызов SDK завершился до отправки запроса")
    raise
```

Не добавляйте в такое сообщение объект исключения, параметры вызова, URL, payload
или credentials: текст стороннего validation exception может содержать исходное
значение поля.

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
`auth_user` имеет собственную audit-границу без auth-recovery: timeout, отмена,
API-ошибка и ошибка выбора договора завершаются ровно одним terminal-событием.

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
`ContractSelectionError` и не переключается на другой договор. В audit это
`contract_selection_failed`, но список доступных договоров туда не записывается.

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
