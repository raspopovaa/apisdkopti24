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
| `API_REQUESTS_PER_SECOND` | Нет | Упреждающий rate limit клиента | `2` для DEMO, `5` для остальных стендов |
| `API_ALLOW_INSECURE_HTTP` | Нет | Разрешить удалённый HTTP | `false` |
| `API_MAX_IN_FLIGHT` | Нет | Максимальное число одновременных операций | `20` |
| `API_MAX_JSON_RESPONSE_BYTES` | Нет | Предельный размер JSON-ответа до декодирования, в байтах | `16777216` (16 МиБ) |
| `LOG_LEVEL` | Нет | Уровень журнала | `INFO` |
| `LOGGER_FILE` | Нет | Основной файл журнала | `./api.log` |
| `REQUEST_LOG_FILE` | Нет | JSONL-аудит операций | `./api_requests.jsonl` |

## Отделите настройки от credentials

Рекомендуемый `ConnectionSettings` не содержит credentials:

```python
from apisdkopti24 import ConnectionSettings

settings = ConnectionSettings(
    base_url="https://api.example.ru/vip/",
    request_log_file="./api_requests.jsonl",
    logger_file="./api.log",
    log_level="INFO",
)
```

Credentials передаются отдельно:

```python
from apisdkopti24 import StaticCredentialsProvider

credentials = StaticCredentialsProvider(
    api_key="api-key",
    login="login",
    password="password",
)
```

`APISettings` сохранён для совместимости, но новые интеграции должны предпочитать
`ConnectionSettings` и отдельные providers.

## Разделяйте основной и audit-журнал

`LOGGER_FILE` содержит обычные сообщения SDK, а `REQUEST_LOG_FILE` — JSONL-события
жизненного цикла операций. При ошибке оба журнала получают безопасный символьный
`sdk_error_code` и очищенный текст; JSONL дополнительно содержит HTTP/API-коды,
если сервер успел вернуть ответ.

Не назначайте локальному timeout фиктивный HTTP-код: для него используется
`sdk_error_code=operation_timeout`, а `http_status_code` и `api_status_code`
остаются `null`. SDK не записывает исходные request/response payload, URL с query,
значения Pydantic input, credentials и абсолютные пути файлов.

Request audit охватывает операции, вошедшие в executor. Ошибки чтения `.env`,
создания настроек или DTO до вызова метода должно журналировать приложение без
вывода секретных значений.

## Подключите динамическую ротацию API key

`OperationExecutor` вызывает provider перед каждым запросом. Поэтому можно
подключить secret manager без пересоздания клиента:

```python
class SecretManagerAPIKeyProvider:
    def get_api_key(self) -> str:
        return read_cached_api_key_from_secret_manager()
```

Provider должен возвращать непустую строку. Сетевой запрос к secret manager лучше
не выполнять на каждый API-вызов: используйте безопасный кэш с контролируемым TTL.

## Настройте timeout и общий deadline

```python
from apisdkopti24 import ConnectionSettings, TimeoutPolicy

settings = ConnectionSettings(
    base_url="https://api.example.ru/vip/",
    timeouts=TimeoutPolicy(
        default=30.0,
        auth=30.0,
        read_heavy=120.0,
        total_default=120.0,
        total_auth=60.0,
        total_read_heavy=300.0,
    ),
)
```

Конкретный timeout попытки и общий deadline операции выбираются из
`OperationSpec.timeout_class`. Общий deadline продолжает отсчитываться во время
rate limiting, backoff и восстановления сессии.

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

## Используйте registry только для инспекции

`client.registry` содержит каталог доступных операций и metadata. Registry
создаётся SDK автоматически и не передаётся в конструктор `APIClient`.
Фактические запросы выполняются по `OperationSpec`, объявленным доменными
сервисами. Для изоляции интеграционных тестов передавайте собственную реализацию
`transport`.

## Ограничьте частоту запросов

Для DEMO обычно используется значение `2`, для production — `5`, если это
соответствует условиям конкретного договора:

```env
API_REQUESTS_PER_SECOND=2
```

Клиентский limiter не отменяет серверные ограничения и тарификацию.

## Используйте безопасный transport

- удалённые API адреса должны использовать HTTPS;
- HTTP разрешён для loopback;
- небезопасный удалённый HTTP требует явного `allow_insecure_http=True`;
- параметры пути централизованно кодируются; символы `/`, `\\`, `?`, `#`
  запрещены. Значения `.` и `..` целиком запрещены, но точка внутри
  идентификатора допустима.

## Внедрите тестовые зависимости

Для тестирования можно внедрять `transport`, `session_manager`, `logger`,
`clock`, `credentials_provider` и `api_key_provider` через конструктор
`APIClient`.
