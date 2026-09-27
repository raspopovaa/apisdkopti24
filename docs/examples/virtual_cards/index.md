---
description: "Учебные примеры: Виртуальные карты и оплата по QR"
---

# Виртуальные карты и оплата по QR

Выпуск виртуальных карт, мобильный профиль карты (МПК) на устройстве водителя и платёжная строка для оплаты по QR-коду.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Выпуск виртуальной карты](create_virtual_card.md) | POST `cards` | Да | Да | Нет |
| [Выпуск виртуальной карты по типу или шаблону](release_virtual_card.md) | POST `cards/release` | Да | Да | Нет |
| [Список мобильных профилей карт](get_mpc_qr_list.md) | GET `MPC` | Нет | Нет | Нет |
| [Выпуск мобильного профиля карты](init_mpc.md) | POST `cards/{card_id}/initMPC` | Да | Нет | Нет |
| [Подтверждение мобильного профиля карты](confirm_mpc.md) | POST `cards/{card_id}/confirmMPC` | Да | Нет | Нет |
| [Платёжная строка для оплаты по QR](generate_payment_qr.md) | POST `cards/{card_id}/pay` | Да | Нет | Нет |
| [Смена PIN или перевыпуск ключей МПК](update_mpc.md) | POST `cards/{card_id}/updateMPC` | Да | Нет | Нет |
| [Сброс счётчика мобильного профиля](reset_mpc.md) | POST `cards/{card_id}/resetMPC` | Да | Нет | Нет |
| [Удаление мобильного профиля карты](delete_mpc.md) | POST `cards/{card_id}/deleteMPC` | Да | Нет | Нет |
