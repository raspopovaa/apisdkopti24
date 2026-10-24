---
description: "Практическое применение SDK в пульте топливных карт: методы, бюджет тарифицируемых запросов, структура и архитектура."
---

# Практическое применение: пульт топливных карт

Пульт топливных карт: дашборд по договору, построенный на SDK `apisdkopti24`. Он
показывает баланс и расход, скидки и сервисный сбор, группы карт, последние транзакции,
карту заправок по регионам, структуру расхода, контроль подозрительных заправок и
расход запросов API.

- **Прототип:** [raspopovaa.github.io/apisdkopti24-dashboard](https://raspopovaa.github.io/apisdkopti24-dashboard/)
- **Репозиторий:** [raspopovaa/apisdkopti24-dashboard](https://github.com/raspopovaa/apisdkopti24-dashboard)

Дашборд в разработке. Опубликованный прототип статический: он не обращается к API,
четыре договора в нём построены по ответам DEMO, а синтетический договор генерируется по
обезличенному профилю. Сервер, который будет обращаться к API через SDK, ещё не написан.
На этой странице описано, как он будет устроен и сколько запросов потратит.

## Какие методы SDK использует дашборд

Тарификация указана по `specifications/api-methods.yaml`. Её нельзя определять по
HTTP-методу или названию: проверяйте колонку «Тариф» и страницу метода.

| Данные на экране | Вызов SDK | Тариф | DEMO |
|---|---|:---:|:---:|
| Договоры учётной записи | [`client.auth.auth_user()`](examples/auth/auth_user.md) | нет | да |
| Размер пакета и расход запросов | [`client.auth.get_info()`](examples/auth/get_info.md) | нет | да |
| Баланс, последний платёж, расход месяца в ₽ и литрах | [`client.contracts.get_contract_data()`](examples/contracts/get_contract_data.md) | **да** | да |
| Платежи за 3 месяца | [`client.contracts.get_payments()`](examples/contracts/get_payments.md) | **да** | да |
| История транзакций: цены, скидка, сбор, тип и регион АЗС, координаты | [`client.reports.order_report()`](examples/reports/order_report.md) | **да**¹ | да |
| Готовность отчёта | [`client.reports.get_report_jobs()`](examples/reports/get_report_jobs.md) | нет | да |
| Файл отчёта | [`client.reports.download_report_file_to()`](examples/reports/download_report_file.md) | **да** | нет |
| Транзакции внутри дня | [`client.transactions.get_transactions_v2()`](examples/transactions/get_transactions_v2.md) | **да** | да |
| Подробности транзакции по клику | [`client.transactions.get_transaction_detail()`](examples/transactions/get_transaction_detail.md) | нет | да |
| Карты, комментарии, группа карты | [`client.cards.get_cards_v2()`](examples/cards/get_cards_v2.md) | нет | да |
| Группы карт | [`client.card_groups.get_card_groups()`](examples/card_groups/get_card_groups.md) | нет | да |
| Названия, коды и цвета топлива; регионы | [`client.dictionaries.get_dictionary()`](examples/dictionaries/get_dictionary.md) | нет | да |
| АЗС: координаты, тип, цены на стеле | [`client.dictionaries.get_azs_list_v1()`](examples/dictionaries/get_azs_list_v1.md) | нет | да |

¹ SDK считает `order_report` тарифицируемым по худшему случаю. Таблица тарификации в
`get_info().data.methods_info` относит к платным заказ с отправкой на почту, а заказ без
`emails`: к бесплатным. Проверьте это для своего тарифа.

Ставки сервисного сбора и скидок в API не приходят: они берутся из договора и
приложений к нему.

## Как уложиться в 500 тарифицируемых запросов в месяц

Каждый вызов тарифицируемого метода: один запрос по тарифу. Бесплатный пакет на
500 запросов действует по текущим условиям обслуживания, но размер пакета зависит от
тарифа. Проверьте его в API-портале или в поле `client_info.Queries` ответа
`get_info()`. Дашборд показывает фактический остаток пакета по `get_info()`, а этот метод
бесплатный.

Главное правило: **API опрашивает сервер по своему расписанию, а не браузер.** Страница
раз в 10 секунд спрашивает у сервера готовые снимки блоков, но к API эти запросы не идут.
Поэтому расход не зависит от числа зрителей и открытых вкладок.

### Расписание тарифицируемых вызовов

Расчёт для одного договора и месяца из 31 дня.

| Задача | Вызов | Частота | Запросов в месяц |
|---|---|---|---:|
| Баланс, платёж, расход месяца | `get_contract_data` | раз в 2 часа, 12 в сутки | 372 |
| Транзакции за прошедшие сутки | `order_report` + `download_report_file_to` | раз в сутки ночью | 62 |
| Платежи | `get_payments` | только когда в `get_contract_data` меняется `last_payment_date` | ≈ 5 |
| **Итого регулярно** | | | **≈ 439** |
| Первичное заполнение при подключении договора: 3 месячных отчёта, платежи, данные договора | 3 × (`order_report` + `download_report_file_to`), `get_payments`, `get_contract_data` | один раз | 8 |
| Резерв на повторы после `429`, `509` и сбоев сети | | | ≈ 53 |
| **Всего** | | | **≤ 500** |

Если нужны транзакции внутри дня, тарифицируемые запросы приходится перераспределить:

| Вариант | Расписание | Запросов в месяц |
|---|---|---:|
| Экономный (выше) | договор раз в 2 часа, транзакции из суточного отчёта | ≈ 439 |
| Со свежими транзакциями | договор раз в 3 часа (248), `get_transactions_v2` 4 раза в рабочее время (124), суточный отчёт (62), платежи (≈ 5) | ≈ 439 |
| Не укладывается | договор раз в час (744) | > 500 |

Каждая страница `get_transactions_v2`: отдельный тарифицируемый вызов. Окно в несколько
часов обычно помещается на одну страницу (размер задаёт `page_limit`), но у большого парка
страниц может быть больше.

### Бесплатные вызовы

Их тоже ограничивает лимит частоты, но пакет они не расходуют.

| Вызов | Частота |
|---|---|
| `get_info` | раз в час: факт расхода и остаток пакета |
| `get_cards_v2`, `get_card_groups` | раз в час: новые карты, комментарии и группы |
| `get_dictionary(name="Goods")`, `get_dictionary(name="Region")` | раз в сутки |
| `get_azs_list_v1` | раз в сутки, постранично |
| `get_report_jobs` | пока отчёт формируется: месячный отчёт готовится около 5 минут |
| `get_transaction_detail` | по клику пользователя |
| `auth_user` | при старте и при истечении сессии |

### Что ещё расходует запросы

- **Повторы.** SDK повторяет только операции, которые каталог помечает безопасными, и
  только после `429`, `509` или сбоя сети. Каждая повторная попытка: отдельный запрос по
  тарифу. Число попыток задаётся в [конфигурации](configuration.md).
- **Несколько договоров.** Расписание считается на договор. Для двух договоров
  регулярный расход удваивается: реже опрашивайте второстепенные договоры.
- **Повторная авторизация.** `auth_user` бесплатен, но повтор тарифицируемого вызова
  после неё снова расходует запрос.
- **DEMO.** DEMO не тарифицируется и не поддерживает скачивание отчёта, поэтому
  расписание на нём проверить целиком нельзя.

## Архитектура

```text
API ОПТИ 24 ── SDK apisdkopti24 ── сервер дашборда (FastAPI, один процесс)
                (1 запрос/с,        │ сборщик: фоновые задачи по расписанию
                 безопасные         │ база: история транзакций за 3 месяца,
                 повторы)           │       снимки блоков, счётчик запросов
                                    │ API для браузера: снимки блоков с ETag
                                    ▼
             браузер ── раз в 10 с: GET снимков (304, если данные не изменились) ── дашборд
```

- **Сборщик.** Один `APIClient` на всё время жизни сервера, как асинхронный менеджер
  контекста. Расписание из раздела выше. Ключ API, логин и пароль доступны только серверу
  через провайдер учётных данных; в браузер, журналы и базу они не попадают.
- **База.** При подключении договора сервер загружает транзакции за 3 месяца месячными
  отчётами (период одного заказа: не больше календарного месяца), затем добавляет
  суточный отчёт каждую ночь.
- **API для браузера.** Планируемые маршруты: `GET /api/contracts`,
  `GET /api/contracts/{key}/blocks/{block}?month=YYYY-MM`,
  `GET /api/contracts/{key}/version`. В адресах: только непрозрачный ключ договора, без
  ID договора.
- **Страница.** Статическая: HTML, ECharts и границы регионов Natural Earth. Она
  обновляет только блоки, видимые на экране, и не запрашивает данные, пока вкладка скрыта.

Что делает SDK, а что: сервер API:

| SDK | Сервер API |
|---|---|
| проверяет параметры до отправки | тарифы, пакет запросов и квоты |
| ограничивает частоту, по умолчанию 1 запрос/с | роли учётной записи и видимость объектов |
| повторяет только безопасные операции | IP-ограничения и привязка к договору |
| восстанавливает сессию после `401` один раз | ответы `403 accessDenied` и `509` |

При `403 accessDenied` SDK не переавторизуется: это ограничение роли, ключа, IP, тарифа
или привязки к договору, его нужно устранять в API-портале.

## Структура репозитория дашборда

```text
prototype/dashboard.html          прототип страницы (HTML, CSS, JavaScript)
prototype/russia-regions.json     границы регионов РФ (Natural Earth 1:10m)
prototype/synthetic-profile.json  агрегатный профиль синтетического договора
scripts/build_regions_geo.py      подготовка границ регионов
scripts/build_synthetic_profile.py  профиль синтетического договора из отчёта
scripts/serve_prototype.py        локальный запуск прототипа
src/fuel_portal/                  синтетические данные автопарка для демо и тестов
docs/dashboard-spec.md            описание блоков, данных и формул
.github/workflows/pages.yml       публикация прототипа на GitHub Pages
```

## Пример: суточный отчёт о транзакциях

`order_report` и `download_report_file_to` тарифицируются: каждый вызов расходует запрос
по тарифу. `get_report_jobs` бесплатен. Скачивание отчёта на DEMO недоступно.

```python
import asyncio
from datetime import date, timedelta
from pathlib import Path

from apisdkopti24 import (
    APIClient,
    ConnectionSettings,
    EnvironmentCredentialsProvider,
    ReportWaitTimeoutError,
)

CONTRACT_ID = "contract-id"


async def download_yesterday(client: APIClient, destination: Path) -> Path | None:
    yesterday = date.today() - timedelta(days=1)
    order = await client.reports.order_report(
        report_id="tsc_report_transaction_reriod",
        format="xlsx",  # доступные форматы: поле formats в get_reports()
        params={
            "start_date": yesterday.isoformat(),
            "end_date": date.today().isoformat(),
            "id_agreement": [CONTRACT_ID],
        },
    )
    job_ids = order.data.job_id or []
    if not job_ids:
        return None  # задача не создана: заказ не повторяется автоматически
    try:
        # Опрашивает только бесплатный get_report_jobs, пока available_after не станет 0.
        job = await client.reports.wait_for_report(job_id=job_ids[0], timeout=900)
    except ReportWaitTimeoutError:
        return None  # задача осталась в списке: продолжите ожидание в следующем запуске
    return await client.reports.download_report_file_to(
        job_id=job.job_id, destination=destination
    )


async def main() -> None:
    settings = ConnectionSettings.from_env()
    credentials = EnvironmentCredentialsProvider.from_env()
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        await client.auth.auth_user(contract_id=CONTRACT_ID)
        try:
            path = await download_yesterday(client, Path("yesterday-report.xlsx"))
            print("Отчёт:", path or "не готов")
        finally:
            await client.auth.logoff()


if __name__ == "__main__":
    asyncio.run(main())
```

Отчёт заказывается один раз за сутки. Если задача не появилась или не успела
сформироваться, сборщик не повторяет заказ вслепую: повторный заказ означает новый
тарифицируемый запрос. `wait_for_report` ждёт между опросами столько, сколько
показывает `available_after`, но не меньше `poll_interval` (по умолчанию 30 секунд).
`available_after = 0` не гарантирует готовность файла: если скачивание ответило
`NotFoundError` «Формирование отчета не завершено», повторите его через несколько
минут.

Дальше: [типовые сценарии](scenarios.md) и [ошибки и повторы](errors.md).
