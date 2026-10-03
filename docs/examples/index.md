---
description: "Учебные примеры вызова методов SDK: код, HTTP-запрос, ответ и ошибки."
---

# Учебные примеры

Каждый пример — короткий запускаемый скрипт и страница с его разбором:

- **Пример** — код вызова метода с обработкой характерных ошибок;
- **Что отправляет SDK** — HTTP-запрос и таблица полей: где передаётся каждое
  поле и в каком виде;
- **Что возвращает API** — пример ответа, модель проверки и вывод примера;
- **Ошибки** — ответы API с ошибкой, исключения SDK с их текстом, причины и
  что делать; отдельно — ошибки, которые SDK находит до отправки запроса.

Запросы и тексты исключений на страницах не написаны вручную: генератор
выполняет каждый пример на подставном транспорте и записывает, что отправил
и выбросил SDK. Проверка в CI не даёт примерам разойтись с кодом.

## Как запустить пример

1. Установите SDK по инструкции из раздела
   [Установка через pip](../getting-started.md#pip).
2. Создайте `.env` по образцу `.env.example`: `API_BASE_URL`, `API_KEY`,
   `API_LOGIN`, `API_PASSWORD` и `API_CONTRACT_ID`.
3. Замените в начале файла примера условные значения своими.
4. Выполните `python examples/methods/<раздел>/<метод>.py`.

Примеры, которые изменяют данные или тарифицируются, спрашивают подтверждение
перед вызовом. Начинайте с DEMO-стенда.

## Примеры по разделам

### Авторизация

Вход с выбором договора, статистика обращений к API по тарифу и завершение серверной сессии.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Авторизация и выбор договора](auth/auth_user.md) | POST `authUser` | Нет | Нет | Да |
| [Статистика обращений к API](auth/get_info.md) | GET `info` | Нет | Нет | Да |
| [Завершение сессии](auth/logoff.md) | GET `logoff` | Нет | Нет | Да |

### Группы карт

Группы объединяют карты договора: на группу можно назначить лимиты и ограничения сразу для всех её карт.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список групп карт](card_groups/get_card_groups.md) | GET `cardGroups` | Нет | Нет | Да |
| [Создание и переименование группы карт](card_groups/set_card_group.md) | POST `setCardGroup` | Да | Да | Да |
| [Добавление и удаление карт в группе](card_groups/set_cards_to_group.md) | POST `setCardsToGroup` | Да | Да | Да |
| [Удаление группы карт](card_groups/remove_card_group.md) | POST `removeCardGroup` | Да | Да | Да |

### Топливные карты

Получение списка карт и сведений о карте, блокировка, комментарии, водители и сброс счётчика неверных вводов PIN.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список карт договора (API v2)](cards/get_cards_v2.md) | GET `cards` | Нет | Нет | Да |
| [Список карт договора (API v1)](cards/get_cards_v1.md) | GET `cards` | Нет | Да | Да |
| [Сведения о карте](cards/get_card_detail.md) | GET `cards` | Нет | Да | Да |
| [Карты группы](cards/get_cards_by_group.md) | GET `cards` | Нет | Нет | Нет |
| [Водители карты](cards/get_card_drivers.md) | GET `cards/{card_id}/drivers` | Нет | Да | Да |
| [Блокировка и разблокировка карт](cards/block_card.md) | POST `blockCard` | Да | Да | Да |
| [Комментарий к карте](cards/set_card_comment.md) | POST `setCardComment` | Да | Да | Да |
| [Запрос кода для сброса PIN](cards/verify_pin.md) | POST `cards/{card_id}/verifyPIN` | Да | Нет | Да |
| [Сброс счётчика неверных вводов PIN](cards/reset_pin.md) | POST `cards/{card_id}/resetPIN` | Да | Да | Нет |

### Договоры и документы

Баланс и реквизиты договора, платежи, счета, закрывающие документы и заказ новых карт.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Данные договора и баланс](contracts/get_contract_data.md) | GET `getPartContractData` | Нет | Да | Да |
| [Платежи по договору](contracts/get_payments.md) | GET `getPayments` | Нет | Да | Да |
| [Счета на оплату](contracts/get_invoices.md) | GET `invoices` | Нет | Нет | Да |
| [Заказ счёта на оплату](contracts/order_invoice.md) | POST `invoice` | Да | Нет | Нет |
| [Закрывающие документы](contracts/get_documents.md) | GET `documents` | Нет | Нет | Нет |
| [Отправка документов на email](contracts/order_documents_email.md) | POST `documents` | Да | Да | Нет |
| [Заказ новых карт](contracts/order_cards.md) | POST `orderCards` | Да | Да | Нет |

### Справочники и АЗС

Общие справочники (статусы, товары, регионы, офисы) и поиск торговых точек с фильтрами.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Общий справочник](dictionaries/get_dictionary.md) | GET `getDictionary` | Нет | Нет | Да |
| [Поиск АЗС (API v2)](dictionaries/get_azs_list_v2.md) | GET `azs` | Нет | Нет | Нет |
| [Список АЗС (API v1)](dictionaries/get_azs_list_v1.md) | GET `AZS` | Нет | Нет | Да |
| [Фильтры поиска АЗС](dictionaries/get_azs_filters.md) | GET `azs/filters` | Нет | Нет | Нет |

