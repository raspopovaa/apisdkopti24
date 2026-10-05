---
description: Настройка URL, credentials, timeout, retry, rate limit и dependency injection в apisdkopti24.
---

# Конфигурация

## Задайте переменные окружения

| Переменная | Обязательна | Назначение | Значение по умолчанию |
|---|:---:|---|---|
| `API_BASE_URL` | Да | Полный URL API; для удалённых узлов требуется `https://` | — |
| `API_KEY` | Да | Ключ API | — |
| `API_LOGIN` | Да | Логин пользователя | — |
| `API_PASSWORD` | Да | Пароль пользователя | — |
| `API_REQUESTS_PER_SECOND` | Нет | Упреждающий rate limit клиента | `1` для DEMO и рабочей среды |
| `API_ALLOW_INSECURE_HTTP` | Нет | Разрешить удалённый HTTP: `true`/`1`/`yes`/`on` или `false`/`0`/`no`/`off`, регистр не важен; другое значение — `SDKConfigurationError` | `false` |
| `API_MAX_IN_FLIGHT` | Нет | Максимальное число одновременных операций | `20` |
| `API_MAX_JSON_RESPONSE_BYTES` | Нет | Предельный размер любого JSON-ответа до декодирования, в байтах | `16777216` (16 МиБ) |
| `API_MAX_IN_MEMORY_RESPONSE_BYTES` | Нет | Предельный размер файла, возвращаемого в память | `67108864` (64 МиБ) |
| `API_MAX_ERROR_RESPONSE_BYTES` | Нет | Предельный размер тела ошибки потоковой загрузки | `1048576` (1 МиБ) |
| `LOG_LEVEL` | Нет | Уровень основного файла журнала (`LOGGER_FILE`): `DEBUG`, `INFO`, `WARNING`, `ERROR` или `CRITICAL`; другое значение — `SDKConfigurationError`. Без файловых журналов уровень задаёт приложение на логгере `apisdkopti24`; на `REQUEST_LOG_FILE` уровень не влияет | `INFO` |
| `LOGGER_FILE` | Нет | Основной файл журнала; пустое значение — не писать файл | не задан |
| `REQUEST_LOG_FILE` | Нет | JSONL-аудит операций; пустое значение — не писать файл | не задан |

Файл `.env` SDK читает сам, без внешних библиотек, по правилам, привычным по
`python-dotenv`:

- строка `export KEY=value` равнозначна `KEY=value` — тот же файл можно
  подключать в shell через `source .env`;
- у значения без кавычек всё, начиная с `#`, перед которым стоит пробел или табуляция, —
  комментарий:
  `API_KEY=abc  # ключ из портала` даёт `abc`; `#` без пробела перед ним — часть
  значения;
- значение в одинарных или двойных кавычках берётся целиком: `API_PASSWORD='a #b'`
  даёт `a #b`;
- переменные, уже заданные в окружении процесса, не перезаписываются;
- прочитанные значения записываются в окружение процесса (`os.environ`), поэтому
  их видят и дочерние процессы.

## Отделите настройки от credentials

Рекомендуемый `ConnectionSettings` не содержит credentials:

```python
from apisdkopti24 import ConnectionSettings

settings = ConnectionSettings(
    base_url="https://api.example.ru/vip/",
    max_json_response_bytes=16 * 1024 * 1024,
    max_in_memory_response_bytes=64 * 1024 * 1024,
    max_error_response_bytes=1024 * 1024,
    request_log_file="./api_requests.jsonl",
    logger_file="./api.log",
    log_level="INFO",
)
```

Все три лимита должны быть положительными. JSON, включая справочники, читается
потоково и прекращает загружаться после достижения соответствующего предела.
Для больших бинарных ответов используйте методы сохранения в файл, а не возврат
всего содержимого в память.

Credentials передаются отдельно:

```python
from apisdkopti24 import StaticCredentialsProvider

credentials = StaticCredentialsProvider(
    api_key="api-key",
    login="login",
    password="password",
)
```

Объект настроек не хранит ключ API, логин и пароль. Передавайте в `APIClient`
`ConnectionSettings` и отдельно `credentials_provider` (или `api_key_provider`):

```python
client = APIClient(
    settings=ConnectionSettings(base_url="https://api.example.ru/vip/"),
    credentials_provider=StaticCredentialsProvider(
        api_key="api-key", login="login", password="password"
    ),
)
```

## Разделяйте основной и audit-журнал

