---
description: Асинхронный Python SDK apisdkopti24 для корпоративного API топливных карт и QR-платежей.
---

# apisdkopti24

Асинхронная Python-библиотека для авторизации, управления картами, договорами,
транзакциями, отчётами, пользователями, виртуальными картами и оплатой по QR.

SDK объединяет HTTP-транспорт, управление сессией, выбор договора и Pydantic-
модели в одном асинхронном клиенте. Публичные операции сгруппированы по доменным
сервисам, поэтому по имени вызова видно, с какой частью API он работает.

!!! info "Текущая версия"
    Документация соответствует `apisdkopti24 3.3.2` и Python
    `>=3.11,<3.15`.

## Начните отсюда

| Раздел | Для чего нужен |
|---|---|
| [Установка и быстрый запуск](getting-started.md) | Установить пакет и выполнить первый запрос |
| [Конфигурация](configuration.md) | Настроить URL, credentials, timeout, retry и rate limit |
| [Миграция на 3.0](migration-3.0.md) | Перейти с линии 2.x на явный lifecycle и строгие модели |
| [Типовые сценарии](scenarios.md) | Собрать вызовы SDK в безопасные прикладные последовательности |
| [Оплата по QR-коду](qr-payments.md) | Выпустить МПК и безопасно сформировать платёжную строку |
| [Методы API](methods.md) | Найти вызов SDK, маршрут, DEMO-доступность и тарификацию |
| [Ошибки и retry](errors.md) | Обработать HTTP/API-ошибки и безопасные повторы |
| [API Reference](api-reference.md) | Посмотреть сигнатуры сервисов и модели данных |

Для первого подключения пройдите разделы в таком порядке:

1. [Установите пакет и выполните первый запрос](getting-started.md).
2. [Настройте credentials, timeout и rate limit](configuration.md).
3. [Добавьте обработку ошибок и безопасные retry](errors.md).
4. [Выберите операции в каталоге методов](methods.md).

## Основной стиль использования

SDK предоставляет типизированные композиционные сервисы:

```python
auth = await client.auth.auth_user()
cards = await client.cards.get_cards_v2(page=1, onpage=20)
reports = await client.reports.get_reports()
transactions = await client.transactions.get_transactions_v2(
    date_from="2026-07-01",
    date_to="2026-07-31",
)
```

Пример предполагает выбранный договор. При первом подключении с несколькими
договорами обработайте `ContractSelectionError`, выберите ID из
`available_contracts` и повторите `auth_user(contract_id=...)` — полный пример
приведён в [типовых сценариях](scenarios.md).

Прямых методов вида `client.get_cards_v2()` нет. Каждый метод находится в
своём доменном пространстве: `client.cards`, `client.reports`, `client.users` и
других.

## Управляйте lifecycle клиента

Используйте `APIClient` как асинхронный контекстный менеджер. Один экземпляр
переиспользует соединения, применяет общий rate limit и закрывает transport при
выходе из блока:

```python
async with APIClient(
    settings=settings,
    credentials_provider=credentials,
) as client:
    await client.auth.auth_user(contract_id="contract-id")
    cards = await client.cards.get_cards_v2(page=1, onpage=20)
    await client.auth.logoff()
```

Не создавайте клиент для каждого API-вызова. В web-приложении привяжите один
экземпляр к lifecycle процесса и закройте его при остановке приложения.

## Гарантии SDK

- единый декларативный registry маршрутов;
- проверка HTTP-кода и API-кода ответа;
- re-auth без рекурсивного захвата session lock;
- общий deadline и лимит попыток для одной бизнес-операции;
- retry только в соответствии с idempotency policy;
- percent-encoding параметров пути и запрет небезопасных сегментов;
- изоляция credentials от доменных сервисов;
- типизированные response/request модели на Pydantic v2;
- автоматическая сверка 91 внешнего метода с независимым YAML-контрактом.

## Дополнительные материалы

- [Архитектура SDK](architecture.md)
- [Информационная безопасность](security.md)
- [Совместимость со спецификацией](spec-compatibility.md)
- [Версионирование документации](versioning.md)
- [Исходный код на GitHub](https://github.com/raspopovaa/apisdkopti24)
- [Пакет apisdkopti24 на TestPyPI](https://test.pypi.org/project/apisdkopti24/)
