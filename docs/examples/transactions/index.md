---
description: "Учебные примеры: Транзакции"
---

# Транзакции

Операции по картам и договору: покупки на АЗС, возвраты и корректировки за период, детали отдельной транзакции.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Транзакции договора за период](get_transactions_v2.md) | GET `transactions` | Нет | Да | Да |
| [Транзакции карты за период](get_card_transactions_v2.md) | GET `cards/{card_id}/transactions` | Нет | Да | Да |
| [Детали транзакции](get_transaction_detail.md) | GET `transactions/{transaction_id}` | Нет | Нет | Да |
| [Последние транзакции (API v1)](get_transactions_v1.md) | GET `transactions` | Нет | Да | Нет |
