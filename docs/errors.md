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

`str(APIError)` содержит локальное сообщение по коду и текст, присланный
сервером в `status.errors[].message`, например:

```text
AccessDeniedError: [403] Доступ запрещён при выполнении delete_mpc Сообщение сервера: Невозможно деактивировать МПК. Подсказка: …
```

Перед выводом текст сервера очищается: удаляются управляющие символы, email,
телефоны и значения вида `ключ=значение`. Если сообщение упоминает PIN, пароль,
токен или другое чувствительное поле, оно заменяется на «Ответ API с ошибкой
содержал конфиденциальные данные». Берутся не больше пяти сообщений, каждое
обрезается до 500 символов. Очищенные сообщения доступны в
`APIError.server_messages`.

В `context.messages` и в audit остаётся только локальное сообщение: текст
сервера туда не попадает. Поле `error_type` содержит только известное имя ошибки
контракта либо `None`. Некорректные типы полей JSON не должны ломать обработку
ошибки. Исходный ответ целиком доступен только через `get_raw_payload()`; не
журналируйте этот результат.

`APIError.context.transient` описывает временный характер ответа; прежнее поле
`context.retryable` сохраняет тот же смысл и само по себе не разрешает повтор.
В audit поля `retry_allowed` и его alias `retryable` учитывают конкретную
операцию. Для решения о повторе используйте именно operation-aware значение.

Ошибки ISO-формата и диапазона дат выбрасываются как `RequestValidationError`,
без HTTP/API-кодов. Проверка периода транзакций выполняется до ленивой авторизации.

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
deadline. Ожидание свободного слота одновременных запросов, rate limit и retry
backoff также должно помещаться в остаток бюджета; SDK не начинает заведомо
неуспевающее ожидание. Если срок истёк, пока запрос ждал слот, запрос не
отправляется.

`OperationTimeoutError` не содержит HTTP- или API-код: это локальное исчерпание
общего лимита времени, в том числе при ожидании свободного слота, разрешённой частоты запросов,
задержки перед повтором или восстановления сессии. Оно не доказывает, что сервер
не получил запрос или не выполнил операцию. В audit-журнале эта ситуация получает код
`operation_timeout`; назначать ей фиктивный HTTP `408` или `500` нельзя.

## Сервер API недоступен

Если соединение с сервером API не установлено, SDK выбрасывает
`APIConnectionError`. Это происходит, когда исчерпаны попытки подключения или
общий deadline истёк, пока SDK пытался подключиться. Исходная ошибка httpx
(`ConnectError` или `ConnectTimeout`) сохраняется в `__cause__`, имя хоста — в
атрибуте `host`. В audit-журнале используется код `network_connect_failed`.

API принимает запросы только с IP-адресов
стран RU, BY, KZ, TJ, KG, IQ, AE и RS. С других адресов сервер не отвечает ни
HTTP-ошибкой, ни отказом в соединении, поэтому клиент видит только timeout
подключения. Отдельный лимит `TimeoutPolicy.connect` (по умолчанию `10.0` с)
не даёт такой попытке ждать полный timeout чтения.

```python
from apisdkopti24 import APIConnectionError

try:
    await client.auth.auth_user()
except APIConnectionError as error:
    print(f"{error.host} недоступен: проверьте сеть, VPN или прокси")
```

Ошибка возникает до получения ответа, поэтому API-кода у неё нет. Для мутации
сервер всё равно мог получить запрос, если соединение оборвалось после отправки;
ориентируйтесь на `retry_allowed`.

SDK также различает локальные причины, которые раньше выглядели как общий
`ValueError` или `TypeError`:

| Исключение | Значение |
|---|---|
| `SDKConfigurationError` | Неверная конфигурация клиента до начала операции |
| `RequestValidationError` | Публичные параметры не прошли проверку SDK |
| `RequestPreparationError` | Параметр нельзя разместить в запросе этой операции |
| `ResponseTooLargeError` | Ответ превысил настроенный in-memory лимит |
| `ResponseShapeError` | Верхний уровень ответа имеет неожиданную структуру |
| `ResponseValidationError` | Ответ не соответствует модели данных SDK |
| `FileWriteError` | Файл не удалось безопасно сохранить |