По умолчанию SDK не создаёт файлов журнала. Сообщения идут в логгер
`apisdkopti24.client`, у которого нет своих обработчиков. Чтобы видеть их,
добавьте обработчик к логгеру `apisdkopti24`:

```python
import logging

sdk_logger = logging.getLogger("apisdkopti24")
sdk_logger.setLevel(logging.INFO)
sdk_logger.addHandler(logging.StreamHandler())
```

Файлы включаются явно: `LOGGER_FILE` и `REQUEST_LOG_FILE` в окружении или
`logger_file` и `request_log_file` в настройках. Можно задать только один из них.
Пустое значение переменной окружения означает «не задано» — так же и для числовых
лимитов: пустой `API_MAX_IN_FLIGHT=` включает значение по умолчанию.

`LOGGER_FILE` содержит обычные сообщения SDK, а `REQUEST_LOG_FILE` — JSONL-события
жизненного цикла операций. `LOG_LEVEL` ограничивает только `LOGGER_FILE`: журнал
аудита получает все события (`started`, `completed`, `failed`, `cancelled`) при
любом уровне, чтобы у каждой операции оставалось итоговое событие. Без файловых
журналов `LOG_LEVEL` не действует — уровень задаёт приложение на логгере
`apisdkopti24`. При ошибке оба журнала получают безопасный символьный
`sdk_error_code` и очищенный текст; JSONL дополнительно содержит HTTP/API-коды,
если сервер успел вернуть ответ.

Не назначайте локальному timeout фиктивный HTTP-код: для него используется
`sdk_error_code=operation_timeout`, а `http_status_code` и `api_status_code`
остаются `null`. SDK не записывает исходные request/response payload, URL с query,
значения Pydantic input, credentials и абсолютные пути файлов.

Request audit охватывает операции, вошедшие в executor. Ошибки чтения `.env`,
создания настроек или DTO до вызова метода должно журналировать приложение без
вывода секретных значений.

### Права и ротация файлов журналов

SDK открывает `LOGGER_FILE` и `REQUEST_LOG_FILE` обычным `logging.FileHandler`:
файл создаётся с правами по umask процесса (обычно `0644`) и не ротируется — он
растёт, пока процесс работает. Секретов, тел запросов и URL в журналах нет, но
есть имена операций, коды ошибок и время работы, поэтому:

- создайте файлы заранее с правами `0600` (например, `install -m 600 /dev/null
  /var/log/app/api.jsonl`) или запускайте процесс с `umask 077`;
- для ротации используйте системный `logrotate` с `copytruncate` или передайте
  клиенту свой логгер с `RotatingFileHandler`:

```python
import logging
from logging.handlers import RotatingFileHandler

from apisdkopti24 import APIClient, ConnectionSettings, StaticCredentialsProvider
from apisdkopti24.logger import RequestAuditFilter, RequestAuditFormatter

audit_handler = RotatingFileHandler("api.jsonl", maxBytes=10_000_000, backupCount=5)
audit_handler.addFilter(RequestAuditFilter())  # только события аудита
audit_handler.setFormatter(RequestAuditFormatter())  # JSONL с безопасным набором полей

sdk_logger = logging.getLogger("my_app.apisdkopti24")
sdk_logger.setLevel(logging.INFO)
sdk_logger.addHandler(audit_handler)

client = APIClient(
    settings=ConnectionSettings(base_url="https://api.example.ru/vip/"),
    credentials_provider=StaticCredentialsProvider(
        api_key="api-key", login="login", password="password"
    ),
    logger=sdk_logger,
)
```

Переданный логгер SDK дополняет фильтром очистки секретов; закрывать его
обработчики при `aclose()` клиент не будет — это делает приложение.

## Подключите динамическую ротацию API key {#api-key-rotation}

После ротации токена в личном кабинете старый ключ перестаёт работать. Чтобы
не перезапускать приложение, передайте в `APIClient` собственного поставщика
ключа (`api_key_provider`). SDK вызывает его `get_api_key()` перед **каждым**
запросом (`OperationExecutor` в `src/apisdkopti24/executor.py`), поэтому новый
ключ начинает действовать со следующего запроса.

`StaticCredentialsProvider` и `EnvironmentCredentialsProvider`
(`src/apisdkopti24/credentials.py`) читают ключ один раз при создании и для
ротации не подходят.

Для этого в SDK есть `RefreshingAPIKeyProvider`
(`src/apisdkopti24/credentials.py`). Он хранит ключ в памяти и обновляет его
фоновой задачей из вашей асинхронной функции раз в `ttl_seconds`. Сам
`get_api_key()` не обращается ни к сети, ни к диску, поэтому не блокирует цикл
событий.

