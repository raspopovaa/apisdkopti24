# Методы API

Документация генерируется из runtime registry, публичных сигнатур, type hints, моделей SDK и метаданных спецификации.

!!! info "Покрытие"
    Опубликовано **89 операций** из 89, зарегистрированных в SDK.
    Методы МПК/QR временно исключены до отдельного решения по QR-спецификации.

| Сервис | Операций | Назначение |
|---|---:|---|
| [`client.auth`](methods/auth.md) | 3 | Авторизация и сведения о сессии |
| [`client.card_groups`](methods/card_groups.md) | 4 | Группы топливных карт |
| [`client.cards`](methods/cards.md) | 9 | Топливные карты |
| [`client.contracts`](methods/contracts.md) | 7 | Договоры и документы |
| [`client.dictionaries`](methods/dictionaries.md) | 4 | Справочники и торговые точки |
| [`client.ewallet`](methods/ewallet.md) | 3 | Электронный кошелек |
| [`client.final_prices`](methods/final_prices.md) | 2 | Расчет итоговой стоимости |
| [`client.invites`](methods/invites.md) | 5 | Приглашения пользователей |
| [`client.limits`](methods/limits.md) | 3 | Продуктовые лимиты |
| [`client.region_limits`](methods/region_limits.md) | 3 | Региональные ограничения |
| [`client.reports`](methods/reports.md) | 7 | Отчеты |
| [`client.restrictions`](methods/restrictions.md) | 3 | Ограничители обслуживания |
| [`client.templates`](methods/templates.md) | 16 | Шаблоны виртуальных карт |
| [`client.transactions`](methods/transactions.md) | 4 | Транзакции |
| [`client.users`](methods/users.md) | 7 | Пользователи и водители |
| [`client.virtual_cards`](methods/virtual_cards.md) | 9 | Виртуальные карты и QR |

## Общий формат ответа

Большинство методов возвращают типизированную модель SDK. Ответ проходит проверку Pydantic: обязательные поля, типы, вложенные модели, ограничения схемы и пользовательские валидаторы.

Подробные структуры и фактические правила проверки приведены в разделе [Типы данных](data-types/index.md).