Эти классы сохраняют совместимость с прежними обработчиками: ошибки конфигурации,
запроса и модели ответа наследуют `ValueError`, ошибка структуры — `TypeError`, а
ошибка записи — `OSError`.

`ResponseValidationError` заменяет прежний `pydantic.ValidationError` при разборе
ответа. Текст исключения однострочный и не содержит значений из ответа; в
`problems` — пары «путь поля, тип ошибки» (до 50), в `problem_count` — общее число
ошибок, исходная ошибка Pydantic — в `__cause__`:

```python
from apisdkopti24 import ResponseValidationError

try:
    cards = await client.cards.get_cards_v1()
except ResponseValidationError as error:
    for location, kind in error.problems:
        print(f"{error.operation}: {location} — {kind}")
```

## Читайте структурированный audit-журнал

SDK формирует для каждой операции, дошедшей до executor, одно терминальное событие:

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
`network_connect_failed`, `network_timeout`, `network_error`, `response_too_large`,
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
    print("Ошибка может быть временной:", exc.context.transient)
    # Возможность повтора определяется политикой конкретной операции.
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

## Учитывайте автоматический re-auth {#re-auth}

Для защищённой операции SDK выполняет не более одного восстановления сессии и
одного повторного запроса. `auth_user` выполняется через низкоуровневый executor
без auth-recovery, поэтому рекурсивный захват session lock исключён.

Re-auth запускается, только если `401` вернул сам защищённый метод. Если
`authUser` при автоматической авторизации отклонил учётные данные с `401`,
операция сразу завершается `NotAuthenticatedError`: повторный вход дал бы тот же
отказ и ещё одну неудачную попытку входа на сервере.

Выбранный `contract_id` сохраняется при re-auth и повторно проверяется по
актуальному списку договоров. Если доступ к договору отозван, SDK возвращает
`ContractSelectionError` и не переключается на другой договор. В audit это
`contract_selection_failed`, но список доступных договоров туда не записывается.

Повтор бизнес-запроса после re-auth использует тот же operation budget, поэтому
восстановление сессии не обнуляет deadline и счётчик попыток исходной операции.

## Настройте повторы запросов {#retry}

Повторы настраиваются на двух уровнях:

- **каталог операций** решает, *можно ли* автоматически повторять конкретную
  операцию. Это свойство метода API, приложение его не меняет;
- **`RetryPolicy`** в настройках клиента задаёт, *сколько раз и с какими паузами*
  SDK повторяет разрешённые операции.

### Что задаёт каталог операций {#retry-catalog}

Политика повтора записана для каждой операции в
`specifications/operation-catalog.json` (поля `retry_class` и `idempotent`).
Скрипт `scripts/generate_request_metadata.py` переносит её в
`src/apisdkopti24/endpoints.py`, откуда её читает транспорт.

| Политика `retry_class` | Что SDK повторяет автоматически | Операции |
|---|---|---|
| `safe` | сбой сети, ответы `429` и `509` | 37 операций чтения, например `get_cards_v2`, `get_transactions_v2`, `download_report_file` |
| `network_only` | только сбой сети | `auth_user` |
| `never` | ничего | 51 операция изменения данных, включая удаления: `block_card`, `move_to_card`, `delete_user` |