```python
import asyncio

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    RefreshingAPIKeyProvider,
    StaticLoginPasswordProvider,
)


async def fetch_api_key_from_vault() -> str:
    """Прочитать ключ из вашего secret manager асинхронным клиентом."""
    raise NotImplementedError


async def main() -> None:
    api_keys = RefreshingAPIKeyProvider(fetch_api_key_from_vault, ttl_seconds=300)
    # start(): получить первый ключ и запустить обновление; выход — остановить его.
    async with api_keys:
        async with APIClient(
            settings=ConnectionSettings(base_url="https://api.example.ru/vip/"),
            api_key_provider=api_keys,
            credentials_provider=StaticLoginPasswordProvider(
                login="login",
                password="password",
            ),
        ) as client:
            cards = await client.cards.get_cards_v2(onpage=20)
            print("Карт:", cards.total_count)


if __name__ == "__main__":
    asyncio.run(main())
```

Как ведёт себя поставщик:

| Ситуация | Что происходит |
|---|---|
| Вызов до `start()` или `refresh()` | запрос не отправляется, `SDKConfigurationError` |
| Источник вернул пустую строку или упал при фоновом обновлении | прежний ключ остаётся в работе, `last_refresh_failed` становится `True`, в журнал пишется предупреждение только с типом исключения |
| Следующее обновление прошло успешно | новый ключ действует со следующего запроса, `last_refresh_failed` снова `False` |
| Вы сами выполнили ротацию в личном кабинете | вызовите `api_keys.set_api_key(new_key)` или `await api_keys.refresh()`, чтобы не ждать конца интервала |

Что учитывать:

- `ttl_seconds` задаёт, сколько времени после ротации SDK может отправлять старый
  ключ. В этот промежуток сервер отвечает `403`, и SDK поднимает
  `AccessDeniedError`: сам SDK ключ не перечитывает и повторно не авторизуется;
- один поставщик можно передать нескольким клиентам: все они начнут отправлять
  новый ключ одновременно;
- логин и пароль меняются так же: `credentials_provider` с методом
  `get_credentials() -> tuple[str, str]` вызывается при каждой авторизации
  (`authUser`). Если вы меняете пароль, верните новый из своего поставщика.

## Настройте timeout и общий deadline {#timeouts}

`TimeoutPolicy` (`src/apisdkopti24/config.py`) задаёт два вида лимитов: timeout
одной HTTP-попытки и общий срок операции, в который укладываются все попытки,
паузы и восстановление сессии. Какой из четырёх классов применяется к методу,
записано в каталоге операций (`timeout_class` в
`specifications/operation-catalog.json`); приложение класс не меняет.

| Класс | Операции | Timeout попытки | Общий срок |
|---|---|---|---|
| `default` | 52 операции, в основном изменения данных: `block_card`, `move_to_card`, `create_template` | `default` = 30 с | `total_default` = 120 с |
| `auth` | `auth_user` | `auth` = 30 с | `total_auth` = 60 с |
| `read_heavy` | 34 долгие операции: чтение и загрузки (`get_cards_v2`, `get_transactions_v2`, `download_report_file`) | `read_heavy` = 120 с | `total_read_heavy` = 300 с |
| `slow_mutation` | `remove_card_group` и `delete_user`: удаление бывает дольше 120 и 30 секунд соответственно | `slow_mutation` = 300 с | `total_slow_mutation` = 360 с |

`connect` (10 с) ограничивает установку соединения в каждой попытке. Через `.env`
таймауты не настраиваются — только в коде. Класс конкретного метода можно
посмотреть через реестр: `client.registry.get("get_cards_v2").timeout_class`.

Сервер может обрабатывать тяжёлые запросы дольше номинальных 120 секунд. Если
отчёты или большие выборки обрываются `OperationTimeoutError`, увеличьте
`read_heavy` и `total_read_heavy`, а остальные классы оставьте короткими:

```python
from apisdkopti24 import ConnectionSettings, TimeoutPolicy

settings = ConnectionSettings(
    base_url="https://api.example.ru/vip/",
    timeouts=TimeoutPolicy(
        read_heavy=180.0,  # одна попытка долгой операции
        total_read_heavy=600.0,  # весь вызов, включая повторы
    ),
)
```

