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
| 🔁 **Безопасные повторы** | Повторяется только чтение; изменения данных после неясного сбоя не повторяются |
| 🚦 **Лимит частоты** | 2 запроса/с на DEMO и 5 запросов/с в рабочей среде по умолчанию, значение настраивается |
| ⏱ **Общий бюджет времени** | Один deadline и лимит попыток на операцию, включая retry и повторную авторизацию |
| 🧾 **Аудит без утечек** | Одно итоговое событие на операцию; ключи, пароли, идентификаторы и тела ответов в журнал не попадают |
| 📄 **Отчёты и QR** | Потоковое скачивание отчётов в файл, выпуск МПК и платёжные строки для QR |

## Установка

```bash
pip install apisdkopti24==3.4.5
```

или с [uv](https://docs.astral.sh/uv/):

```bash
uv add apisdkopti24==3.4.5
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

## Как API ведёт себя на практике

Сервер местами отличается от спецификации 1.1.60. SDK учитывает это в моделях, а
то, что остаётся на стороне приложения, стоит знать заранее:

- **`509` возможен и при соблюдении лимита частоты.** SDK автоматически повторяет
  только чтение; изменяющий запрос с таким ответом мог быть уже выполнен.
- **Код ошибки не всегда отражает суть.** Повтор `create_user` с тем же телефоном
  возвращает `403`, а не `409`; `set_card_group` с занятым именем создаёт вторую
  группу. Перед повторной отправкой изменения проверяйте состояние чтением.
- **`timestamp` транзакций — местное время с суффиксом `Z`.** Для UTC используйте
  поле `utc_time`.
- **Состав групп карт обновляется с задержкой.** Сразу после изменения `status` и
  `cards_count` могут быть пустыми.
- **Ответы расходятся со спецификацией в ряде полей** (`null` вместо строки, числа
  вместо строк, отсутствующие поля). Модели ослаблены точечно; при неожиданной
  форме SDK выбрасывает `ResponseValidationError`.

Полный перечень расхождений — в разделе
[«Совместимость со спецификацией»](https://raspopovaa.github.io/apisdkopti24/latest/spec-compatibility/).

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
| `429`, `509` | `RateLimitError` | Повторяет только чтение | Снизить частоту запросов |
| `5xx` | `ServerError` | Повторяет только чтение и только `500`, `502`–`504` | Проверить состояние чтением, прежде чем повторять изменение |

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

## Сервисы

<details>
<summary>16 сервисов, 89 операций</summary>

| Сервис | Операций | Назначение |
|---|---:|---|
| [`client.auth`](https://raspopovaa.github.io/apisdkopti24/latest/methods/auth/) | 3 | Авторизация и сведения о сессии |
| [`client.card_groups`](https://raspopovaa.github.io/apisdkopti24/latest/methods/card_groups/) | 4 | Группы топливных карт |
| [`client.cards`](https://raspopovaa.github.io/apisdkopti24/latest/methods/cards/) | 9 | Топливные карты |
| [`client.contracts`](https://raspopovaa.github.io/apisdkopti24/latest/methods/contracts/) | 7 | Договоры и документы |
| [`client.dictionaries`](https://raspopovaa.github.io/apisdkopti24/latest/methods/dictionaries/) | 4 | Справочники и торговые точки |
| [`client.ewallet`](https://raspopovaa.github.io/apisdkopti24/latest/methods/ewallet/) | 3 | Электронный кошелёк |
| [`client.final_prices`](https://raspopovaa.github.io/apisdkopti24/latest/methods/final_prices/) | 2 | Расчёт итоговой стоимости |
| [`client.invites`](https://raspopovaa.github.io/apisdkopti24/latest/methods/invites/) | 5 | Приглашения пользователей |
| [`client.limits`](https://raspopovaa.github.io/apisdkopti24/latest/methods/limits/) | 3 | Продуктовые лимиты |
| [`client.region_limits`](https://raspopovaa.github.io/apisdkopti24/latest/methods/region_limits/) | 3 | Региональные ограничения |
| [`client.reports`](https://raspopovaa.github.io/apisdkopti24/latest/methods/reports/) | 7 | Отчёты |
| [`client.restrictions`](https://raspopovaa.github.io/apisdkopti24/latest/methods/restrictions/) | 3 | Ограничители обслуживания |
| [`client.templates`](https://raspopovaa.github.io/apisdkopti24/latest/methods/templates/) | 16 | Шаблоны виртуальных карт |
| [`client.transactions`](https://raspopovaa.github.io/apisdkopti24/latest/methods/transactions/) | 4 | Транзакции |
| [`client.users`](https://raspopovaa.github.io/apisdkopti24/latest/methods/users/) | 7 | Пользователи и водители |
| [`client.virtual_cards`](https://raspopovaa.github.io/apisdkopti24/latest/methods/virtual_cards/) | 9 | Виртуальные карты и QR |

</details>

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
