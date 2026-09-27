---
description: "Учебные примеры: Пользователи"
---

# Пользователи

Водители и другие пользователи клиента: список, создание, привязка к картам и договорам, удаление.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список пользователей](get_users.md) | GET `users` | Нет | Нет | Да |
| [Создание пользователя](create_user.md) | POST `users` | Да | Да | Да |
| [Привязка карты к пользователю](attach_card.md) | POST `users/{user_id}/attachCard` | Да | Да | Да |
| [Отвязка карты от пользователя](detach_card.md) | POST `users/{user_id}/detachCard` | Да | Да | Да |
| [Привязка договоров к пользователю](attach_contracts.md) | POST `users/{user_id}/attachContracts` | Да | Да | Да |
| [Отвязка договоров от пользователя](detach_contracts.md) | POST `users/{user_id}/detachContracts` | Да | Да | Да |
| [Удаление пользователя](delete_user.md) | DELETE `users/{user_id}` | Да | Да | Да |
