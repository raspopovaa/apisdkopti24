# Архитектура SDK

## Request pipeline

1. Доменный метод явно передаёт executor имя операции и параметры пути.
2. `DefaultRequestExecutor` применяет session/recovery policy операции.
3. `OperationExecutor` получает декларативный `EndpointSpec` из registry,
   выбирает route variant, безопасно кодирует path-параметры и передаёт timeout,
   `retry_class` и `idempotent` в transport.
4. Transport независимо применяет rate limit и сетевой retry.
5. `ResponseDecoder` требует успешные HTTP-код и `payload.status.code`.
6. Executor проверяет, что JSON-ответ является объектом, а доменный сервис
   преобразует его в типизированную модель.

## Декларативные endpoints

Все маршруты находятся в `endpoints.py`. Registry не использует AST,
`inspect`, динамический импорт сервисов или соглашения об именовании методов.
`MethodSpec` сохранён как alias `EndpointSpec` для обратной совместимости.
Сервисы не содержат HTTP-методов и endpoint-строк: operation-centric executor
является единственной точкой разрешения маршрута.
Внешний код и признак тарификации объявляются непосредственно в соответствующем
вызове `endpoint()` или `route()`, поэтому отдельного внутреннего metadata-overlay
нет.

## Dependency injection

`APIClient` принимает `transport`, `session_manager`, `registry`, `logger` и
`clock`. Функция `compose_client_runtime()` статически собирает authenticator,
coordinator, оба executor и сервисы; двухфазной настройки через `bind()` нет.
`AsyncTransport` отдельно принимает HTTP client, response decoder,
политики, logger и clock. Transport не знает об `APIClient`, session manager или
re-auth.

Публичный `client.settings` имеет тип `ConnectionSettings` и не содержит API key,
логин или пароль. Секреты находятся в отдельных `APIKeyProvider` и
`CredentialsProvider`; единый `StaticCredentialsProvider` реализует оба узких
контракта. `OperationExecutor` хранит только `APIKeyProvider` и запрашивает ключ
непосредственно перед каждым запросом, поэтому ротация в secret manager не требует
пересоздания клиента. `DefaultAuthenticator` — единственный компонент, который
получает логин и пароль. Legacy `APISettings` преобразуется в безопасные настройки
в composition root и не сохраняется клиентом.

Сервисы зависят только от узких протоколов `RequestExecutor`, read-only
`SessionContext`, `SessionGate` и logger. Они не могут изменять состояние сессии.
`SessionGate` также используется асинхронным resolver договора, если вызывающий
код не передал `contract_id` явно.
Только `DefaultAuthenticator` получает `SessionMutator` и `CredentialsProvider`,
а `AuthService` делегирует ему `auth_user`. Ни один доменный сервис не хранит
ссылку на `APIClient`, его настройки или transport.

`AuthenticationCoordinator` получает готовый authenticator в конструкторе и
реализует `SessionGate` и `SessionRecovery`. Auth-операция выполняется через
низкоуровневый `OperationExecutor` и помечена в registry как не
требующая сессии, поэтому её `401` возвращается вызывающему коду без рекурсивного
re-auth. Пароль не передаётся остальным сервисам.

Потоковые и JSON-запросы используют только маршруты registry и настроенный
`base_url`. Значения path-параметров кодируются, а разделители пути и dot-segments
запрещены. API key и session ID не могут быть отправлены на другой origin.

## Наблюдаемость

Каждый экземпляр клиента создаёт собственный logger и владеет только своими
handlers. Закрытие одного клиента не влияет на остальные. Основной файл лога и
`request_log_file` открываются в append-режиме. Request-аудит записывается в
JSONL и содержит только имя операции, версию, route name, HTTP-метод и результат;
URL, path-параметры и payload в него не попадают. Внедрённый пользователем logger
не закрывается SDK.

## Композиционные сервисы

Все доменные вызовы выполняются через композиционные сервисы:

```python
auth = await client.auth.auth_user()
cards = await client.cards.get_cards_v2()
jobs = await client.reports.get_report_jobs()
users = await client.users.get_users()
```

Здесь предполагается единственный договор. Если авторизация возвращает несколько
договоров, вызывающий код явно выбирает один из `ContractSelectionError.available_contracts`
и повторяет `auth_user(contract_id=...)`.

