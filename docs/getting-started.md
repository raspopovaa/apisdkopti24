---
description: Установка apisdkopti24 из PyPI, настройка окружения и выполнение первого запроса к API.
---

# Установка и быстрый запуск

## Требования

- Python `>=3.11,<3.15`;
- доступ к API из разрешённой сети;
- API key, логин и пароль;
- HTTPS URL стенда с путём `/vip/`.

## Установка через pip {#pip}

Пакет и его runtime-зависимости устанавливаются из PyPI. Проект остаётся в
разработке, поэтому закрепляйте проверенную версию явно.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install apisdkopti24==0.0.8
```

## Установка через uv

```bash
uv venv --python 3.11
uv pip install apisdkopti24==0.0.8
```

Проверка установки:

```bash
.venv/bin/python -c \
  "from apisdkopti24 import APIClient, __version__; print(__version__, APIClient.__name__)"
```

Ожидаемый результат:

```text
0.0.8 APIClient
```

## Настройте `.env`

Создайте `.env` рядом с запускаемым скриптом:

```env
API_BASE_URL=https://api.example.ru/vip/
API_KEY=your_api_key
API_LOGIN=your_login
API_PASSWORD=your_password
API_REQUESTS_PER_SECOND=1
API_ALLOW_INSECURE_HTTP=false
```

Не добавляйте `.env` в Git.

`API_BASE_URL` должен включать схему и путь API. Для удалённых стендов используйте
HTTPS; HTTP без отдельного разрешения доступен только для loopback-адресов.

## Выполните первый запрос

Сохраните пример в `example.py` рядом с `.env`:

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

Запустите скрипт из созданного окружения:

```bash
python example.py
```

При первом подключении знать `contract_id` не требуется. Единственный договор
выбирается автоматически. Если договоров несколько, первая авторизация возвращает
`ContractSelectionError.available_contracts`; после выбора повторите авторизацию с
`contract_id`. SDK намеренно не выбирает первый договор без подтверждения. Метод,
которому `contract_id` передан явно, работает и без выбора договора.

!!! warning "Доступ к стенду"
    Пример выполняет реальные сетевые запросы. Если API принимает запросы только
    из определённой страны, сети или списка IP, запуск из другой сети завершится
    ошибкой доступа независимо от корректности SDK.

## Управляйте lifecycle клиента

!!! warning "Закрытие клиента не завершает сессию на сервере"
    `aclose()` и выход из `async with` закрывают только локальные ресурсы:
    HTTP-соединения и журнал SDK. Сессия на сервере живёт до истечения срока.
    Завершает её только явный `await client.auth.logoff()`: вызывайте его в
    `finally` перед закрытием клиента, как в примере выше.

Что происходит при закрытии:

- Контекстный менеджер закрывает transport и при успешном завершении, и при
  исключении.
- `logoff()` без активной сессии (например, авторизация не удалась) запрос не
  отправляет и возвращает `None`, поэтому из `finally` не возникает новой
  авторизации. Ответ `401` на `logoff()` тоже не запускает повторный вход: сессия
  на сервере уже истекла.
- После `aclose()` клиент больше не отправляет запросов: любой метод поднимает
  `SDKConfigurationError`, создайте новый `APIClient`.

Короткий скрипт вызывает `logoff()` перед выходом. Сервис или worker-процесс
создаёт один клиент при старте и закрывает его при остановке: так соединения,
ограничитель частоты и сессия переиспользуются между вызовами, а лишних входов
`authUser` нет.

## Проверьте нетарифицируемые read-only методы

Для быстрой проверки реального доступа без создания, изменения или удаления
данных используйте пример:

```bash
python examples/non_billable_real_api.py
```

Скрипт читает `.env`, авторизуется, выбирает договор и последовательно вызывает
только справочные/read-only методы, которые в контракте SDK помечены как
нетарифицируемые.

## Следующие шаги

1. Проверьте все параметры в разделе [Конфигурация](configuration.md).
2. Найдите нужный вызов в [каталоге методов](methods.md).
3. Добавьте обработку исключений из раздела [Ошибки и retry](errors.md).