Остальные HTTP-ошибки (`400`, `403`, `404`, `409`, `5xx`) не повторяются ни при
какой политике. `401` обрабатывает отдельный механизм — одна повторная авторизация,
см. [«Учитывайте автоматический re-auth»](#re-auth).

Политику любой операции можно посмотреть через реестр клиента:

```python
spec = client.registry.get("get_cards_v2")
print(spec.retry_class, spec.idempotent)  # safe True

safe_operations = sorted(
    operation.name
    for operation in client.registry.list_all()
    if operation.retry_class == "safe"
)
```

Изменить политику операции можно только в каталоге, с последующей
перегенерацией `endpoints.py`. Это изменение SDK, а не настройка приложения:
политику `never` нельзя менять на `safe` без проверки, что повтор метода не создаст
дубль операции на сервере.

### Что настраиваете вы: `RetryPolicy` {#retry-policy}

`RetryPolicy` (`src/apisdkopti24/policies.py`) передаётся в `ConnectionSettings`
или `APISettings` параметром `retry_policy`. Через `.env` повторы не настраиваются.

| Параметр | По умолчанию | Что задаёт |
|---|---:|---|
| `network_attempts` | `5` | Попыток при сбое сети для `safe` и `network_only` |
| `rate_limit_attempts` | `3` | Попыток при `429`/`509`, только для `safe` |
| `max_total_attempts` | `5` | Общий лимит HTTP-попыток одной операции, включая `authUser` и повтор при восстановлении сессии. Не ставьте меньше `3`: восстановлению после `401` нужны исходный запрос, `authUser` и повтор, иначе операция завершится `RetryBudgetExceededError` |
| `network_backoff_min_seconds` | `2.0` | Начальный предел паузы после сбоя сети; удваивается с каждой попыткой |
| `network_backoff_max_seconds` | `60.0` | Наибольший предел паузы после сбоя сети |
| `rate_limit_backoff_seconds` | `0.5` | Предел паузы после `429`/`509` растёт как это значение × номер попытки |
| `auth_retry_min_interval_seconds` | `5.0` | Минимальный интервал между запросами `authUser` и начальный предел паузы при повторе авторизации |

Фактическое число попыток — меньшее из лимита для вида сбоя и `max_total_attempts`.
Пауза выбирается случайно от нуля до текущего предела (full jitter), поэтому
параллельные клиенты не повторяют запросы одновременно. Все попытки и паузы
укладываются в общий срок операции из `TimeoutPolicy`
(см. [«Конфигурация»](configuration.md)): если пауза не помещается в остаток срока,
SDK сразу поднимает `OperationTimeoutError`.

Пример: меньше повторов и короче паузы для интерактивного приложения.

```python
import asyncio

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    RetryPolicy,
)


async def main() -> None:
    settings = ConnectionSettings(
        base_url="https://api.example.ru/vip/",
        retry_policy=RetryPolicy(
            network_attempts=3,
            rate_limit_attempts=2,
            network_backoff_min_seconds=1.0,
            network_backoff_max_seconds=10.0,
        ),
    )
    credentials = EnvironmentCredentialsProvider.from_env()

    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        cards = await client.cards.get_cards_v2(onpage=20)
        print("Карт:", cards.total_count)


if __name__ == "__main__":
    asyncio.run(main())
```

Чтобы отключить автоматические повторы, оставьте по одной попытке на каждый вид
сбоя, а общий лимит не трогайте — он нужен для восстановления сессии:

```python
retry_policy = RetryPolicy(network_attempts=1, rate_limit_attempts=1)
```

### Что важно учитывать при повторах {#retry-notes}

- операции изменения не повторяются после неопределённого сетевого результата:
  сервер мог выполнить запрос, даже если ответ не дошёл;
- `409 duplicateConflict` не считается основанием для автоматического повтора;
- JSON-ответы и загрузка файлов используют одну и ту же политику повторов;
- каждый повтор — новый запрос к API, и он может тарифицироваться, если метод
  платный.

Повторы применяет `RetryController` в `src/apisdkopti24/resilience.py`; транспорт
(`src/apisdkopti24/transport.py`) только передаёт ему политику операции.

## Примените безопасную обработку ошибок

1. Не добавляйте внешний retry вокруг всех вызовов без учёта idempotency.
2. Сохраняйте `method_name`, HTTP/API-коды и sanitized correlation data.
3. Не журналируйте credentials, session ID и исходный payload ошибки.
4. Для длительных сбоев используйте circuit breaker на уровне приложения.

### Остановите вызовы при длительном сбое API {#circuit-breaker}

SDK не содержит circuit breaker: решение «перестать обращаться к API на время» зависит
от приложения. Считайте сбоями только признаки недоступности сервера —
`APIConnectionError`, `OperationTimeoutError` и `ServerError`. Ошибки запроса
(`ValidationError`, `AccessDeniedError`, `NotFoundError`) говорят о данных или
правах, а не о состоянии API, и размыкать цепь не должны.

```python
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

from apisdkopti24 import APIConnectionError, OperationTimeoutError, ServerError

ResultT = TypeVar("ResultT")
OUTAGE_ERRORS = (APIConnectionError, OperationTimeoutError, ServerError)


class CircuitOpenError(RuntimeError):
    """API временно не вызывается после серии сбоев."""


class CircuitBreaker:
    def __init__(self, *, failure_threshold: int = 5, reset_after_seconds: float = 60.0) -> None:
        self._failure_threshold = failure_threshold
        self._reset_after_seconds = reset_after_seconds
        self._failures = 0
        self._opened_at: float | None = None

    async def call(self, operation: Callable[[], Awaitable[ResultT]]) -> ResultT:
        if self._opened_at is not None:
            if time.monotonic() - self._opened_at < self._reset_after_seconds:
                raise CircuitOpenError("API временно недоступно; повторите позже")
            self._opened_at = None  # после паузы пропускаем пробный вызов
        try:
            result = await operation()
        except OUTAGE_ERRORS:
            self._failures += 1
            if self._failures >= self._failure_threshold:
                self._opened_at = time.monotonic()
            raise
        self._failures = 0
        return result


breaker = CircuitBreaker(failure_threshold=5, reset_after_seconds=60)
cards = await breaker.call(lambda: client.cards.get_cards_v2(onpage=20))
```

Держите один `CircuitBreaker` на клиент и не оборачивайте им повтор изменяющих
операций: предохранитель сокращает число обращений к недоступному API, но не
делает повтор перевода или блокировки безопасным.


## Отказ журналирования и текстовый вывод

Текстовый audit содержит `operation_id`, `sdk_error_code` и безопасную причину;
JSON audit сохраняет эти же поля структурированно. При внутреннем сбое
классификатора записывается минимальное событие `sdk_internal_error`.
Исключение logging handler не заменяет результат или исходную ошибку операции.
SDK пытается записать постоянное сообщение об отказе через logger
`apisdkopti24.audit`; `OperationAudit.logging_failed` отмечает недоставку.
Если отказал и резервный logger, доставка не гарантируется: для контроля
полноты audit нужна внешняя проверка работоспособности обработчиков.

Встроенный текстовый handler использует `SafeExceptionFormatter`
(`src/apisdkopti24/logger.py`): он исключает текст и цепочку исключений, пути и
строки исходников из traceback. Если вы подключаете собственный handler к логгеру
SDK, назначьте ему этот formatter явно:

```python
import logging

from apisdkopti24.logger import SafeExceptionFormatter

handler = logging.FileHandler("sdk.log", encoding="utf-8")
handler.setFormatter(SafeExceptionFormatter("%(asctime)s %(levelname)s %(message)s"))

sdk_logger = logging.getLogger("apisdkopti24")
sdk_logger.setLevel(logging.INFO)
sdk_logger.addHandler(handler)
```

Логгер `apisdkopti24` получает сообщения всех клиентов, у которых не заданы ни
`logger_file`, ни `request_log_file` и не внедрён собственный `logger`
(см. [«Конфигурация»](configuration.md)).

Не вставляйте `str(exc)` в само сообщение и не передавайте raw payload через
`extra`: formatter не может распознать произвольный секрет в пользовательском
тексте. SDK не изменяет formatter внедрённого пользователем handler.
Модели скрывают входные значения в строке Pydantic validation error, но
`errors()`, `model_dump()` и исходная цепочка исключений остаются диагностическими
данными. Причины сохраняются через exception chaining; это не разрешение
публиковать необработанный traceback.

## Язык сообщений

Собственные сообщения SDK, комментарии и строки документации написаны по-русски.
Имена классов, параметров, коды ошибок, значения перечислений и поля JSON-аудита
сохраняют машинные имена: например, `sdk_error_code=network_timeout` и
`event=failed`. Не разбирайте текст исключения для управления приложением:
используйте тип исключения и структурированные поля.

SDK не переводит данные ответа сервера и стандартные исключения Python,
HTTPX или Pydantic. Их исходные объекты сохраняются для диагностики; безопасный
`ErrorDescriptor.error_message` и сообщения штатного аудита формируются по-русски.