Каждый доменный метод объявлен непосредственно в конкретном сервисе. В SDK нет
доменных mixin-классов и прямых методов вида `client.get_cards_v2()`.
`AuthService` создаётся отдельно в composition root и делегирует работу с
credentials изолированному authenticator. `ServiceContainer` не зависит от учётных данных и
собирает остальные сервисы в одном типизированном composition root,
а внутренний `_ServiceFacade` предоставляет явные свойства без динамического
`__getattr__`.

Доступные пространства имён: `auth`, `card_groups`, `cards`, `contracts`,
`dictionaries`, `ewallet`, `final_prices`, `invites`, `limits`, `region_limits`,
`reports`, `restrictions`, `templates`, `transactions`, `users` и
`virtual_cards`.

## Модели данных

Локальный modeling framework заменён Pydantic v2. Совместимый `BaseModel`
сохраняет `model_validate()`, `model_dump()`, `Field`, validators, `describe()` и
адаптер `decode_model()`. Pydantic проверяет
типы элементов `dict`, длину fixed tuple и вложенные структуры. Response-модели
сохраняют дополнительные серверные поля для forward compatibility, а
`StrictRequestModel` запрещает неизвестные поля во всех request DTO.

Все JSON-методы возвращают полный envelope `status/data/timestamp` и используют
единый `decode_model()`. Публичные параметры сервисов являются keyword-only.
Бинарные методы отчётов сохраняют обратную совместимость с возвратом `bytes`, а
методы `download_report_file_to()` и `download_report_file_v1_to()` потоково
пишут данные во временный файл и атомарно заменяют целевой файл после успеха.
Запись выполняется буферами, поэтому файловый I/O не создаёт отдельный вызов
worker thread на каждый сетевой chunk.

Каждый endpoint связан с сервисом явной константой `Operation[TResponse]`.
`DefaultRequestExecutor` один раз разрешает `EndpointSpec`, создаёт неизменяемый
`PreparedOperation` с `RequestContext` и централизованно декодирует ответ.
Identity-декораторы и неявный `ContextVar` в этом пути не используются.

`ConcurrencyPolicy.max_in_flight` ограничивает число активных HTTP-запросов на
экземпляр `APIClient`. Ограничение охватывает чтение потокового ответа целиком,
но не является глобальным rate limiter между несколькими клиентами или процессами.
Для больших списков доступны последовательные bounded-итераторы
`iter_cards_v2()`, `iter_users()`, `iter_invites()` и `iter_transactions_v2()`.

## Контракт endpoints

`tests/contracts/endpoints.json` является версионируемым snapshot-контрактом для
всех 89 операций. Contract-тест сравнивает с ним имя и домен операции, версии,
маршруты, demo-доступность, idempotency, session policy, timeout и retry class.
Изменение registry поэтому требует явного изменения контракта, а не проходит
незаметно вместе с реализацией.

Snapshot дополняется независимым текстовым контрактом
`specifications/api-methods.yaml`, однократно преобразованным из внешней таблицы.
Скрипт `scripts/verify_external_contract.py` выполняет строгое сопоставление
`external_code → EndpointSpec/RouteVariant` и проверяет operation, route name,
HTTP-метод, версию, путь, DEMO-доступность и тарификацию. Исходный Excel не
хранится в репозитории. Известные противоречия сводной и детальной спецификаций
перечислены непосредственно в YAML и не исправляются неявно.

Дополнительный независимый контракт `specifications/api-contract-v1.1.60.yaml`
связывает внешний маршрут с параметрами официальной спецификации, сигнатурой
SDK, response-моделью и aliases строгих request DTO. Его CI-аудит предотвращает
незаметное расхождение маршрута, Python API и Pydantic schema.

## Источники спецификаций и QR

Очищенные исходные документы находятся в `docs/specifications/`, а
нормализованные машинно-проверяемые контракты — в `specifications/`. Основная
спецификация API 1.1.60 и QR-спецификация 1.0.4 являются разрешёнными источниками.

Текущий runtime registry содержит 89 операций, тогда как опубликованный каталог
пока показывает 82 и исторически исключает 7 МПК/QR-операций. Перед реализацией
QR необходимо составить проверяемое соответствие «операция спецификации → route →
параметры → response model → сервис → тесты». Похожие методы виртуальных карт не
считаются реализацией QR без подтверждения контрактом.

При конфликте документов, нормализованного YAML, registry, сигнатур или тестов
расхождение фиксируется явно. Нельзя молча выбирать удобный вариант или добавлять
поля по догадке. Сырые документы с credentials в Git не добавляются; используются
только `.sanitized`-копии.
