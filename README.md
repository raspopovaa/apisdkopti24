# apisdkopti24 — Python SDK для Opti24 API (ОПТИ 24)

Документация, комментарии и собственные диагностические сообщения SDK написаны
по-русски. Для обработки ошибок используйте классы исключений и машинные коды,
а не сравнение текста. Сообщения сторонних библиотек и данные сервера сохраняют
исходный язык; подробнее — [язык сообщений](docs/errors.md#язык-сообщений).

[![CI](https://github.com/raspopovaa/apisdkopti24/actions/workflows/ci.yml/badge.svg)](https://github.com/raspopovaa/apisdkopti24/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-0f766e.svg)](https://raspopovaa.github.io/apisdkopti24/)
[![Python](https://img.shields.io/badge/Python-3.11--3.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/license/mit)

Асинхронный Python SDK для работы с **Opti24 API** — корпоративным
**API топливных карт АЗС** (сервис ОПТИ 24): карты, договоры, транзакции,
отчёты, лимиты и оплата по QR-коду.

[Документация](https://raspopovaa.github.io/apisdkopti24/) ·
[Каталог методов](https://raspopovaa.github.io/apisdkopti24/latest/methods/) ·
[Сообщить об ошибке](https://github.com/raspopovaa/apisdkopti24/issues)

> [!IMPORTANT]
> Проект находится в разработке. Публикация пакета в PyPI не означает
> production-готовность: текущая версия не
> предназначена для production-интеграций без предварительного тестирования.

## Возможности

- типизированные асинхронные методы на базе `httpx` и Pydantic;
- доменные сервисы `client.auth`, `client.cards`, `client.reports` и другие;
- управление сессией, выбор договора и безопасное восстановление авторизации;
- общий deadline и единый лимит HTTP-попыток на бизнес-операцию;
- retry только для разрешённых политикой операций;
- ограничение частоты и числа параллельных запросов;
- единая обработка HTTP- и API-ошибок;
- потоковое скачивание файлов отчётов;
- выпуск МПК и формирование одноразовых платёжных строк для QR-кодов;
- каталог методов с DEMO-доступностью и тарификацией.

## Требования

- Python `>=3.11,<3.15`;
- URL стенда, API key, логин и пароль;
- доступ к API из разрешённой сети.

## Установка

Стабильный артефакт текущей версии устанавливается из PyPI. Та же версия
предварительно проверяется через TestPyPI в процессе выпуска.

### uv

Создайте виртуальное окружение и установите SDK:

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install apisdkopti24==3.3.11
```

### pip

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install apisdkopti24==3.3.11
```

Проверка импорта:

```bash
.venv/bin/python -c \
  "from apisdkopti24 import APIClient, __version__; print(__version__, APIClient.__name__)"
```

## Быстрый старт

Параметры для входа на DEMO-стенд указаны в спецификации (https://cdn.opti-24.ru/upload/upload/vip-api/api_specification.docx).
Создайте рядом со скриптом файл `.env`:

```env
API_BASE_URL=https://api.example.ru/vip/
API_KEY=your_api_key
API_LOGIN=your_login
API_PASSWORD=your_password
```

Не добавляйте `.env` в Git.

Сохраните пример как `example.py` и запустите его командой
`python example.py`:

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

    async with APIClient(
        settings=settings,
        credentials_provider=credentials,
    ) as client:
        try:
            auth = await client.auth.auth_user()
        except ContractSelectionError as exc:
            print("Доступные договоры:")
            for contract_id, contract_number in exc.available_contracts:
                print(contract_id, contract_number)
            contract_id = input("Введите ID договора: ").strip()
            auth = await client.auth.auth_user(contract_id=contract_id)

        try:
            cards = await client.cards.get_cards_v2(page=1, onpage=5)
            print("Договоров:", len(auth.data.contracts))
            print("Карт найдено:", cards.total_count)
        finally:
            await client.auth.logoff()


if __name__ == "__main__":
    asyncio.run(main())
```

### Что делает пример

1. `Path(__file__).with_name(".env")` находит `.env` рядом со скриптом независимо
   от каталога, из которого запущена команда.
2. `ConnectionSettings` загружает настройки соединения, а
   `EnvironmentCredentialsProvider` — API key, логин и пароль. Секреты не нужно
   записывать в исходный код.
3. `async with APIClient(...)` открывает HTTP-клиент и гарантированно закрывает
   сетевые ресурсы при выходе из блока, в том числе после исключения.
4. `auth_user()` авторизует пользователя. Единственный договор выбирается
   автоматически. Если доступны несколько договоров, SDK не выбирает первый без
   подтверждения: пример выводит их и повторяет авторизацию с введённым
   `contract_id`.
5. `get_cards_v2(page=1, onpage=5)` получает первую страницу, содержащую не более
   пяти карт. `cards.total_count` показывает общее количество найденных карт, а не
   только число элементов на этой странице.
6. Блок `finally` вызывает `logoff()` даже при ошибке получения карт и тем самым
   завершает серверную сессию. `asyncio.run(main())` запускает всю асинхронную
   последовательность.

Пример выполняет реальные сетевые запросы. Корректные credentials не отменяют
сетевые, географические и серверные ограничения API. Для долгоживущего приложения
создавайте один `APIClient` на весь жизненный цикл приложения, а не новый клиент
для каждого запроса.

## Использование

Клиент объединяет 89 операций в предметные сервисы. Название атрибута показывает,
с какой областью API работает метод:

| Сервис | Операций | Назначение |
|---|---:|---|
| [`client.auth`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/auth/) | 3 | Авторизация и сведения о сессии |
| [`client.card_groups`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/card_groups/) | 4 | Группы топливных карт |
| [`client.cards`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/cards/) | 9 | Топливные карты |
| [`client.contracts`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/contracts/) | 7 | Договоры и документы |
| [`client.dictionaries`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/dictionaries/) | 4 | Справочники и торговые точки |
| [`client.ewallet`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/ewallet/) | 3 | Электронный кошелёк |
| [`client.final_prices`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/final_prices/) | 2 | Расчёт итоговой стоимости |
| [`client.invites`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/invites/) | 5 | Приглашения пользователей |
| [`client.limits`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/limits/) | 3 | Продуктовые лимиты |
| [`client.region_limits`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/region_limits/) | 3 | Региональные ограничения |
| [`client.reports`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/reports/) | 7 | Отчёты |
| [`client.restrictions`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/restrictions/) | 3 | Ограничители обслуживания |
| [`client.templates`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/templates/) | 16 | Шаблоны виртуальных карт |
| [`client.transactions`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/transactions/) | 4 | Транзакции |
| [`client.users`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/users/) | 7 | Пользователи и водители |
| [`client.virtual_cards`](https://raspopovaa.github.io/apisdkopti24/3.3/methods/virtual_cards/) | 9 | Виртуальные карты и QR |

Ссылки ведут к полному описанию параметров, возвращаемых моделей, доступности на
стендах и тарификации. Следующие вызовы выполняются внутри уже авторизованного
`async with APIClient(...) as client` из примера выше.

### Получить карты договора

```python
cards = await client.cards.get_cards_v2(
    page=1,
    onpage=20,
)

print("Всего карт:", cards.total_count)
for card in cards.result:
    print(card.id, card.number, card.status_name, card.product_name)
```

Ответ уже проверен Pydantic и представлен моделью `CardsV2Response`. Свойства
`cards.total_count` и `cards.result` дают удобный доступ к данным envelope
`status/data/timestamp`.

### Получить документы и транзакции за период

```python
documents = await client.contracts.get_documents(
    date_start="2026-07-01",
    date_end="2026-07-31",
    page=1,
    on_page=20,
)

for document in documents.data.result or []:
    print(document.number, document.total, document.currency)

transactions = await client.transactions.get_transactions_v2(
    date_from="2026-07-01",
    date_to="2026-07-31",
    page_limit=100,
    page_offset=0,
)

for transaction in transactions.data.result or []:
    print(transaction.timestamp, transaction.product_name, transaction.sum)
```

SDK использует выбранный при авторизации договор. Если нужно обратиться к другому
доступному договору, передайте его явно: `contract_id="contract-id"`.

Для выполненных операций SDK записывает одно терминальное audit-событие:
`completed`, `failed` или `cancelled`. Ошибка содержит безопасный символьный
`sdk_error_code`; HTTP- и API-коды присутствуют только тогда, когда сервер вернул
ответ. Например, локальный `OperationTimeoutError` записывается как
`operation_timeout` без фиктивного HTTP-кода. События одной операции связаны
локальным `operation_id` и содержат `elapsed_ms` и `attempts_used`.
`error_message` формируется из локального каталога: текст ответа сервера и
неизвестные типы ошибок не попадают в audit. Очищенный текст сервера выводится
только в `str(APIError)` и `APIError.server_messages`.
Полный ответ доступен только через `APIError.get_raw_payload()` для явной
диагностики. Ошибки формата и диапазона дат являются `RequestValidationError`
без HTTP-кода. Текстовый audit также содержит код, причину и `operation_id`.
Поле
`transient` описывает временный характер причины, а `retry_allowed` дополнительно
учитывает retry policy и идемпотентность конкретного метода. `auth_user` также
пишет terminal-событие, включая timeout и ошибку выбора договора. Полная таблица
полей приведена в
[руководстве по обработке ошибок](https://raspopovaa.github.io/apisdkopti24/latest/errors/).

## Документация

Полное руководство опубликовано на
[GitHub Pages](https://raspopovaa.github.io/apisdkopti24/).

| Раздел | Содержание |
|---|---|
| [Начало работы](https://raspopovaa.github.io/apisdkopti24/latest/getting-started/) | Установка, `.env` и первый запрос |
| [Конфигурация](https://raspopovaa.github.io/apisdkopti24/latest/configuration/) | Timeout, retry, rate limit и dependency injection |
| [Методы API](https://raspopovaa.github.io/apisdkopti24/latest/methods/) | Сигнатуры, маршруты, DEMO-доступность и тарификация |
| [Типовые сценарии](https://raspopovaa.github.io/apisdkopti24/latest/scenarios/) | Прикладные последовательности вызовов |
| [Ручная проверка 89 методов](https://raspopovaa.github.io/apisdkopti24/latest/manual-api-check/) | Интерактивная сверка запросов, моделей и ответов |
| [Оплата по QR-коду](https://raspopovaa.github.io/apisdkopti24/latest/qr-payments/) | Выпуск МПК и формирование платёжной строки |
| [Ошибки и retry](https://raspopovaa.github.io/apisdkopti24/latest/errors/) | Исключения и правила безопасных повторов |
| [Архитектура](https://raspopovaa.github.io/apisdkopti24/latest/architecture/) | Слои SDK и зависимости |
| [Безопасность](https://raspopovaa.github.io/apisdkopti24/latest/security/) | Credentials, журналирование и транспорт |
| [API Reference](https://raspopovaa.github.io/apisdkopti24/latest/api-reference/) | Сервисы и модели данных |

Если вы впервые подключаете SDK, начните с [установки и быстрого
запуска](https://raspopovaa.github.io/apisdkopti24/latest/getting-started/), затем
проверьте [конфигурацию](https://raspopovaa.github.io/apisdkopti24/latest/configuration/)
и правила [обработки ошибок](https://raspopovaa.github.io/apisdkopti24/latest/errors/).

## Разработка и проверка изменений

```bash
git clone https://github.com/raspopovaa/apisdkopti24.git
cd apisdkopti24
uv sync --frozen --all-extras

uv run pytest
uv run ruff check src tests scripts tools typecheck
uv run black --check src tests scripts tools typecheck
uv run mypy src/apisdkopti24 typecheck
```

При изменении API-контрактов выполните дополнительные проверки из
[руководства по версиям и контрактам](https://raspopovaa.github.io/apisdkopti24/latest/versioning/).

## Лицензия

Проект распространяется на условиях лицензии MIT.
