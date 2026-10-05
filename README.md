<div align="center">

# apisdkopti24

**Асинхронный Python SDK для Opti24 API — корпоративного API топливных карт АЗС (ОПТИ 24)**

Карты, договоры, транзакции, отчёты, лимиты и оплата по QR-коду: типизированно,
безопасно для повторов и без ручной работы с сессией.

[![CI](https://github.com/raspopovaa/apisdkopti24/actions/workflows/ci.yml/badge.svg)](https://github.com/raspopovaa/apisdkopti24/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/apisdkopti24?color=0f766e)](https://pypi.org/project/apisdkopti24/)
[![Python](https://img.shields.io/badge/Python-3.11%20%E2%80%93%203.14-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Документация](https://img.shields.io/badge/docs-GitHub%20Pages-0f766e)](https://raspopovaa.github.io/apisdkopti24/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/raspopovaa/apisdkopti24/blob/main/LICENSE)

[Документация](https://raspopovaa.github.io/apisdkopti24/) ·
[Каталог методов](https://raspopovaa.github.io/apisdkopti24/latest/methods/) ·
[Учебные примеры](https://raspopovaa.github.io/apisdkopti24/latest/examples/) ·
[Сообщить об ошибке](https://github.com/raspopovaa/apisdkopti24/issues)

<img src="https://raw.githubusercontent.com/raspopovaa/apisdkopti24/main/.github/assets/readme-demo.svg" alt="Демо: три строки кода получают список карт, а SDK проверяет параметры, открывает сессию, соблюдает лимит частоты, разбирает ответ в модель и пишет событие аудита" width="820">

</div>

> [!IMPORTANT]
> Проект в разработке и ещё не использовался в production. Проверьте интеграцию
> на DEMO-стенде, прежде чем подключать рабочий договор.

## О SDK

`apisdkopti24` — клиентская библиотека для приложений и сервисов, которые работают
с корпоративным договором топливных карт ОПТИ 24 через API. Она берёт на себя
транспорт, сессию, выбор договора, повторы и разбор ответов, чтобы код
приложения оставался на уровне предметных действий: «получить карты»,
«заблокировать карту», «заказать отчёт».

**Что покрывает.** 89 операций корпоративного API (спецификация 1.1.60) и
QR API (1.0.4): авторизация и выбор договора, топливные и виртуальные карты,
группы карт, продуктовые лимиты, региональные ограничения и ограничители
обслуживания, договоры и документы, транзакции, отчёты, пользователи и
приглашения, электронный кошелёк, справочники и АЗС, расчёт итоговой стоимости,
выпуск мобильного профиля карты (МПК) и оплата по QR-коду.

**Как устроен.** Один асинхронный `APIClient` объединяет 16 доменных сервисов:
`client.cards`, `client.transactions`, `client.reports` и другие. Параметры
проверяются до отправки запроса, ответы превращаются в типизированные
Pydantic-модели. Маршрут, HTTP-метод, тарификация, доступность на DEMO, класс
timeout и допустимость повтора каждой операции хранятся в едином реестре,
сверенном со спецификацией, а не разбросаны по коду.

**Где работает.** Корпоративный API доступен на DEMO и в рабочей среде, QR API —
на своём тестовом стенде и в рабочей среде. DEMO общий для всех клиентов, не
тарифицируется и поддерживает только часть методов — какие именно, указано в
[каталоге методов](https://raspopovaa.github.io/apisdkopti24/latest/methods/).

**Чего SDK не делает.** Роли, IP-ограничения, квоты, тарифы и видимость объектов
проверяет сервер. SDK не пытается их обойти, а превращает отказ в понятное
исключение с очищенным текстом ответа.

## Возможности

### Предметные методы вместо HTTP

Один `APIClient` открывает 16 сервисов и 89 операций: `client.cards`,
`client.transactions`, `client.reports` и другие. При первом вызове SDK сам
открывает сессию и подставляет договор, а параметры проверяет до отправки
запроса. Ответ приходит Pydantic-моделью: поля подсказывает IDE, ошибки типов
находит mypy.

```python
cards = await client.cards.get_cards_v2(onpage=20)
for card in cards.result:
    print(card.number, card.status)
```

### Сбой сети не превращается в дубль операции

- Автоматически повторяются только операции, которые каталог помечает
  безопасными. Перевод средств или блокировка карты после неясного сбоя не
  повторяются. Число попыток и паузы задаёт `RetryPolicy`
  ([как настроить](https://raspopovaa.github.io/apisdkopti24/latest/errors/#retry)).
- На каждую операцию действует общий срок и лимит попыток; повторы и повторная
  авторизация их не обнуляют.
- Ответ `401` вызывает одну повторную авторизацию на все параллельные запросы, а
  `409` превращается в `DuplicateConflictError`, а не в успех.
- Лимит частоты включён по умолчанию: 1 запрос/с. Спецификация заявляет 2 запроса/с
  на DEMO и 5 в рабочей среде, но сервер отвечает `509` уже при 2 запросах/с;
  более высокую частоту по условиям договора задайте через
  `API_REQUESTS_PER_SECOND`
  ([как настроить](https://raspopovaa.github.io/apisdkopti24/latest/configuration/#rate-limit)).

Подробнее — в разделе [«Ошибки»](#ошибки).

### Журналы без секретов

По умолчанию SDK ничего не пишет. Если включить аудит, на каждую операцию
приходится ровно одно JSONL-событие с кодом результата, числом попыток и
временем выполнения. API key, пароли, идентификаторы карт и договоров и тела
ответов в журнал не попадают, а текст исключений короткий и очищенный.
Подробнее — в разделе [«Журналирование и аудит»](#журналирование-и-аудит).

### Отчёты и оплата по QR-коду

- `download_report_file_to()` пишет отчёт в файл потоком и заменяет файл
  атомарно: большой отчёт не держится в памяти, а недописанный файл не появится.
- Ответы, которые читаются в память, ограничены по размеру; пределы задаются
  переменными `API_MAX_JSON_RESPONSE_BYTES`, `API_MAX_IN_MEMORY_RESPONSE_BYTES` и
  `API_MAX_ERROR_RESPONSE_BYTES` или полями `max_json_response_bytes`,
  `max_in_memory_response_bytes` и `max_error_response_bytes` в `ConnectionSettings`.
- Мобильный профиль карты выпускается с подтверждением по SMS
  (`init_mpc` → `confirm_mpc`), а платёжная строка для QR приходит со сроком
  действия `end_date` и счётчиками `tries` и `transaction_count` от сервера.
  Подробнее — в [описании QR-платежей](https://raspopovaa.github.io/apisdkopti24/latest/qr-payments/).

## Установка

```bash
pip install apisdkopti24==0.0.2
```

или с [uv](https://docs.astral.sh/uv/):

```bash
uv add apisdkopti24==0.0.2
```

Проект в разработке, поэтому закрепляйте проверенную версию явно.

## Быстрый старт

Создайте рядом со скриптом файл `.env` и не добавляйте его в Git. Параметры
DEMO-стенда приведены в
[спецификации API](https://cdn.opti-24.ru/upload/upload/vip-api/api_specification.docx).

```env
API_BASE_URL=https://api.example.ru/vip/
API_KEY=your_api_key
API_LOGIN=your_login
API_PASSWORD=your_password
```

```python
import asyncio
from pathlib import Path

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    ContractSelectionError,
    EnvironmentCredentialsProvider,
)


async def main() -> None:
    env_file = Path(__file__).with_name(".env")
    settings = ConnectionSettings.from_env(env_file=env_file)
    credentials = EnvironmentCredentialsProvider.from_env(env_file=env_file)

    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        try:
            await client.auth.auth_user()
        except ContractSelectionError as exc:
            # Несколько договоров: SDK не выбирает первый без подтверждения.
            for contract_id, contract_number in exc.available_contracts:
                print(contract_id, contract_number)
            await client.auth.auth_user(contract_id=input("ID договора: ").strip())

        try:
            cards = await client.cards.get_cards_v2(page=1, onpage=5)
            print("Карт найдено:", cards.total_count)
        finally:
            await client.auth.logoff()


if __name__ == "__main__":
    asyncio.run(main())
```

Создавайте один `APIClient` на всё время жизни приложения, а не на каждый запрос.
Каждый вызов метода API тарифицируется, если в
[каталоге методов](https://raspopovaa.github.io/apisdkopti24/latest/methods/)
не указано обратное; повторы и повторная авторизация тоже расходуют запросы.
Подробнее — в разделе
[«Начало работы»](https://raspopovaa.github.io/apisdkopti24/latest/getting-started/).

## Что важно по спецификации

- **Договор выбирается явно:** большинство методов используют договор сессии;
  переданный `contract_id` имеет приоритет.
- **QR-платёж — отдельный контур API.** `generate_payment_qr` возвращает строку
  BER-TLV, а не изображение QR; срок действия нужно проверять по `end_date` перед
  показом. Корпоративный DEMO не проверяет QR-методы.
- **Суммы переводов и счетов** (`move_to_card`, `move_to_contract`, `order_invoice`)
  SDK передаёт строкой из `Decimal`, без округления; суммы лимитов — числом, как в
  спецификации. Состав запроса может отличаться от привычного REST: например,
  `update_template` использует `POST` с `_method=PUT`.
- **Тарификация и повторы заданы для каждой операции отдельно.** Не выводите их
  из HTTP-метода: SDK автоматически повторяет только операции, которые каталог
  помечает безопасными, и не повторяет изменение данных после неясного сбоя.

Подробности и ограничения — в [описании QR-платежей](https://raspopovaa.github.io/apisdkopti24/latest/qr-payments/),
[сопоставлении со спецификацией](https://raspopovaa.github.io/apisdkopti24/latest/spec-compatibility/)
и [каталоге операций](https://raspopovaa.github.io/apisdkopti24/latest/methods/).

## Ошибки

SDK проверяет и HTTP-статус, и `status.code` в теле ответа: успешный код в теле не
скроет неуспешный HTTP-ответ, и наоборот. Ошибки API наследуют `APIError`:

| Код | Исключение | Что делает SDK | Что делать приложению |
|---|---|---|---|
| `400` | `ValidationError` | — | Исправить параметры запроса |
| `401` | `NotAuthenticatedError` | Один раз переавторизуется и повторяет запрос | Проверить credentials, если ошибка осталась |
| `403` | `AccessDeniedError` | Не переавторизуется | Проверить роль, API key, IP, квоту и договор; читать текст сообщения |
| `404` | `NotFoundError` | — | Проверить идентификатор объекта |
| `409` | `DuplicateConflictError` | Не повторяет | Считать признаком дубля, а не успехом |
| `429`, `509` | `RateLimitError` | Повторяет только бесплатное чтение | Снизить частоту: без `509` устойчиво около 1 запроса/с |
| `5xx` | `ServerError` | Не повторяет | Повторить чтение позже; изменение повторять только после проверки состояния чтением |

Локальные сбои не выдают себя за ответ сервера и не наследуют `APIError`:
`OperationTimeoutError` и `RetryBudgetExceededError` (исчерпан общий бюджет
времени или попыток), `RequestValidationError` (неверный формат или диапазон
дат), `ResponseValidationError` (ответ не совпал с моделью),
`ContractSelectionError` (нужно выбрать договор), `APIConnectionError` (сервер
недоступен), `APIResponseTimeoutError` и `APINetworkError` (сервер не ответил;
изменение могло выполниться — проверьте состояние чтением).

```python
from apisdkopti24 import AccessDeniedError, APIError, OperationTimeoutError

try:
    cards = await client.cards.get_cards_v2(page=1, onpage=20)
except AccessDeniedError as exc:
    # Причина отказа часто есть только в тексте сообщения сервера.
    print("Доступ запрещён:", exc.server_messages)
except APIError as exc:
    print("Ошибка API:", exc.http_status_code, exc.api_status_code)
except OperationTimeoutError:
    # Сервер мог получить запрос: это не доказательство, что операция не выполнена.
    print("Истёк общий deadline операции")
```

`str(exc)` — короткая однострочная строка: email, телефоны, пары
`ключ=значение` и упоминания PIN или паролей из неё вырезаются. Полный ответ
сервера доступен только явно через `exc.get_raw_payload()`; не журналируйте его.

## Журналирование и аудит

По умолчанию SDK ничего не пишет на диск и не выводит в консоль. Чтобы видеть
сообщения, подключите обработчик к логгеру `apisdkopti24`:

```python
import logging

logging.getLogger("apisdkopti24").addHandler(logging.StreamHandler())
logging.getLogger("apisdkopti24").setLevel(logging.INFO)
```

Файлы журнала включаются явно — в `.env` или в `ConnectionSettings`
(`logger_file`, `request_log_file`):

```env
LOGGER_FILE=logs/sdk.log
REQUEST_LOG_FILE=logs/audit.jsonl
```

`REQUEST_LOG_FILE` — JSONL-аудит: на каждую операцию приходится ровно одно
итоговое событие `completed`, `failed` или `cancelled`. Пример события
(сокращено, значения условные):

```json
{"event": "failed", "operation": "get_cards_v2", "operation_id": "3f9c…", "sdk_error_code": "api_access_denied", "http_status_code": 403, "api_status_code": 403, "attempts_used": 1, "elapsed_ms": 184, "transient": false, "retry_allowed": false}
```

- `operation_id` — случайный локальный идентификатор, связывающий события одной
  операции;
- `sdk_error_code` — стабильный символьный код; у локального timeout это
  `operation_timeout`, а HTTP-код остаётся `null`, а не придумывается;
- `retry_allowed` уже учитывает идемпотентность метода — решайте о повторе по
  нему, а не по `transient`.

В журналы и аудит не попадают API key, пароли, session ID, телефоны, email,
идентификаторы карт и договоров, PIN, данные МПК, URL с идентификаторами, тела запросов и ответов, а
также текст сообщений сервера. Ожидаемые отказы (`4xx`, лимит частоты, локальная
валидация) пишутся с уровнем `WARNING`, серверные и сетевые сбои — `ERROR`,
отмена задачи — `INFO`.

Полный список полей и кодов — в разделе
[«Ошибки и retry»](https://raspopovaa.github.io/apisdkopti24/latest/errors/), настройка
журналов — в [«Конфигурации»](https://raspopovaa.github.io/apisdkopti24/latest/configuration/).

## Методы по задачам

В SDK **89 операций в 16 сервисах**. Ниже — карта методов; ссылки ведут к полным
описаниям параметров, тарификации и примерам.

| Задача | Сервисы и примеры методов |
|---|---|
| **Доступ и пользователи** | [`auth`](https://raspopovaa.github.io/apisdkopti24/latest/methods/auth/) — `auth_user`, `logoff`; [`users`](https://raspopovaa.github.io/apisdkopti24/latest/methods/users/) — `get_users`, `create_user`, `attach_card`; [`invites`](https://raspopovaa.github.io/apisdkopti24/latest/methods/invites/) — `create_invite`, `resend_invite` |
| **Топливные карты** | [`cards`](https://raspopovaa.github.io/apisdkopti24/latest/methods/cards/) — `get_cards_v2`, `block_card`, `reset_pin`; [`card_groups`](https://raspopovaa.github.io/apisdkopti24/latest/methods/card_groups/) — `get_card_groups`, `set_card_group` |
| **Договоры и расчёты** | [`contracts`](https://raspopovaa.github.io/apisdkopti24/latest/methods/contracts/) — `get_contract_data`, `get_payments`, `order_invoice`; [`ewallet`](https://raspopovaa.github.io/apisdkopti24/latest/methods/ewallet/) — `move_to_card`, `set_card_product`; [`final_prices`](https://raspopovaa.github.io/apisdkopti24/latest/methods/final_prices/) — `get_final_prices`, `check_purchase` |
| **Лимиты и шаблоны карт** | [`templates`](https://raspopovaa.github.io/apisdkopti24/latest/methods/templates/) — `create_template`, `create_template_limit`, ограничения; [`limits`](https://raspopovaa.github.io/apisdkopti24/latest/methods/limits/), [`region_limits`](https://raspopovaa.github.io/apisdkopti24/latest/methods/region_limits/), [`restrictions`](https://raspopovaa.github.io/apisdkopti24/latest/methods/restrictions/) |
| **Операции и отчётность** | [`transactions`](https://raspopovaa.github.io/apisdkopti24/latest/methods/transactions/) — `get_transactions_v2`, `get_transaction_detail`; [`reports`](https://raspopovaa.github.io/apisdkopti24/latest/methods/reports/) — `order_report`, `download_report_file` |
| **QR и справочники** | [`virtual_cards`](https://raspopovaa.github.io/apisdkopti24/latest/methods/virtual_cards/) — `init_mpc`, `generate_payment_qr`, `get_mpc_qr_list`; [`dictionaries`](https://raspopovaa.github.io/apisdkopti24/latest/methods/dictionaries/) — `get_dictionary`, `get_azs_list_v2` |

## Как проходит запрос

Один вызов метода сервиса проходит через восемь шагов. Каждый отвечает за одну
задачу и лежит в своём модуле.

<img src="https://raw.githubusercontent.com/raspopovaa/apisdkopti24/main/.github/assets/readme-request-flow.svg" alt="Путь вызова client.cards.get_cards_v2: 1 — сервис проверяет параметры моделью CardsV2Query (services/cards.py); 2 — создаются общий срок, лимит попыток и событие аудита (executor.py); 3 — при отсутствии сессии выполняется один authUser на все параллельные вызовы (session.py, authentication.py); 4 — по OperationSpec собирается запрос GET v2/cards с заголовками api_key, session_id и contract_id (executor.py, endpoints.py); 5 — запрос занимает один из слотов одновременных запросов, выдерживает интервал лимита частоты и списывает попытку из бюджета, а при 429, 509 или сбое сети повторяется, только если каталог это разрешает (resilience.py); 6 — httpx отправляет запрос без редиректов с timeout, равным остатку срока операции (transport.py); 7 — проверяются HTTP-статус и status.code, при 401 выполняется одна повторная авторизация и повтор (response.py, errors.py); 8 — ответ разбирается в CardsV2Response и пишется итоговое событие аудита (models/cards.py, error_reporting.py)" width="820">

Что важно на этом пути:

- **Повтор решает каталог операции, а не HTTP-метод.** Пауза и повтор после
  `429`, `509` или сбоя сети возможны только у операций, которые каталог помечает
  безопасными. Перевод средств или блокировка карты не повторяются.
- **Срок и попытки общие на всю операцию.** Ожидание слота, повторы и повторная
  авторизация расходуют один бюджет, а не начинают отсчёт заново.
- **Сессия восстанавливается один раз.** Если несколько запросов одновременно
  получили `401`, повторная авторизация выполняется один раз для всех.

## Структура репозитория

<img src="https://raw.githubusercontent.com/raspopovaa/apisdkopti24/main/.github/assets/readme-structure.svg" alt="Структура репозитория: слева папки src/apisdkopti24 (код SDK), specifications (каталог операций и контракты API), examples (примеры вызовов), docs (сайт документации), scripts (генераторы и сверка контрактов), tests, tools/spec_contract (аудит спецификации), typecheck и .github/workflows; справа слои кода SDK сверху вниз — публичный фасад (client.py, service_groups.py, composition.py), сервисы и модели (services/, models/, service_base.py, validation.py), реестр операций (endpoints.py, request_metadata.py, registry.py, policies.py), выполнение операции (executor.py, session.py, authentication.py, execution_budget.py), транспорт (transport.py, resilience.py, response.py, downloads.py, file_io.py) и сквозные модули (errors.py, error_reporting.py, logger.py, sanitization.py, config.py, credentials.py)" width="820">

<details>
<summary>Структура текстом</summary>

```text
src/apisdkopti24/       SDK: клиент, сервисы, модели, транспорт и повторы
specifications/         каталог 89 операций и контракты API 1.1.60 / QR 1.0.4
examples/methods/       исполняемые примеры вызовов API
tests/                  модульные проверки и сверка контрактов
tools/spec_contract/    инструменты валидации спецификаций
scripts/                генерация и служебные задачи проекта
typecheck/              проверки типов публичного интерфейса
docs/                   руководство, справочник и разбор совместимости
.github/workflows/      CI и публикационные процессы
```

</details>

Каталог операций задаёт параметры запросов, тарификацию, идемпотентность и
политику повтора; он служит источником метаданных SDK и связан с тестами контрактов.
Подробнее — в [обзоре архитектуры](https://raspopovaa.github.io/apisdkopti24/latest/architecture/).

## Документация

| Раздел | Что внутри |
|---|---|
| [Начало работы](https://raspopovaa.github.io/apisdkopti24/latest/getting-started/) | Установка, `.env` и первый запрос |
| [Конфигурация](https://raspopovaa.github.io/apisdkopti24/latest/configuration/) | Timeout, retry, лимит частоты, внедрение зависимостей |
| [Учебные примеры](https://raspopovaa.github.io/apisdkopti24/latest/examples/) | Пример, HTTP-запрос, ответ и ошибки для каждого из 89 методов |
| [Оплата по QR-коду](https://raspopovaa.github.io/apisdkopti24/latest/qr-payments/) | Выпуск МПК, срок жизни платёжной строки, блокировки |
| [Ошибки и retry](https://raspopovaa.github.io/apisdkopti24/latest/errors/) | Исключения, поля аудита и правила безопасных повторов |
| [Безопасность](https://raspopovaa.github.io/apisdkopti24/latest/security/) | Credentials, журналирование и транспорт |

## Разработка

<details>
<summary>Проверки перед изменением</summary>

```bash
git clone https://github.com/raspopovaa/apisdkopti24.git && cd apisdkopti24
uv sync --frozen --all-extras

uv run pytest
uv run ruff check src tests scripts tools typecheck
uv run black --check src tests scripts tools typecheck
uv run mypy src/apisdkopti24 typecheck
```

При изменении API-контрактов выполните дополнительные проверки из
[руководства по версиям и контрактам](https://raspopovaa.github.io/apisdkopti24/latest/versioning/).

</details>

## Лицензия

[MIT](https://github.com/raspopovaa/apisdkopti24/blob/main/LICENSE)
