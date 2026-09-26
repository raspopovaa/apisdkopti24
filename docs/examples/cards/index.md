---
description: "Учебные примеры: Топливные карты"
---

# Топливные карты

Получение списка карт и сведений о карте, блокировка, комментарии, водители и сброс счётчика неверных вводов PIN.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список карт договора (API v2)](get_cards_v2.md) | GET `cards` | Нет | Нет | Да |
| [Список карт договора (API v1)](get_cards_v1.md) | GET `cards` | Нет | Да | Да |
| [Сведения о карте](get_card_detail.md) | GET `cards` | Нет | Да | Да |
| [Карты группы](get_cards_by_group.md) | GET `cards` | Нет | Нет | Нет |
| [Водители карты](get_card_drivers.md) | GET `cards/{card_id}/drivers` | Нет | Да | Да |
| [Блокировка и разблокировка карт](block_card.md) | POST `blockCard` | Да | Да | Да |
| [Комментарий к карте](set_card_comment.md) | POST `setCardComment` | Да | Да | Да |
| [Запрос кода для сброса PIN](verify_pin.md) | POST `cards/{card_id}/verifyPIN` | Да | Нет | Да |
| [Сброс счётчика неверных вводов PIN](reset_pin.md) | POST `cards/{card_id}/resetPIN` | Да | Да | Нет |