Передайте настройки в клиент: `APIClient(settings=settings, credentials_provider=...)`.
Конкретный timeout попытки и общий deadline операции выбираются из
`OperationSpec.timeout_class`. `connect` ограничивает установку соединения в
каждой попытке и не превышает timeout попытки. Если подключиться не удалось,
операция завершается `APIConnectionError`; если сервер не ответил за timeout
попытки — `APIResponseTimeoutError` (см. [сетевые ошибки](errors.md#network-errors)). Общий deadline продолжает отсчитываться во время
ожидания свободного слота `API_MAX_IN_FLIGHT`, rate limiting, backoff и восстановления сессии.

Каждая попытка сначала занимает слот одновременных запросов, затем ждёт интервал
лимита частоты и только после этого списывает попытку из бюджета. Поэтому запросы,
которые ждали слот, не уходят пачкой сверх лимита частоты, а timeout попытки
считается от времени, оставшегося после ожидания. Если срок операции истёк, пока
запрос ждал слот, SDK запрос не отправляет и поднимает `OperationTimeoutError`. На
время паузы перед повтором слот освобождается.

Общее число HTTP-попыток дополнительно ограничивает
`RetryPolicy.max_total_attempts` (по умолчанию `5`). Retry использует full jitter,
поэтому параллельные клиенты не обязаны повторять запросы одновременно.

## Управляйте сессией явно

`session_id` и `contract_id` доступны только для чтения. Используйте явные
операции lifecycle:

```python
client.select_contract(contract_id="contract-id")
client.restore_session(session_id="session-id", contract_id="contract-id")
client.clear_session()
```

`restore_session()` восстанавливает только локальное состояние. Сервер проверит
валидность сессии при следующем запросе.

Договор, выбранный через `select_contract()`, сохраняется, если авторизация не
удалась из-за сбоя сети, ответа `5xx` или истечения срока: следующая попытка
авторизуется в том же договоре. Выбор сбрасывается, только если сервер не вернул
этот договор среди доступных (`ContractSelectionError`), и при `clear_session()`
или `logoff()`.

Если `select_contract()` вызван, пока идёт вход, выбор приложения сохраняется:
SDK не заменяет его договором, который определился при входе.

Итераторы `iter_cards_v2`, `iter_transactions_v2` и `iter_card_transactions_v2`
без `contract_id` берут договор сессии один раз, перед первой страницей. Смена
договора во время перебора действует со следующего вызова итератора и не
смешивает страницы двух договоров.

## Используйте registry только для инспекции

`client.registry` содержит каталог доступных операций и metadata. Registry
создаётся SDK автоматически и не передаётся в конструктор `APIClient`.
Фактические запросы выполняются по `OperationSpec`, объявленным доменными
сервисами. Для изоляции интеграционных тестов передавайте собственную реализацию
`transport`.

## Ограничьте частоту и параллельность запросов {#rate-limit}

SDK сам сдерживает поток запросов двумя ограничениями:

| Ограничение | По умолчанию | В `.env` | В коде |
|---|---|---|---|
| Частота запросов | `1` запрос/с для DEMO и рабочей среды | `API_REQUESTS_PER_SECOND` | `RateLimitPolicy(requests_per_second=...)` |
| Одновременные запросы | `20` | `API_MAX_IN_FLIGHT` | `ConcurrencyPolicy(max_in_flight=...)` |
| Интервал между `authUser` | `5` с | — | `RetryPolicy(auth_retry_min_interval_seconds=...)` |

Значение по умолчанию выбирается по хосту `API_BASE_URL`
(`src/apisdkopti24/environments.py`); явное значение его заменяет.

!!! warning "Фактический лимит ниже заявленного"
    Спецификация заявляет 2 запроса в секунду для DEMO и 5 для рабочей среды, но
    сервер отвечает `509` уже при 2 запросах в секунду — примерно на четверть
    запросов. При 1 запросе в секунду `509` не возникает, поэтому это значение и
    выбрано по умолчанию. Бесплатное чтение SDK после `509` повторит, а платное
    чтение и изменяющие операции — нет: они завершатся `RateLimitError`. Поднимайте частоту, только если договор
    это допускает. Подробности —
    в [«Фактической частоте без `509`»](spec-compatibility.md#rate-limit-observed).

Через `.env`:

```env
API_REQUESTS_PER_SECOND=2
API_MAX_IN_FLIGHT=10
```

Через код:

```python
from apisdkopti24 import ConcurrencyPolicy, ConnectionSettings, RateLimitPolicy

settings = ConnectionSettings(
    base_url="https://api.example.ru/vip/",
    rate_limit_policy=RateLimitPolicy(requests_per_second=2),
    concurrency_policy=ConcurrencyPolicy(max_in_flight=10),
)
```

Лимиты действуют внутри одного `APIClient` (точнее, одного transport). Если
приложение запускает несколько процессов или клиентов с одним ключом API,
сервер видит их суммарный поток. Разделите лимит между ними: например, при
4 процессах-воркерах и лимите договора 5 запросов/с задайте каждому
`API_REQUESTS_PER_SECOND=1.25`. Внутри одного процесса используйте один клиент на
всё приложение.

Отключить ограничитель нельзя: `requests_per_second` должен быть конечным числом
больше нуля, а `0`, отрицательные значения, `nan` и `inf` дают
`SDKConfigurationError`. То же правило действует для `TimeoutPolicy` (конечные
значения больше нуля) и задержек `RetryPolicy` (конечные неотрицательные значения).

Клиентский limiter не отменяет серверные ограничения и тарификацию. Сервер может
изредка отвечать `509` и при соблюдении лимита; бесплатное чтение SDK повторит
автоматически, платное — нет (см. [«Настройте повторы запросов»](errors.md#retry)).

## Используйте безопасный transport

- удалённые API адреса должны использовать HTTPS;
- HTTP разрешён для loopback;
- небезопасный удалённый HTTP требует явного `allow_insecure_http=True`;
- параметры пути централизованно кодируются; символы `/`, `\\`, `?`, `#`
  запрещены. Значения `.` и `..` целиком запрещены, но точка внутри
  идентификатора допустима.

## Внедрите тестовые зависимости {#testing}

Для тестов без обращения к API передайте в `APIClient` транспорт с подменённым
HTTP-клиентом. `httpx.MockTransport` отвечает из вашей функции, а SDK проходит
весь обычный путь: проверку параметров, авторизацию, повторы и разбор моделей.

```python
import asyncio

import httpx

from apisdkopti24 import (
    APIClient,
    AsyncTransport,
    ConnectionSettings,
    StaticCredentialsProvider,
)

AUTH_RESPONSE = {
    "status": {"code": 200},
    "data": {
        "session_id": "session-id",
        "client_id": "client-id",
        "client_status": "Active",
        "org_name": "Test organization",
        "user_id": "user-id",
        "contracts": [
            {
                "id": "contract-id",
                "number": "C-1",
                "mpc": False,
                "cards_count": 0,
                "one_price": False,
            }
        ],
        "role_id": "Supervisor",
        "role_name": "Administrator",
        "access": {"web": True, "api": True, "mobile": True},
        "email": "user@example.test",
        "read_only": False,
    },
}


def fake_api(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/v1/authUser"):
        return httpx.Response(200, json=AUTH_RESPONSE)
    if request.url.path.endswith("/v2/cards"):
        cards = {"total_count": 0, "result": []}
        return httpx.Response(200, json={"status": {"code": 200}, "data": cards})
    return httpx.Response(404, json={"status": {"code": 404}})


async def main() -> None:
    settings = ConnectionSettings(base_url="https://api.example.ru/vip/")
    async with httpx.AsyncClient(transport=httpx.MockTransport(fake_api)) as http_client:
        async with APIClient(
            settings=settings,
            transport=AsyncTransport(settings.base_url, http_client=http_client),
            credentials_provider=StaticCredentialsProvider(
                api_key="api-key",
                login="login",
                password="password",
            ),
        ) as client:
            cards = await client.cards.get_cards_v2()
            assert cards.total_count == 0


asyncio.run(main())
```

Готовые примеры такой проверки — в `tests/test_full_chain.py`, а ответы сервера
для разных методов — в `tests/fixtures/spec/1.1.60/`.

Кроме `transport`, через конструктор `APIClient` можно внедрить:

| Параметр | Что подменяет | Пример использования |
|---|---|---|
| `credentials_provider` | логин и пароль (и ключ API, если у объекта есть `get_api_key()`) | `StaticCredentialsProvider(...)` в тестах |
| `api_key_provider` | только ключ API | обновляемый ключ, см. [ротацию ключа](#api-key-rotation) |
| `logger` | логгер SDK; фильтр очистки секретов SDK добавит сам | перехват сообщений через `caplog` |
| `clock` | `now()` для заголовка `date_time` и монотонное время для сроков | детерминированные сроки в тестах |
| `session_manager` | состояние сессии и договора | заранее «авторизованный» клиент |

Внедрённый транспорт клиент не закрывает: закройте `http_client` сами, как в примере.
