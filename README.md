# apisdkopti24 — Python SDK для API ОПТИ 24

[![CI](https://github.com/raspopovaa/apisdkopti24/actions/workflows/ci.yml/badge.svg)](https://github.com/raspopovaa/apisdkopti24/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-0f766e.svg)](https://raspopovaa.github.io/apisdkopti24/)
[![Python](https://img.shields.io/badge/Python-3.11--3.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/license/mit)

Асинхронный Python SDK для работы с корпоративным API топливных карт.

[Документация](https://raspopovaa.github.io/apisdkopti24/) ·
[Каталог методов](https://raspopovaa.github.io/apisdkopti24/latest/methods/) ·
[Сообщить об ошибке](https://github.com/raspopovaa/apisdkopti24/issues)

> [!IMPORTANT]
> Проект находится в разработке. Текущая версия публикуется в TestPyPI и не
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

Пока пакет размещён в TestPyPI. Зависимости устанавливаются отдельно из
основного PyPI, чтобы тестовый индекс не участвовал в их разрешении.

### uv

```bash
uv venv --python 3.11
uv pip install "httpx>=0.27,<1.0" "pydantic>=2.13.4,<3.0"
uv pip install --index-url https://test.pypi.org/simple/ \
  --no-deps apisdkopti24==3.3.3
```

### pip

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install "httpx>=0.27,<1.0" "pydantic>=2.13.4,<3.0"
python -m pip install --index-url https://test.pypi.org/simple/ \
  --no-deps apisdkopti24==3.3.3
```

Проверка импорта:

```bash
.venv/bin/python -c \
  "from apisdkopti24 import APIClient, __version__; print(__version__, APIClient.__name__)"
```

## Быстрый старт

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

Пример выполняет реальные сетевые запросы. Корректные credentials не отменяют
сетевые и географические ограничения API. Единственный договор выбирается
автоматически. Если договоров несколько, SDK не выбирает первый без подтверждения:
пример выводит доступные договоры и повторяет авторизацию с выбранным ID.

Контекстный менеджер закрывает HTTP-клиент даже при исключении, а блок `finally`
отправляет `logoff`, если авторизация уже состоялась. Для долгоживущих приложений
создавайте один `APIClient` на lifecycle приложения и не создавайте новый клиент
для каждого запроса.

## Использование

Методы сгруппированы по предметным областям:

```python
await client.auth.get_info()
await client.cards.get_cards_v2(page=1, onpage=20)
await client.transactions.get_transactions_v2(
    date_from="2026-07-01",
    date_to="2026-07-31",
)
await client.reports.get_reports()
```

Параметры публичных методов передаются по имени. JSON-операции возвращают
типизированный envelope `status/data/timestamp`.

Для проверки реального доступа без изменяющих операций используйте пример
`examples/non_billable_real_api.py`. Он вызывает только read-only методы,
которые в контракте SDK помечены как нетарифицируемые:

```bash
python examples/non_billable_real_api.py
```

Для последовательной ручной проверки всех 89 операций используйте интерактивный
сценарий. Перед каждым вызовом он показывает контракт, пример запроса и модели,
запрашивает параметры, а мутации выполняет только после явного подтверждения:

```bash
python examples/check_all_89_real_api.py --env-file .env.integration
```

Подробный порядок работы и ограничения безопасности описаны в
[руководстве по ручной проверке](https://raspopovaa.github.io/apisdkopti24/latest/manual-api-check/).

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

## Разработка

```bash
git clone https://github.com/raspopovaa/apisdkopti24.git
cd apisdkopti24
uv sync --extra dev

uv run pytest
uv run ruff check src tests scripts tools typecheck
uv run black --check src tests scripts tools typecheck
uv run mypy src/apisdkopti24 typecheck
```

Перед изменением API-контрактов также запустите сборку документации, описанную в
[руководстве проекта](https://raspopovaa.github.io/apisdkopti24/latest/versioning/).

## Лицензия

Проект распространяется на условиях лицензии MIT.
