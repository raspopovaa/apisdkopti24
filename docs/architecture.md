# Архитектура SDK

## Поток выполнения запроса

1. Доменный сервис передаёт неизменяемый `OperationSpec` и `RequestOptions`.
2. `DefaultRequestExecutor` применяет session gate, однократное восстановление
   сессии и безопасный аудит.
3. `OperationExecutor` выбирает маршрут и создаёт полный `PreparedRequest` с
   единым deadline/attempt budget.
4. `AsyncTransport` выполняет HTTP-вызов, делегируя ограничение частоты
   `RateLimiter`, повторы `RetryController`, а атомарную запись `AtomicFileWriter`.
5. Ответ проверяется по HTTP-коду и `status.code`, затем декодируется в response
   type из `OperationSpec`.

## Контракт операции

`OperationSpec[TResponse]` объединяет имя, response type, маршрут, версии API,
варианты маршрута, session policy, timeout/retry, idempotency, внешнюю metadata и
форму wire-запроса (`RequestContract`: path/query/body и расположение `contract_id`).
Отдельный `EndpointSpec` удалён: executor, registry и генераторы контрактов
работают с полным `OperationSpec`.

Сервисы не передают произвольный `**kwargs`: `RequestOptions` типизирует версию,
route name, path/query/form/JSON, contract ID и дополнительные заголовки.
Transport получает только `PreparedRequest` и не разрешает операции или сессии.
Имена transport-полей однозначны: `query`, `form`, `json_body`. `Content-Type`
добавляется автоматически только при наличии form- или JSON-тела; у GET без тела
этот заголовок отсутствует.

## Разделение зависимостей

Обычные сервисы зависят от `JsonRequestExecutor`. Потоковый `ReportsService`
использует составной executor из отдельных JSON-, bytes- и file-протоколов.

`APIClient` собирается в `compose_client_runtime()`. Сервисы находятся в одном
типизированном `ServiceContainer`; дублирующий `_ServiceFacade` удалён.
`client.services.cards` — основной типизированный путь, а `client.cards`
сохранён через совместимый runtime-адаптер.

`TemplatesService` является публичным фасадом четырёх внутренних компонентов:
CRUD шаблона, лимитов, товарных ограничений и географических ограничений.

## Безопасность и устойчивость

API key и credentials передаются через узкие provider-протоколы и не хранятся в
публичных настройках. Защищённые заголовки нельзя переопределить. Path-параметры
кодируются и отклоняют разделители и dot-segments.

Повторная авторизация использует тот же `OperationBudget`, что и исходная
попытка. Повторы изменения данных запрещены после неопределённой сетевой ошибки.
Файл сначала пишется во временный путь и после успеха атомарно заменяет целевой.

## Проверяемые контракты

Registry сопоставляется с `tests/contracts/endpoints.json`,
`specifications/api-methods.yaml` и монолитным
`specifications/api-contract-v1.1.60.yaml`. Модульный каталог в
`specifications/contracts/1.1.60/` имеет уровни `provisional` и `verified`.

Файл `specifications/request-matrix-v1.1.60.json` фиксирует method, version,
rendered path, query, form/JSON, заголовки и источник контракта для каждой из 89
операций. Параметризованный тест строит реальный `PreparedRequest` по каждой
строке и сравнивает все wire-поля до обращения к HTTP-серверу.

Статус повышается до `verified` только при подтверждённом первичном источнике и
прохождении fixture/model audit. Автоматический рефакторинг его не повышает:
полный audit служит очередью дальнейшей типизации, начиная с авторизации и
транзакций.

Request DTO и общие constrained-типы проверяют данные до сериализации. Их
машинный каталог генерируется в `specifications/request-models-v1.1.60.json`, а
правила выбора DTO описаны в [руководстве по исходящим запросам](request-validation.md).
