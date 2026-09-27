---
description: "Учебные примеры: Шаблоны виртуальных карт"
---

# Шаблоны виртуальных карт

Шаблон задаёт тип виртуальной карты и её лимиты, товарные и географические ограничения. Карты, выпущенные по шаблону, получают эти настройки.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список шаблонов](get_templates.md) | GET `vc/templates` | Нет | Нет | Да |
| [Создание шаблона](create_template.md) | POST `vc/templates` | Да | Да | Да |
| [Изменение шаблона](update_template.md) | POST `vc/templates/{template_id}` | Да | — | Да |
| [Удаление шаблона](delete_template.md) | DELETE `vc/templates/{template_id}` | Да | Да | Да |
| [Лимиты шаблона](get_template_limits.md) | GET `vc/templates/{template_id}/limits` | Нет | Нет | Да |
| [Добавление лимита в шаблон](create_template_limit.md) | POST `vc/templates/{template_id}/limits` | Да | Да | Да |
| [Изменение лимита шаблона](update_template_limit.md) | POST `vc/templates/{template_id}/limits/{limit_id}` | Да | — | Да |
| [Удаление лимита шаблона](delete_template_limit.md) | DELETE `vc/templates/{template_id}/limits/{limit_id}` | Да | Да | Да |
| [Товарные ограничители шаблона](get_template_restrictions.md) | GET `vc/templates/{template_id}/restrictions` | Нет | Нет | Да |
| [Добавление товарного ограничителя в шаблон](create_template_restriction.md) | POST `vc/templates/{template_id}/restrictions` | Да | Да | Да |
| [Изменение товарного ограничителя шаблона](update_template_restriction.md) | POST `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | — | Да |
| [Удаление товарного ограничителя шаблона](delete_template_restriction.md) | DELETE `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | — | Да |
| [Географические ограничения шаблона](get_template_georestrictions.md) | GET `vc/templates/{template_id}/georestrictions` | Нет | Нет | Да |
| [Добавление географического ограничения в шаблон](create_template_georestriction.md) | POST `vc/templates/{template_id}/georestrictions` | Да | Да | Да |
| [Изменение географического ограничения шаблона](update_template_georestriction.md) | POST `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | — | Да |
| [Удаление географического ограничения шаблона](delete_template_georestriction.md) | DELETE `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | — | Да |