### Электронный кошелёк

Перевод карты на кошелёк и обратно, пополнение кошелька карты с договора и возврат средств на договор.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Смена продукта карты](ewallet/set_card_product.md) | POST `setCardProduct` | Да | Да | Да |
| [Пополнение кошелька карты](ewallet/move_to_card.md) | POST `moveToCard` | Да | Да | Да |
| [Возврат средств с кошелька на договор](ewallet/move_to_contract.md) | POST `moveToContract` | Да | Да | Да |

### Итоговые цены

Расчёт цены товаров для карты на конкретной АЗС с учётом тарифа договора и проверка возможности покупки.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Итоговая цена товаров на АЗС](final_prices/get_final_prices.md) | POST `cards/{card_id}/calculatePrices` | Нет | Нет | Нет |
| [Проверка возможности покупки](final_prices/check_purchase.md) | POST `cards/{card_id}/checkPurchase` | Нет | Нет | Нет |

### Приглашения

Регистрация пользователей по приглашению: создание, список, повторная отправка, продление и удаление.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Создание приглашения](invites/create_invite.md) | POST `invites` | Да | Да | Нет |
| [Список приглашений](invites/get_invites.md) | GET `invites` | Нет | Нет | Да |
| [Повторная отправка приглашения](invites/resend_invite.md) | GET `invites/{invite_id}/send` | Да | Да | Нет |
| [Продление приглашения](invites/prolong_invite.md) | POST `invites/{invite_id}/prolong` | Да | Да | Нет |
| [Удаление приглашения](invites/delete_invite.md) | DELETE `invites/{invite_id}` | Да | Нет | Да |

### Продуктовые лимиты

Лимиты расхода по карте или группе карт: объём в литрах или сумма в рублях за сутки, неделю, месяц и другие периоды.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список продуктовых лимитов](limits/get_limits.md) | GET `limit` | Нет | Нет | Да |
| [Установка продуктового лимита](limits/set_limit.md) | POST `setLimit` | Да | Да | Да |
| [Удаление продуктового лимита](limits/remove_limit.md) | POST `removeLimit` | Да | Да | Да |

### Региональные ограничения

Где можно пользоваться картой: разрешающие и запрещающие ограничения по стране, региону и конкретной АЗС.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список региональных ограничений](region_limits/get_region_limits.md) | GET `regionLimit` | Нет | Да | Да |
| [Установка регионального ограничения](region_limits/set_region_limit.md) | POST `setRegionLimit` | Да | Да | Да |
| [Удаление регионального ограничения](region_limits/remove_region_limit.md) | POST `removeRegionLimit` | Да | Да | Да |

### Отчёты

Заказ отчётов по договору и картам, список заказанных отчётов и скачивание готовых файлов.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Доступные отчёты](reports/get_reports.md) | GET `reports` | Нет | Нет | Да |
| [Заказ отчёта](reports/order_report.md) | POST `reports` | Да | Да | Да |
| [Заказанные отчёты](reports/get_report_jobs.md) | GET `reports/jobs` | Нет | Нет | Да |
| [Скачивание файла отчёта](reports/download_report_file.md) | GET `reports/jobs/{job_id}` | Нет | Да | Нет |
| [Заказ транзакционного отчёта (API v1)](reports/order_report_v1.md) | GET `reports` | Да | Да | Нет |
| [Заказанные отчёты (API v1)](reports/get_report_job_list_v1.md) | GET `getReportJobList` | Нет | Нет | Да |
| [Скачивание файла отчёта (API v1)](reports/download_report_file_v1.md) | GET `getReportFile` | Нет | Да | Нет |

### Товарные ограничители

Какие товары можно или нельзя покупать по карте: разрешающие и запрещающие ограничители по типам и группам продуктов.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список товарных ограничителей](restrictions/get_restrictions.md) | GET `restriction` | Нет | Да | Да |
| [Установка товарного ограничителя](restrictions/set_restriction.md) | POST `setRestriction` | Да | Да | Нет |
| [Удаление товарного ограничителя](restrictions/remove_restriction.md) | POST `removeRestriction` | Да | Да | Да |

### Шаблоны виртуальных карт

