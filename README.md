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

<img src="https://raw.githubusercontent.com/raspopovaa/apisdkopti24/main/.github/assets/readme-demo.svg" alt="Демо: асинхронный клиент авторизуется и получает список топливных карт" width="820">

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

| | |
|---|---|
| ⚡ **Асинхронность и типы** | 89 операций в 16 сервисах на `httpx` и Pydantic, строгая проверка mypy |
| 🔐 **Сессия и договор** | Авторизация, выбор договора и однократное восстановление сессии без гонок |
| 🔁 **Повторы по метаданным** | SDK учитывает retry-класс и идемпотентность каждой операции; например, `resend_invite` может повторно отправить приглашение |
| 🚦 **Лимит частоты** | 2 запроса/с на DEMO и 5 запросов/с в рабочей среде по умолчанию, значение настраивается |
| ⏱ **Общий бюджет времени** | Один deadline и лимит попыток на операцию, включая retry и повторную авторизацию |
| 🧾 **Аудит без утечек** | Одно итоговое событие на операцию; ключи, пароли, идентификаторы и тела ответов в журнал не попадают |
| 📄 **Отчёты и QR** | Потоковое скачивание отчётов в файл, выпуск МПК и платёжные строки для QR |

## Установка

```bash
pip install apisdkopti24==3.4.6
```

или с [uv](https://docs.astral.sh/uv/):

```bash
uv add apisdkopti24==3.4.6
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

- **Выбор договора.** Если доступен один договор, `auth_user()` выбирает его автоматически. Если договоров несколько, укажите ровно один параметр — `contract_id` или `contract_number`; без выбора SDK сообщает `ContractSelectionError`.
- **QR-платёж — отдельный контур API.** `generate_payment_qr` возвращает строку BER-TLV, а не изображение; перед показом проверьте `end_date`. Корпоративный DEMO не проверяет QR-методы.
- **Формат запросов.** Денежные значения передаются строками; например, `update_template` использует `POST` с `_method=PUT`.
- **Повторы и тарификация.** Их правила заданы метаданными каждой операции. Например, `resend_invite` идемпотентен и допускает безопасный сетевой повтор, но каждый вызов тарифицируется и может повторно отправить приглашение.

Подробнее — в [каталоге операций](https://raspopovaa.github.io/apisdkopti24/latest/methods/), [описании QR-платежей](https://raspopovaa.github.io/apisdkopti24/latest/qr-payments/) и [сопоставлении со спецификацией](https://raspopovaa.github.io/apisdkopti24/latest/spec-compatibility/).

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
| `429`, `509` | `RateLimitError` | Повторяет согласно политике операции | Снизить частоту запросов |
| `5xx` | `ServerError` | Повторяет `500`, `502`–`504` только если это разрешено политикой операции | Проверить состояние чтением, прежде чем повторять изменение |

Локальные сбои не выдают себя за ответ сервера и не наследуют `APIError`:
`OperationTimeoutError` и `RetryBudgetExceededError` (исчерпан общий бюджет
времени или попыток), `RequestValidationError` (неверный формат или диапазон
дат), `ResponseValidationError` (ответ не совпал с моделью),
`ContractSelectionError` (нужно выбрать договор), `APIConnectionError` (сервер
недоступен).

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

В SDK **89 операций в 16 сервисах**. Ниже — карта методов; ссылки ведут к полным описаниям параметров, тарификации и примерам.

| Задача | Сервисы и примеры методов |
|---|---|
| **Доступ и пользователи** | [auth](https://raspopovaa.github.io/apisdkopti24/latest/methods/auth/) — `auth_user`, `logoff`; [users](https://raspopovaa.github.io/apisdkopti24/latest/methods/users/) — `get_users`, `create_user`, `attach_card`; [invites](https://raspopovaa.github.io/apisdkopti24/latest/methods/invites/) — `create_invite`, `resend_invite` |
| **Топливные карты** | [cards](https://raspopovaa.github.io/apisdkopti24/latest/methods/cards/) — `get_cards_v2`, `block_card`, `reset_pin`; [card_groups](https://raspopovaa.github.io/apisdkopti24/latest/methods/card_groups/) — `get_card_groups`, `set_card_group` |
| **Договоры и расчёты** | [contracts](https://raspopovaa.github.io/apisdkopti24/latest/methods/contracts/) — `get_contract_data`, `get_documents`; [ewallet](https://raspopovaa.github.io/apisdkopti24/latest/methods/ewallet/) — `get_payments`, `order_invoice`; [final_prices](https://raspopovaa.github.io/apisdkopti24/latest/methods/final_prices/) — `get_final_prices`, `check_purchase` |
| **Лимиты и шаблоны карт** | [templates](https://raspopovaa.github.io/apisdkopti24/latest/methods/templates/) — `create_template`, `create_template_limit`; [limits](https://raspopovaa.github.io/apisdkopti24/latest/methods/limits/), [region_limits](https://raspopovaa.github.io/apisdkopti24/latest/methods/region_limits/), [restrictions](https://raspopovaa.github.io/apisdkopti24/latest/methods/restrictions/) |
| **Операции и отчётность** | [transactions](https://raspopovaa.github.io/apisdkopti24/latest/methods/transactions/) — `get_transactions_v2`, `get_transaction_detail`; [reports](https://raspopovaa.github.io/apisdkopti24/latest/methods/reports/) — `order_report`, `download_report_file` |
| **QR и справочники** | [virtual_cards](https://raspopovaa.github.io/apisdkopti24/latest/methods/virtual_cards/) — `init_mpc`, `generate_payment_qr`, `get_mpc_qr_list`; [dictionaries](https://raspopovaa.github.io/apisdkopti24/latest/methods/dictionaries/) — `get_dictionary`, `get_azs_list_v2` |

## Структура репозитория

```text
src/apisdkopti24/       SDK: клиент, сервисы, модели, транспорт и повторы
specifications/         каталог операций и контракты API 1.1.60 / QR 1.0.4
examples/methods/       исполняемые примеры вызовов API
tests/                  модульные проверки и сверка контрактов
tools/spec_contract/    инструменты валидации спецификаций
scripts/                генерация и служебные задачи проекта
typecheck/              проверки типов публичного интерфейса
docs/                   руководство, справочник и разбор совместимости
.github/workflows/      CI и публикационные процессы
```

Каталог операций задаёт параметры запросов, тарификацию, идемпотентность и политику повтора; его метаданные сверяются с тестами контрактов. Подробнее — в [обзоре архитектуры](https://raspopovaa.github.io/apisdkopti24/latest/architecture/).

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