Шаблон задаёт тип виртуальной карты и её лимиты, товарные и географические ограничения. Карты, выпущенные по шаблону, получают эти настройки.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список шаблонов](templates/get_templates.md) | GET `vc/templates` | Нет | Нет | Да |
| [Создание шаблона](templates/create_template.md) | POST `vc/templates` | Да | Да | Да |
| [Изменение шаблона](templates/update_template.md) | POST `vc/templates/{template_id}` | Да | — | Да |
| [Удаление шаблона](templates/delete_template.md) | DELETE `vc/templates/{template_id}` | Да | Да | Да |
| [Лимиты шаблона](templates/get_template_limits.md) | GET `vc/templates/{template_id}/limits` | Нет | Нет | Да |
| [Добавление лимита в шаблон](templates/create_template_limit.md) | POST `vc/templates/{template_id}/limits` | Да | Да | Да |
| [Изменение лимита шаблона](templates/update_template_limit.md) | POST `vc/templates/{template_id}/limits/{limit_id}` | Да | — | Да |
| [Удаление лимита шаблона](templates/delete_template_limit.md) | DELETE `vc/templates/{template_id}/limits/{limit_id}` | Да | Да | Да |
| [Товарные ограничители шаблона](templates/get_template_restrictions.md) | GET `vc/templates/{template_id}/restrictions` | Нет | Нет | Да |
| [Добавление товарного ограничителя в шаблон](templates/create_template_restriction.md) | POST `vc/templates/{template_id}/restrictions` | Да | Да | Да |
| [Изменение товарного ограничителя шаблона](templates/update_template_restriction.md) | POST `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | — | Да |
| [Удаление товарного ограничителя шаблона](templates/delete_template_restriction.md) | DELETE `vc/templates/{template_id}/restrictions/{restriction_id}` | Да | — | Да |
| [Географические ограничения шаблона](templates/get_template_georestrictions.md) | GET `vc/templates/{template_id}/georestrictions` | Нет | Нет | Да |
| [Добавление географического ограничения в шаблон](templates/create_template_georestriction.md) | POST `vc/templates/{template_id}/georestrictions` | Да | Да | Да |
| [Изменение географического ограничения шаблона](templates/update_template_georestriction.md) | POST `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | — | Да |
| [Удаление географического ограничения шаблона](templates/delete_template_georestriction.md) | DELETE `vc/templates/{template_id}/georestrictions/{georestriction_id}` | Да | — | Да |

### Транзакции

Операции по картам и договору: покупки на АЗС, возвраты и корректировки за период, детали отдельной транзакции.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Транзакции договора за период](transactions/get_transactions_v2.md) | GET `transactions` | Нет | Да | Да |
| [Транзакции карты за период](transactions/get_card_transactions_v2.md) | GET `cards/{card_id}/transactions` | Нет | Да | Да |
| [Детали транзакции](transactions/get_transaction_detail.md) | GET `transactions/{transaction_id}` | Нет | Нет | Да |
| [Последние транзакции (API v1)](transactions/get_transactions_v1.md) | GET `transactions` | Нет | Да | Нет |

### Пользователи

Водители и другие пользователи клиента: список, создание, привязка к картам и договорам, удаление.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Список пользователей](users/get_users.md) | GET `users` | Нет | Нет | Да |
| [Создание пользователя](users/create_user.md) | POST `users` | Да | Да | Да |
| [Привязка карты к пользователю](users/attach_card.md) | POST `users/{user_id}/attachCard` | Да | Да | Да |
| [Отвязка карты от пользователя](users/detach_card.md) | POST `users/{user_id}/detachCard` | Да | Да | Да |
| [Привязка договоров к пользователю](users/attach_contracts.md) | POST `users/{user_id}/attachContracts` | Да | Да | Да |
| [Отвязка договоров от пользователя](users/detach_contracts.md) | POST `users/{user_id}/detachContracts` | Да | Да | Да |
| [Удаление пользователя](users/delete_user.md) | DELETE `users/{user_id}` | Да | Да | Да |

### Виртуальные карты и оплата по QR

Выпуск виртуальных карт, мобильный профиль карты (МПК) на устройстве водителя и платёжная строка для оплаты по QR-коду.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Выпуск виртуальной карты](virtual_cards/create_virtual_card.md) | POST `cards` | Да | Да | Нет |
| [Выпуск виртуальной карты по типу или шаблону](virtual_cards/release_virtual_card.md) | POST `cards/release` | Да | Да | Нет |
| [Список мобильных профилей карт](virtual_cards/get_mpc_qr_list.md) | GET `MPC` | Нет | Нет | Нет |
| [Выпуск мобильного профиля карты](virtual_cards/init_mpc.md) | POST `cards/{card_id}/initMPC` | Да | Нет | Нет |
| [Подтверждение мобильного профиля карты](virtual_cards/confirm_mpc.md) | POST `cards/{card_id}/confirmMPC` | Да | Нет | Нет |
| [Платёжная строка для оплаты по QR](virtual_cards/generate_payment_qr.md) | POST `cards/{card_id}/pay` | Да | Нет | Нет |
| [Смена PIN или перевыпуск ключей МПК](virtual_cards/update_mpc.md) | POST `cards/{card_id}/updateMPC` | Да | Нет | Нет |
| [Сброс счётчика мобильного профиля](virtual_cards/reset_mpc.md) | POST `cards/{card_id}/resetMPC` | Да | Нет | Нет |
| [Удаление мобильного профиля карты](virtual_cards/delete_mpc.md) | POST `cards/{card_id}/deleteMPC` | Да | Нет | Нет |

